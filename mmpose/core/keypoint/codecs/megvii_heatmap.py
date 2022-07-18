# Copyright (c) OpenMMLab. All rights reserved.
from typing import Optional, Tuple

import cv2
import numpy as np

from mmpose.registry import KEYPOINT_CODECS
from ..transforms import keypoints_bbox2img
from .base import BaseKeypointCodec
from .utils import gaussian_blur, get_heatmap_maximum


@KEYPOINT_CODECS.register_module()
class MegviiHeatmap(BaseKeypointCodec):
    """Represent keypoints as heatmaps via "Megvii" approach. See `MSPN`_
    (2019) and `CPN`_ (2018) for details.

    Note:

        - instance number: N
        - keypoint number: K
        - keypoint dimension: C
        - image size: [w, h]
        - heatmap size: [W, H]

    Args:
        input_size (tuple): Image size in [w, h]
        heatmap_size (tuple): Heatmap size in [W, H]
        kernel_size (tuple): The kernel size of the heatmap gaussian in
            [ks_x, ks_y]

    .. _`MSPN`: https://arxiv.org/abs/1901.00148
    .. _`CPN`: https://arxiv.org/abs/1711.07319
    """

    def __init__(
        self,
        input_size: Tuple[int, int],
        heatmap_size: Tuple[int, int],
        kernel_size: int,
    ) -> None:

        super().__init__()
        self.input_size = input_size
        self.heatmap_size = heatmap_size
        self.kernel_size = kernel_size

    def encode(
        self,
        keypoints: np.ndarray,
        keypoints_visible: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Encode keypoints into heatmaps.
        Args:
            keypoints (np.ndarray): Keypoint coordinates in shape (N, K, C)
            keypoints_visible (np.ndarray): Keypoint visibilities in shape
                (N, K)

        Returns:
            tuple:
            - heatmaps (np.ndarray): The generated heatmap in shape
                (K, H, W) where [W, H] is the `heatmap_size`
            - keypoint_weights (np.ndarray): The target weights in shape
                (K,)
        """

        N, K, _ = keypoints.shape
        W, H = self.heatmap_size

        assert N == 1, (
            f'{self.__class__.__name__} only support single-instance '
            'keypoint encoding')

        input_size = np.array(self.input_size)
        feat_stride = input_size / [W, H]

        heatmaps = np.zeros((K, H, W), dtype=np.float32)
        keypoint_weights = np.ones(K, dtype=np.float32)

        for k in range(K):
            # skip unlabled keypoints
            if keypoints_visible[0, k] < 0.5:
                keypoint_weights[k] = 0
                continue

            # get center coordinates
            kx, ky = (keypoints[0, k] / feat_stride).astype(np.int64)
            if kx < 0 or kx >= W or ky < 0 or ky >= H:
                keypoint_weights[k] = 0
                continue

            heatmaps[k, ky, kx] = 1.
            heatmaps[k] = cv2.GaussianBlur(heatmaps[k], self.kernel_size, 0)

            # normalize the heatmap
            heatmaps[k] = heatmaps[k] / heatmaps[k, ky, kx] * 255.

        return heatmaps, keypoint_weights

    def decode(self, encoded: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Get keypoint coordinates from heatmaps.

        Args:
            encoded (np.ndarray): Heatmaps in shape (K, H, W)

        Returns:
            tuple:
            - keypoints (np.ndarray): Decoded keypoint coordinates in shape
                (K, C)
            - scores (np.ndarray): The keypoint scores in shape (K,). It
                usually represents the confidence of the keypoint prediction.
        """
        heatmaps = gaussian_blur(encoded.copy(), self.kernel_size)
        K, H, W = heatmaps.shape

        keypoints, scores = get_heatmap_maximum(heatmaps)

        for k in range(K):
            heatmap = heatmaps[k]
            px = int(keypoints[k, 0])
            py = int(keypoints[k, 1])
            if 1 < px < W - 1 and 1 < py < H - 1:
                diff = np.array([
                    heatmap[py][px + 1] - heatmap[py][px - 1],
                    heatmap[py + 1][px] - heatmap[py - 1][px]
                ])
                keypoints[k] += (np.sign(diff) * 0.25 + 0.5)

        scores = scores / 255.0 + 0.5

        # Unsqueeze the instance dimension for single-instance results
        keypoints = keypoints[None]
        scores = keypoints[None]

        return keypoints, scores

    def keypoints_bbox2img(self, keypoints: np.ndarray,
                           bbox_centers: np.ndarray,
                           bbox_scales: np.ndarray) -> np.ndarray:
        """Convert decoded keypoints from the bbox space to the image space.
        Topdown codecs should override this method.

        Args:
            keypoints (np.ndarray): Keypoint coordinates in shape (N, K, C).
                The coordinate is in the bbox space
            bbox_centers (np.ndarray): Bbox centers in shape (N, 2).
                See `pipelines.GetBboxCenterScale` for details
            bbox_scale (np.ndarray): Bbox scales in shape (N, 2).
                See `pipelines.GetBboxCenterScale` for details

        Returns:
            np.ndarray: The transformed keypoints in shape (N, K, C).
            The coordinate is in the image space.
        """

        keypoints = keypoints_bbox2img(
            keypoints,
            bbox_centers,
            bbox_scales,
            heatmap_size=self.heatmap_size,
            use_udp=False)
