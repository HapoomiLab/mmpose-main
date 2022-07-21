# Copyright (c) OpenMMLab. All rights reserved.
from abc import ABCMeta, abstractmethod
from typing import Tuple, Union

import torch
import torch.nn.functional as F
from mmengine.data import InstanceData, PixelData
from mmengine.model import BaseModule
from torch import Tensor

from mmpose.core.utils.tensor_utils import _to_numpy
from mmpose.core.utils.typing import ConfigType, OptSampleList, SampleList


class BaseHead(BaseModule, metaclass=ABCMeta):
    """Base head. A subclass should override :meth:`predict` and :meth:`loss`.

    Args:
        init_cfg (dict, optional): The extra init config of layers.
            Defaults to None.
    """

    @abstractmethod
    def forward(self, feats: Tuple[Tensor]):
        """Forward the network."""

    @abstractmethod
    def predict(self, feats: Tuple[Tensor], batch_data_samples: OptSampleList,
                test_cfg: ConfigType) -> SampleList:
        """Predict results from features."""

    @abstractmethod
    def loss(self, feats: Tuple[Tensor], batch_data_samples: OptSampleList,
             train_cfg: ConfigType) -> dict:
        """Calculate losses from a batch of inputs and data samples."""

    def _get_in_channels(self):
        """Get the input channel number of the network according to the feature
        channel numbers and the input transform type."""

        feat_channels = self.in_channels
        if isinstance(feat_channels, int):
            feat_channels = [feat_channels]

        if self.input_transform == 'resize_concat':
            if isinstance(self.input_index, int):
                in_channels = feat_channels[self.input_index]
            else:
                in_channels = sum(feat_channels[i] for i in self.input_index)
        elif self.input_transform == 'select':
            if isinstance(self.input_index, int):
                in_channels = feat_channels[self.input_index]
            else:
                in_channels = [feat_channels[i] for i in self.input_index]
        else:
            raise (ValueError,
                   f'Invalid input transform mode "{self.input_transform}"')

        return in_channels

    def _transform_inputs(
            self, feats: Tuple[Tensor]) -> Union[Tensor, Tuple[Tensor]]:
        """Transform multi scale features into the network input."""
        if self.input_transform == 'resize_concat':
            inputs = [feats[i] for i in self.input_index]
            resized_inputs = [
                F.interpolate(
                    x,
                    size=inputs[0].shape[2:],
                    mode='bilinear',
                    align_corners=self.align_corners) for x in inputs
            ]
            inputs = torch.cat(resized_inputs, dim=1)
        elif self.input_transform == 'select':
            if isinstance(self.input_index, int):
                inputs = feats[self.input_index]
            else:
                inputs = tuple(feats[i] for i in self.input_index)
        else:
            raise (ValueError,
                   f'Invalid input transform mode "{self.input_transform}"')

        return inputs

    def decode(self, batch_outputs: Union[Tensor, Tuple[Tensor]],
               batch_data_samples: OptSampleList,
               test_cfg: ConfigType) -> SampleList:
        """Decode keypoints from outputs."""

        if self.decoder is None:
            raise RuntimeError(
                f'The decoder has not been set in {self.__class__.__name__}. '
                'Please set the decoder configs in the init parameters to '
                'enable head methods `head.predict()` and `head.decode()`')

        if batch_data_samples is None:
            raise ValueError(
                '`batch_data_samples` is required to decode keypoitns.')

        if isinstance(batch_outputs, Tensor):
            batch_outputs_np = _to_numpy(batch_outputs)
            batch_heatmaps_np = batch_outputs_np

            head_type = type(self).__name__.lower()
            if 'regression' in head_type:
                out_heatmaps = False
            else:
                out_heatmaps = True

        elif isinstance(batch_outputs, Tuple):
            assert len(batch_outputs) == 2, (
                'batch_outputs should contain coordinates and heatmaps in '
                f'{self.__class__.__name__}')

            batch_coords, batch_heatmaps = batch_outputs
            batch_outputs_np = _to_numpy(batch_coords)
            batch_heatmaps_np = _to_numpy(batch_heatmaps)

            out_heatmaps = True

        # Whether to visualize the predicted heatmps
        vis_heatmaps = test_cfg.get('vis_heatmaps', True) and out_heatmaps

        # TODO: support decoding with tensor data
        for idx, (outputs, data_sample) in enumerate(
                zip(batch_outputs_np, batch_data_samples)):
            keypoints, scores = self.decoder.decode(outputs)

            # Convert the decoded local keypoints (in input space)
            # to the image coordinate space
            # Convert keypoint coordinates from input space to image space
            if 'gt_instances' in data_sample:
                bbox_centers = data_sample.gt_instances.bbox_centers
                bbox_scales = data_sample.get_instances.bbox_scales
                input_size = data_sample.metainfo.input_size
                keypoints = keypoints / input_size * bbox_scales + \
                    bbox_centers - 0.5 * bbox_scales

            else:
                raise ValueError(
                    '`gt_instances` is required to convert keypoints from'
                    ' from the heatmap space to the image space.')

            # Store the keypoint predictions in the data sample
            if 'pred_instances' not in data_sample:
                data_sample.pred_instances = InstanceData()
            data_sample.pred_instances.keypoints = keypoints
            data_sample.pred_instances.keypoint_scores = scores

            # Store the heatmap predictions in the data sample
            if 'pred_fileds' not in data_sample:
                data_sample.pred_fields = PixelData()

            if vis_heatmaps:
                heatmaps = batch_heatmaps_np[idx]
                data_sample.pred_fields.heatmaps = heatmaps

        return batch_data_samples
