# Copyright (c) OpenMMLab. All rights reserved.

from typing import Optional, Sequence, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
from mmengine.data import PixelData
from torch import Tensor, nn

from mmpose.evaluation.functional import keypoint_pck_accuracy
from mmpose.models.utils.tta import flip_coordinates, flip_heatmaps
from mmpose.registry import KEYPOINT_CODECS, MODELS
from mmpose.utils.tensor_utils import to_numpy
from mmpose.utils.typing import (ConfigType, OptConfigType, OptSampleList,
                                 SampleList)
from .. import HeatmapHead
from ..base_head import BaseHead

OptIntSeq = Optional[Sequence[int]]


@MODELS.register_module()
class IntegralRegressionHead(BaseHead):
    """Top-down integral regression head introduced in `IPR`_ by Xiao et
    al(2018). The head contains a differentiable spatial to numerical transform
    (DSNT) layer that do soft-argmax operation on the predicted heatmaps to
    regress the coordinates.

    This head is used for algorithms that only supervise the coordinates. If
    you need to supervise the heatmaps, please refer to `DSNTHead`.

    Args:
        in_channels (int | sequence[int]): Number of input channels
        in_featuremap_size (int | sequence[int]): Size of input feature map
        num_joints (int): Number of joints
        deconv_out_channels (sequence[int]): The output channel number of each
            deconv layer. Defaults to ``(256, 256, 256)``
        deconv_kernel_sizes (sequence[int | tuple], optional): The kernel size
            of each deconv layer. Each element should be either an integer for
            both height and width dimensions, or a tuple of two integers for
            the height and the width dimension respectively.Defaults to
            ``(4, 4, 4)``
        conv_out_channels (sequence[int], optional): The output channel number
            of each intermediate conv layer. ``None`` means no intermediate
            conv layer between deconv layers and the final conv layer.
            Defaults to ``None``
        conv_kernel_sizes (sequence[int | tuple], optional): The kernel size
            of each intermediate conv layer. Defaults to ``None``
        input_transform (str): Transformation of input features which should
            be one of the following options:

                - ``'resize_concat'``: Resize multiple feature maps specified
                    by ``input_index`` to the same size as the first one and
                    concat these feature maps
                - ``'select'``: Select feature map(s) specified by
                    ``input_index``. Multiple selected features will be
                    bundled into a tuple

            Defaults to ``'select'``
        input_index (int | sequence[int]): The feature map index used in the
            input transformation. See also ``input_transform``. Defaults to -1
        align_corners (bool): `align_corners` argument of
            :func:`torch.nn.functional.interpolate` used in the input
            transformation. Defaults to ``False``
        loss (Config): Config for keypoint loss. Defaults to use
            :class:`SmoothL1Loss`
        decoder (Config, optional): The decoder config that controls decoding
            keypoint coordinates from the network output. Defaults to ``None``
        init_cfg (Config, optional): Config to control the initialization. See
            :attr:`default_init_cfg` for default settings

    .. _`IPR`: https://arxiv.org/abs/1711.08229
    """

    _version = 2

    def __init__(self,
                 in_channels: Union[int, Sequence[int]],
                 in_featuremap_size: Tuple[int, int],
                 num_joints: int,
                 deconv_out_channels: OptIntSeq = (256, 256, 256),
                 deconv_kernel_sizes: OptIntSeq = (4, 4, 4),
                 conv_out_channels: OptIntSeq = None,
                 conv_kernel_sizes: OptIntSeq = None,
                 has_final_layer: bool = True,
                 input_transform: str = 'select',
                 input_index: Union[int, Sequence[int]] = 0,
                 align_corners: bool = False,
                 loss: ConfigType = dict(
                     type='SmoothL1Loss', use_target_weight=True),
                 decoder: OptConfigType = None,
                 init_cfg: OptConfigType = None):

        if init_cfg is None:
            init_cfg = self.default_init_cfg

        super().__init__(init_cfg)

        self.in_channels = in_channels
        self.num_joints = num_joints
        self.align_corners = align_corners
        self.input_transform = input_transform
        self.input_index = input_index
        self.loss_module = MODELS.build(loss)
        if decoder is not None:
            self.decoder = KEYPOINT_CODECS.build(decoder)
        else:
            self.decoder = None

        num_deconv = len(deconv_out_channels) if deconv_out_channels else 0
        if num_deconv != 0:

            self.heatmap_size = tuple(
                [s * (2**num_deconv) for s in in_featuremap_size])

            # deconv layers + 1x1 conv
            self.simplebaseline_head = HeatmapHead(
                in_channels=in_channels,
                out_channels=num_joints,
                deconv_out_channels=deconv_out_channels,
                deconv_kernel_sizes=deconv_kernel_sizes,
                conv_out_channels=conv_out_channels,
                conv_kernel_sizes=conv_kernel_sizes,
                has_final_layer=has_final_layer,
                input_transform=input_transform,
                input_index=input_index,
                align_corners=align_corners)

            if has_final_layer:
                in_channels = num_joints
            else:
                in_channels = deconv_out_channels[-1]

        else:
            self.simplebaseline_head = None
            in_channels = self._get_in_channels()

            if self.input_transform == 'resize_concat':
                if isinstance(in_featuremap_size, tuple):
                    self.heatmap_size = in_featuremap_size
                elif isinstance(in_featuremap_size, list):
                    self.heatmap_size = in_featuremap_size[0]
            elif self.input_transform == 'select':
                if isinstance(in_featuremap_size, tuple):
                    self.heatmap_size = in_featuremap_size
                elif isinstance(in_featuremap_size, list):
                    self.heatmap_size = in_featuremap_size[input_index]

        if isinstance(in_channels, list):
            raise ValueError(
                f'{self.__class__.__name__} does not support selecting '
                'multiple input features.')

        W, H = self.heatmap_size
        self.linspace_x = torch.arange(0.0, 1.0 * H, 1).reshape(H, 1).repeat(
            [1, W]) / H
        self.linspace_y = torch.arange(0.0, 1.0 * W, 1).reshape(1, W).repeat(
            [H, 1]) / W

        self.linspace_x = nn.Parameter(self.linspace_x, requires_grad=False)
        self.linspace_y = nn.Parameter(self.linspace_y, requires_grad=False)

    def _linear_expectation(self, heatmaps: Tensor,
                            linspace: Tensor) -> Tensor:
        """Calculate linear expectation."""

        N, C, _, _ = heatmaps.shape
        heatmaps = heatmaps.mul(linspace).reshape(N, C, -1)
        expectation = torch.sum(heatmaps, dim=2, keepdim=True)

        return expectation

    def _flat_softmax(self, featmaps: Tensor) -> Tensor:
        """Use Softmax to normalize the featmaps in depthwise."""

        _, C, H, W = featmaps.shape

        featmaps = featmaps.reshape(-1, C, H * W)
        heatmaps = F.softmax(featmaps, dim=2)

        return heatmaps.reshape(-1, C, H, W)

    def forward(self, feats: Tuple[Tensor]) -> Union[Tensor, Tuple[Tensor]]:
        """Forward the network. The input is multi scale feature maps and the
        output is the coordinates.

        Args:
            feats (Tuple[Tensor]): Multi scale feature maps.

        Returns:
            Tensor: output coordinates(and sigmas[optional]).
        """
        if self.simplebaseline_head is None:
            feats = self._transform_inputs(feats)
        else:
            feats = self.simplebaseline_head(feats)

        heatmaps = self._flat_softmax(feats)

        pred_x = self._linear_expectation(heatmaps, self.linspace_x)
        pred_y = self._linear_expectation(heatmaps, self.linspace_y)
        coords = torch.cat([pred_x, pred_y], dim=-1)
        return coords, heatmaps

    def predict(self,
                feats: Tuple[Tensor],
                batch_data_samples: OptSampleList,
                test_cfg: ConfigType = {}) -> SampleList:
        """Predict results from outputs."""

        if test_cfg.get('flip_test', False):
            # TTA: flip test -> feats = [orig, flipped]
            assert isinstance(feats, list) and len(feats == 2)
            flip_indices = batch_data_samples[0].metainfo['flip_indices']
            _feats, _feats_flip = feats

            _batch_coords, _batch_heatmaps = self.forward(_feats)

            _batch_coords_flip, _batch_heatmaps_flip = self.forward(
                _feats_flip)
            _batch_coords_flip = flip_coordinates(
                _batch_coords_flip, flip_indices=flip_indices)
            _batch_heatmaps_flip = flip_heatmaps(
                _batch_heatmaps_flip,
                flip_mode='heatmap',
                flip_indices=flip_indices,
                shift_heatmap=False)

            batch_coords = (_batch_coords + _batch_coords_flip) * 0.5
            batch_heatmaps = (_batch_heatmaps + _batch_heatmaps_flip) * 0.5
        else:
            batch_coords, batch_heatmaps = self.forward(feats)  # (B, K, D)

        batch_coords.unsqueeze_(dim=1)  # (B, N, K, D)
        preds = self.decode(batch_coords, batch_data_samples)

        # Whether to visualize the predicted heatmaps
        if test_cfg.get('output_heatmaps', False):
            for heatmaps, data_sample in zip(batch_heatmaps, preds):
                # Store the heatmap predictions in the data sample
                if 'pred_fields' not in data_sample:
                    data_sample.pred_fields = PixelData()
                data_sample.pred_fields.heatmaps = heatmaps

        return preds

    def loss(self,
             inputs: Tuple[Tensor],
             batch_data_samples: OptSampleList,
             train_cfg: ConfigType = {}) -> dict:
        """Calculate losses from a batch of inputs and data samples."""

        pred_coords, _ = self.forward(inputs)
        keypoint_labels = torch.cat(
            [d.gt_instance_labels.keypoint_labels for d in batch_data_samples])
        keypoint_weights = torch.cat([
            d.gt_instance_labels.keypoint_weights for d in batch_data_samples
        ])

        # calculate losses
        losses = dict()

        # TODO: multi-loss calculation
        loss = self.loss_module(pred_coords, keypoint_labels,
                                keypoint_weights.unsqueeze(-1))

        if isinstance(loss, dict):
            losses.update(loss)
        else:
            losses.update(loss_kpt=loss)

        # calculate accuracy
        _, avg_acc, _ = keypoint_pck_accuracy(
            pred=to_numpy(pred_coords),
            gt=to_numpy(keypoint_labels),
            mask=to_numpy(keypoint_weights) > 0,
            thr=0.05,
            norm_factor=np.ones((pred_coords.size(0), 2), dtype=np.float32))

        losses.update(acc_pose=float(avg_acc))

        return losses

    @property
    def default_init_cfg(self):
        init_cfg = [dict(type='Normal', layer=['Linear'], std=0.01, bias=0)]
        return init_cfg
