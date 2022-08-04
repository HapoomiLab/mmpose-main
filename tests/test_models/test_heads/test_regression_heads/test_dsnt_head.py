# Copyright (c) OpenMMLab. All rights reserved.
import unittest
from typing import List, Tuple
from unittest import TestCase

import torch

from mmpose.models.heads import DSNTHead
from mmpose.structures import PoseDataSample
from mmpose.testing import get_packed_inputs


class TestDSNTHead(TestCase):

    def _get_feats(
        self,
        batch_size: int = 2,
        feat_shapes: List[Tuple[int, int, int]] = [(32, 6, 8)],
    ):

        feats = [
            torch.rand((batch_size, ) + shape, dtype=torch.float32)
            for shape in feat_shapes
        ]

        return feats

    def _get_data_samples(self,
                          batch_size: int = 2,
                          with_reg_label: bool = False):
        batch_data_samples = [
            inputs['data_sample'] for inputs in get_packed_inputs(
                batch_size, with_reg_label=with_reg_label)
        ]

        return batch_data_samples

    def test_init(self):
        # square heatmap
        head = DSNTHead(
            in_channels=32, in_featuremap_size=(8, 8), num_joints=17)
        self.assertEqual(head.linspace_x.shape, (64, 64))
        self.assertEqual(head.linspace_y.shape, (64, 64))
        self.assertIsNone(head.decoder)

        # rectangle heatmap
        head = DSNTHead(
            in_channels=32, in_featuremap_size=(6, 8), num_joints=17)
        self.assertEqual(head.linspace_x.shape, (8 * 8, 6 * 8))
        self.assertEqual(head.linspace_y.shape, (8 * 8, 6 * 8))
        self.assertIsNone(head.decoder)

        # 2 deconv + 1x1 conv
        head = DSNTHead(
            in_channels=32,
            in_featuremap_size=(6, 8),
            num_joints=17,
            deconv_out_channels=(32, 32),
            deconv_kernel_sizes=(4, 4),
            conv_out_channels=(32, ),
            conv_kernel_sizes=(1, ),
        )
        self.assertEqual(head.linspace_x.shape, (8 * 4, 6 * 4))
        self.assertEqual(head.linspace_y.shape, (8 * 4, 6 * 4))
        self.assertIsNone(head.decoder)

        # 2 deconv + w/o 1x1 conv
        head = DSNTHead(
            in_channels=32,
            in_featuremap_size=(6, 8),
            num_joints=17,
            deconv_out_channels=(32, 32),
            deconv_kernel_sizes=(4, 4),
            conv_out_channels=(32, ),
            conv_kernel_sizes=(1, ),
            has_final_layer=False,
        )
        self.assertEqual(head.linspace_x.shape, (8 * 4, 6 * 4))
        self.assertEqual(head.linspace_y.shape, (8 * 4, 6 * 4))
        self.assertIsNone(head.decoder)

        # w/o deconv and 1x1 conv
        head = DSNTHead(
            in_channels=32,
            in_featuremap_size=(6, 8),
            num_joints=17,
            deconv_out_channels=tuple(),
            deconv_kernel_sizes=tuple(),
            has_final_layer=False,
        )
        self.assertEqual(head.linspace_x.shape, (8, 6))
        self.assertEqual(head.linspace_y.shape, (8, 6))
        self.assertIsNone(head.decoder)

        # w/o deconv and 1x1 conv
        head = DSNTHead(
            in_channels=32,
            in_featuremap_size=(6, 8),
            num_joints=17,
            deconv_out_channels=None,
            deconv_kernel_sizes=None,
            has_final_layer=False,
        )
        self.assertEqual(head.linspace_x.shape, (8, 6))
        self.assertEqual(head.linspace_y.shape, (8, 6))
        self.assertIsNone(head.decoder)

        # w/ decoder
        head = DSNTHead(
            in_channels=1024,
            in_featuremap_size=(6, 8),
            num_joints=17,
            decoder=dict(type='RegressionLabel', input_size=(192, 256)),
        )
        self.assertIsNotNone(head.decoder)

    def test_predict(self):
        decoder_cfg = dict(type='RegressionLabel', input_size=(192, 256))

        # inputs transform: select
        head = DSNTHead(
            in_channels=[16, 32],
            in_featuremap_size=(6, 8),
            num_joints=17,
            input_transform='select',
            input_index=-1,
            decoder=decoder_cfg,
        )

        feats = self._get_feats(
            batch_size=2, feat_shapes=[(16, 16, 12), (32, 8, 6)])
        batch_data_samples = self._get_data_samples(
            batch_size=2, with_reg_label=False)
        preds = head.predict(feats, batch_data_samples)

        self.assertEqual(len(preds), 2)
        self.assertIsInstance(preds[0], PoseDataSample)
        self.assertIn('pred_instances', preds[0])
        self.assertEqual(
            preds[0].pred_instances.keypoints.shape,
            preds[0].gt_instances.keypoints.shape,
        )

        # inputs transform: resize and concat
        head = DSNTHead(
            in_channels=[16, 32],
            in_featuremap_size=(12, 16),
            num_joints=17,
            input_transform='resize_concat',
            input_index=[0, 1],
            decoder=decoder_cfg,
        )
        feats = self._get_feats(
            batch_size=2, feat_shapes=[(16, 16, 12), (32, 8, 6)])
        batch_data_samples = self._get_data_samples(batch_size=2)
        preds = head.predict(feats, batch_data_samples)

        self.assertEqual(len(preds), 2)
        self.assertIsInstance(preds[0], PoseDataSample)
        self.assertIn('pred_instances', preds[0])
        self.assertEqual(
            preds[0].pred_instances.keypoints.shape,
            preds[0].gt_instances.keypoints.shape,
        )
        self.assertNotIn('pred_heatmaps', preds[0])

        # input transform: output heatmap
        head = DSNTHead(
            in_channels=[16, 32],
            in_featuremap_size=(6, 8),
            num_joints=17,
            input_transform='select',
            input_index=-1,
            decoder=decoder_cfg,
        )

        feats = self._get_feats(
            batch_size=2, feat_shapes=[(16, 16, 12), (32, 8, 6)])
        batch_data_samples = self._get_data_samples(
            batch_size=2, with_reg_label=False)
        preds = head.predict(
            feats, batch_data_samples, test_cfg=dict(output_heatmaps=True))

        self.assertIn('pred_heatmaps', preds[0])
        self.assertEqual(preds[0].pred_heatmaps.heatmaps.shape,
                         (17, 8 * 8, 6 * 8))

    def test_loss(self):
        for dist_loss in ['l1', 'l2']:
            for div_reg in ['kl', 'js']:
                head = DSNTHead(
                    in_channels=[16, 32],
                    in_featuremap_size=(6, 8),
                    num_joints=17,
                    input_transform='select',
                    input_index=-1,
                    loss=dict(
                        type='DSNTLoss',
                        use_target_weight=True,
                        dist_loss=dist_loss,
                        div_reg=div_reg))

                feats = self._get_feats(
                    batch_size=2, feat_shapes=[(16, 16, 12), (32, 8, 6)])
                batch_data_samples = self._get_data_samples(
                    batch_size=2, with_reg_label=True)
                losses = head.loss(feats, batch_data_samples)

                self.assertIsInstance(losses['loss_kpt'], torch.Tensor)
                self.assertEqual(losses['loss_kpt'].shape, torch.Size())
                self.assertIsInstance(losses['acc_pose'], float)

    def test_errors(self):

        with self.assertRaisesRegex(ValueError,
                                    'selecting multiple input features'):
            _ = DSNTHead(
                in_channels=[16, 32],
                in_featuremap_size=(6, 8),
                num_joints=17,
                input_transform='select',
                input_index=[0, 1],
            )


if __name__ == '__main__':
    unittest.main()
