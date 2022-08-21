# Copyright (c) OpenMMLab. All rights reserved.
from typing import List, Tuple
from unittest import TestCase

import torch
from torch import nn

from mmpose.models.heads import CPMHead
from mmpose.structures import PoseDataSample
from mmpose.testing import get_packed_inputs


class TestCPMHead(TestCase):

    def _get_feats(self,
                   batch_size: int = 2,
                   feat_shapes: List[Tuple[int, int, int]] = [(17, 32, 24)]):

        feats = [
            torch.rand((batch_size, ) + shape, dtype=torch.float32)
            for shape in feat_shapes
        ]
        return feats

    def _get_data_samples(self, batch_size: int = 2):
        batch_data_samples = [
            inputs['data_sample'] for inputs in get_packed_inputs(
                batch_size=batch_size,
                num_instances=1,
                num_keypoints=17,
                img_shape=(128, 128),
                input_size=(192, 256),
                heatmap_size=(24, 32),
                with_heatmap=True,
                with_reg_label=False)
        ]
        return batch_data_samples

    def test_init(self):
        # w/o deconv
        head = CPMHead(
            num_stages=1,
            in_channels=256,
            out_channels=17,
            deconv_out_channels=None)
        self.assertTrue(isinstance(head.multi_deconv_layers, nn.ModuleList))
        self.assertTrue(isinstance(head.multi_deconv_layers[0], nn.Identity))

        # w/ deconv
        head = CPMHead(
            num_stages=1,
            in_channels=32,
            out_channels=17,
            deconv_out_channels=(32, 32),
            deconv_kernel_sizes=(4, 4))
        self.assertTrue(isinstance(head.multi_deconv_layers, nn.ModuleList))
        self.assertTrue(isinstance(head.multi_deconv_layers[0], nn.Sequential))

        # w/o final layer
        head = CPMHead(
            num_stages=6,
            in_channels=17,
            out_channels=17,
            has_final_layer=False)
        self.assertTrue(isinstance(head.multi_final_layers, nn.ModuleList))
        self.assertTrue(isinstance(head.multi_final_layers[0], nn.Identity))

        # w/ decoder
        head = CPMHead(
            num_stages=1,
            in_channels=32,
            out_channels=17,
            decoder=dict(
                type='MSRAHeatmap',
                input_size=(192, 256),
                heatmap_size=(48, 64),
                sigma=2.))
        self.assertIsNotNone(head.decoder)

        # the same loss for different stages
        head = CPMHead(
            num_stages=6,
            in_channels=17,
            out_channels=17,
            has_final_layer=False,
            loss=dict(type='KeypointMSELoss', use_target_weight=True),
        )
        self.assertTrue(isinstance(head.loss_module, nn.Module))

        # different loss for different stages
        num_stages = 6
        head = CPMHead(
            num_stages=num_stages,
            in_channels=17,
            out_channels=17,
            has_final_layer=False,
            loss=[dict(type='KeypointMSELoss', use_target_weight=True)] * 6,
        )
        self.assertTrue(isinstance(head.loss_module, nn.ModuleList))
        self.assertTrue(len(head.loss_module), num_stages)

    def test_predict(self):
        decoder_cfg = dict(
            type='MSRAHeatmap',
            input_size=(192, 256),
            heatmap_size=(24, 32),
            sigma=2.)

        # num_stages = 6, has_final_layer = False
        head = CPMHead(
            num_stages=6,
            in_channels=17,
            out_channels=17,
            has_final_layer=False,
            decoder=decoder_cfg)

        with self.assertRaisesRegex(
                AssertionError,
                'length of feature maps did not match the `num_stages`'):
            feats = self._get_feats(batch_size=2, feat_shapes=[(17, 32, 24)])
            batch_data_samples = self._get_data_samples(batch_size=2)
            _ = head.predict(feats, batch_data_samples)

        feats = self._get_feats(batch_size=2, feat_shapes=[(17, 32, 24)] * 6)
        batch_data_samples = self._get_data_samples(batch_size=2)
        preds = head.predict(feats, batch_data_samples)

        self.assertEqual(len(preds), 2)
        self.assertIsInstance(preds[0], PoseDataSample)
        self.assertIn('pred_instances', preds[0])
        self.assertEqual(preds[0].pred_instances.keypoints.shape,
                         preds[0].gt_instances.keypoints.shape)
        # output_heatmaps = False
        self.assertNotIn('pred_fields', preds[0])

        # num_stages = 1, has_final_layer = True
        head = CPMHead(
            num_stages=1,
            in_channels=32,
            out_channels=17,
            has_final_layer=True,
            decoder=decoder_cfg)
        feats = self._get_feats(batch_size=2, feat_shapes=[(32, 32, 24)])
        batch_data_samples = self._get_data_samples(batch_size=2)
        preds = head.predict(
            feats, batch_data_samples, test_cfg=dict(output_heatmaps=True))

        self.assertEqual(len(preds), 2)
        self.assertIsInstance(preds[0], PoseDataSample)
        self.assertIn('pred_instances', preds[0])
        self.assertEqual(preds[0].pred_instances.keypoints.shape,
                         preds[0].gt_instances.keypoints.shape)
        self.assertIn('pred_fields', preds[0])
        self.assertEqual(preds[0].pred_fields.heatmaps.shape, (17, 32, 24))

    def test_tta(self):
        # flip test: heatmap
        decoder_cfg = dict(
            type='MSRAHeatmap',
            input_size=(192, 256),
            heatmap_size=(24, 32),
            sigma=2.)

        head = CPMHead(
            num_stages=1,
            in_channels=32,
            out_channels=17,
            has_final_layer=True,
            decoder=decoder_cfg)

        feats = self._get_feats(batch_size=2, feat_shapes=[(32, 8, 6)])
        batch_data_samples = self._get_data_samples(batch_size=2)
        preds = head.predict([feats, feats],
                             batch_data_samples,
                             test_cfg=dict(
                                 flip_test=True,
                                 flip_mode='heatmap',
                                 shift_heatmap=True,
                             ))

        self.assertEqual(len(preds), 2)
        self.assertIsInstance(preds[0], PoseDataSample)
        self.assertIn('pred_instances', preds[0])
        self.assertEqual(preds[0].pred_instances.keypoints.shape,
                         preds[0].gt_instances.keypoints.shape)

    def test_loss(self):
        # num_stages = 1
        head = CPMHead(
            num_stages=1,
            in_channels=32,
            out_channels=17,
            has_final_layer=True)

        feats = self._get_feats(batch_size=2, feat_shapes=[(32, 32, 24)])
        batch_data_samples = self._get_data_samples(batch_size=2)
        losses = head.loss(feats, batch_data_samples)

        self.assertIsInstance(losses['loss_kpt'], torch.Tensor)
        self.assertEqual(losses['loss_kpt'].shape, torch.Size(()))
        self.assertIsInstance(losses['acc_pose'], torch.Tensor)

        num_stages = 6
        head = CPMHead(
            num_stages=num_stages,
            in_channels=17,
            out_channels=17,
            has_final_layer=False,
            loss=[dict(type='KeypointMSELoss', use_target_weight=True)] *
            num_stages)

        with self.assertRaisesRegex(
                AssertionError,
                'length of feature maps did not match the `num_stages`'):
            feats = self._get_feats(batch_size=2, feat_shapes=[(17, 32, 24)])
            batch_data_samples = self._get_data_samples(batch_size=2)
            _ = head.loss(feats, batch_data_samples)

        feats = self._get_feats(
            batch_size=2, feat_shapes=[(17, 32, 24)] * num_stages)
        batch_data_samples = self._get_data_samples(batch_size=2)
        losses = head.loss(feats, batch_data_samples)

        self.assertIsInstance(losses['loss_kpt'], torch.Tensor)
        self.assertEqual(losses['loss_kpt'].shape, torch.Size(()))
        self.assertIsInstance(losses['acc_pose'], torch.Tensor)

    def test_errors(self):
        # Invalid arguments
        with self.assertRaisesRegex(ValueError, 'Got unmatched values'):
            _ = CPMHead(
                num_stages=1,
                in_channels=17,
                out_channels=17,
                deconv_out_channels=(256, ),
                deconv_kernel_sizes=(4, 4))

        with self.assertRaisesRegex(ValueError, 'Unsupported kernel size'):
            _ = CPMHead(
                num_stages=1,
                in_channels=17,
                out_channels=17,
                deconv_out_channels=(256, ),
                deconv_kernel_sizes=(1, ))

        with self.assertRaisesRegex(ValueError, 'did not match `num_stages`'):
            _ = CPMHead(
                num_stages=6,
                in_channels=17,
                out_channels=17,
                loss=[dict(type='KeypointMSELoss', use_target_weight=True)] *
                4)
