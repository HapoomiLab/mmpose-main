# Copyright (c) OpenMMLab. All rights reserved.
from unittest import TestCase

import numpy as np

from mmpose.core.keypoint.codecs import MSRAHeatmap  # noqa: F401
from mmpose.registry import KEYPOINT_CODECS


class TestMSRAHeatmap(TestCase):

    # name and configs of all test cases
    def setUp(self) -> None:
        self.configs = [
            (
                'msra',
                dict(
                    type='MSRAHeatmap',
                    input_size=(192, 256),
                    heatmap_size=(48, 64),
                    sigma=2.0),
            ),
            (
                'msra+dark',
                dict(
                    type='MSRAHeatmap',
                    input_size=(192, 256),
                    heatmap_size=(48, 64),
                    sigma=2.0,
                    unbiased=True),
            ),
        ]

        keypoints = np.round(np.random.rand(1, 17, 2) *
                             [192, 256]).astype(np.float32)
        keypoints_visible = np.ones((1, 17), dtype=np.float32)
        heatmaps = np.random.rand(17, 64, 48).astype(np.float32)
        self.data = dict(
            keypoints=keypoints,
            keypoints_visible=keypoints_visible,
            heatmaps=heatmaps)

    def test_encode(self):
        keypoints = self.data['keypoints']
        keypoints_visible = self.data['keypoints_visible']

        for name, cfg in self.configs:
            codec = KEYPOINT_CODECS.build(cfg)

            heatmaps, keypoint_weights = codec.encode(keypoints,
                                                      keypoints_visible)

            self.assertEqual(heatmaps.shape, (17, 64, 48),
                             f'Failed case: "{name}"')
            self.assertEqual(keypoint_weights.shape,
                             (17, )), f'Failed case: "{name}"'

    def test_decode(self):
        heatmaps = self.data['heatmaps']

        for name, cfg in self.configs:
            codec = KEYPOINT_CODECS.build(cfg)

            keypoints, scores = codec.decode(heatmaps)

            self.assertEqual(keypoints.shape, (1, 17, 2),
                             f'Failed case: "{name}"')
            self.assertEqual(scores.shape, (1, 17), f'Failed case: "{name}"')

    def test_cicular_verification(self):
        keypoints = self.data['keypoints']
        keypoints_visible = self.data['keypoints_visible']

        for name, cfg in self.configs:
            codec = KEYPOINT_CODECS.build(cfg)

            heatmaps, _ = codec.encode(keypoints, keypoints_visible)
            _keypoints, _ = codec.decode(heatmaps)

            self.assertTrue(
                np.allclose(keypoints, _keypoints, atol=5.),
                f'Failed case: "{name}"')
