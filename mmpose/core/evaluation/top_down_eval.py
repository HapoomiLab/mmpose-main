import cv2
import numpy as np

from mmpose.core.post_processing import transform_preds


def _calc_distances(preds, targets, mask, normalize):
    """Calculate the normalized distances between preds and target.

    Note:
        batch_size: N
        num_keypoints: K

    Args:
        preds (np.ndarray[N, K, 2]): Predicted keypoint location.
        targets (np.ndarray[N, K, 2]): Groundtruth keypoint location.
        normalize (np.ndarray[N, 2]): Typical value is heatmap_size/10

    Returns:
        np.ndarray[K, N]: The normalized distances.
          If target keypoints are missing, the distance is -1.
    """
    N, K, _ = preds.shape
    distances = np.full((K, N), -1, dtype=np.float32)
    distances[mask.T] = np.linalg.norm(
        ((preds - targets) / normalize[:, None, :])[mask], axis=-1)
    return distances


def _distance_acc(distances, thr=0.5):
    """Return the percentage below the distance threshold, while ignoring
    distances values with -1.

    Note:
        batch_size: N
    Args:
        distances (np.ndarray[N, ]): The normalized distances.
        thr (float): Threshold of the distances.

    Returns:
        float: Percentage of distances below the threshold.
          If all target keypoints are missing, return -1.
    """
    distance_valid = distances != -1
    num_distance_valid = distance_valid.sum()
    if num_distance_valid > 0:
        return (distances[distance_valid] < thr).sum() / num_distance_valid
    return -1


def _get_max_preds(heatmaps):
    """Get keypoint predictions from score maps.

    Note:
        batch_size: N
        num_keypoints: K
        heatmap height: H
        heatmap width: W

    Args:
        heatmaps (np.ndarray[N, K, H, W]): model predicted heatmaps.

    Returns:
        tuple: A tuple containing aggregated results.

        - preds (np.ndarray[N, K, 2]): Predicted keypoint location.
        - maxvals (np.ndarray[N, K, 1]): Scores (confidence) of the keypoints.
    """
    assert isinstance(heatmaps,
                      np.ndarray), ('heatmaps should be numpy.ndarray')
    assert heatmaps.ndim == 4, 'batch_images should be 4-ndim'

    N, K, _, W = heatmaps.shape
    heatmaps_reshaped = heatmaps.reshape((N, K, -1))
    idx = np.argmax(heatmaps_reshaped, 2).reshape((N, K, 1))
    maxvals = np.amax(heatmaps_reshaped, 2).reshape((N, K, 1))

    preds = np.tile(idx, (1, 1, 2)).astype(np.float32)
    preds[:, :, 0] = preds[:, :, 0] % W
    preds[:, :, 1] = preds[:, :, 1] // W

    preds = np.where(np.tile(maxvals, (1, 1, 2)) > 0.0, preds, -1)
    return preds, maxvals


def pose_pck_accuracy(output, target, mask, thr=0.5, normalize=None):
    """Calculate the pose accuracy of PCK for each individual keypoint and the
    averaged accuracy across all keypoints from heatmaps.

    Note:
        The PCK performance metric is the percentage of joints with
        predicted locations that are no further than a normalized
        distance of the ground truth. Here we use [w,h]/10.

        batch_size: N
        num_keypoints: K
        heatmap height: H
        heatmap width: W

    Args:
        output (np.ndarray[N, K, H, W]): Model output heatmaps.
        target (np.ndarray[N, K, H, W]): Groundtruth heatmaps.
        mask (np.ndarray[N, K]): Visibility of the target. False for invisible
            joints, and True for visible. Invisible joints will be ignored for
            accuracy calculation.
        thr (float): Threshold of PCK calculation.
        normalize (np.ndarray[N, 2]): Normalization factor for H&W.

    Returns:
        tuple: A tuple containing keypoint accuracy.

        - np.ndarray[K]: Accuracy of each keypoint.
        - float: Averaged accuracy across all keypoints.
        - int: Number of valid keypoints.
    """
    N, K, H, W = output.shape
    if K == 0:
        return None, 0, 0
    if normalize is None:
        normalize = np.tile(np.array([[H, W]]) / 10, (N, 1))

    pred, _ = _get_max_preds(output)
    gt, _ = _get_max_preds(target)
    return keypoint_pck_accuracy(pred, gt, mask, thr, normalize)


def keypoint_pck_accuracy(pred, gt, mask, thr, normalize):
    """Calculate the pose accuracy of PCK for each individual keypoint and the
    averaged accuracy across all keypoints for coordinates.

    Note:
        batch_size: N
        num_keypoints: K

    Args:
        pred (np.ndarray[N, K, 2]): Predicted keypoint location.
        gt (np.ndarray[N, K, 2]): Groundtruth keypoint location.
        mask (np.ndarray[N, K]): Visibility of the target. False for invisible
            joints, and True for visible. Invisible joints will be ignored for
            accuracy calculation.
        thr (float): Threshold of PCK calculation.
        normalize (np.ndarray[N, 2]): Normalization factor.

    Returns:
        tuple: A tuple containing keypoint accuracy.

        - acc (np.ndarray[K]): Accuracy of each keypoint.
        - avg_acc (float): Averaged accuracy across all keypoints.
        - cnt (int): Number of valid keypoints.
    """
    distances = _calc_distances(pred, gt, mask, normalize)

    acc = np.array([_distance_acc(d, thr) for d in distances])
    valid_acc = acc[acc >= 0]
    cnt = len(valid_acc)
    avg_acc = valid_acc.mean() if cnt > 0 else 0
    return acc, avg_acc, cnt


def keypoint_auc(pred, gt, mask, normalize, num_step=20):
    """Calculate the pose accuracy of PCK for each individual keypoint and the
    averaged accuracy across all keypoints for coordinates.

    Note:
        batch_size: N
        num_keypoints: K

    Args:
        pred (np.ndarray[N, K, 2]): Predicted keypoint location.
        gt (np.ndarray[N, K, 2]): Groundtruth keypoint location.
        mask (np.ndarray[N, K]): Visibility of the target. False for invisible
            joints, and True for visible. Invisible joints will be ignored for
            accuracy calculation.
        normalize (float): Normalization factor.

    Returns:
        float: Area under curve.
    """
    nor = np.tile(np.array([[normalize, normalize]]), (pred.shape[0], 1))
    x = [1.0 * i / num_step for i in range(num_step)]
    y = []
    for thr in x:
        _, avg_acc, _ = keypoint_pck_accuracy(pred, gt, mask, thr, nor)
        y.append(avg_acc)

    auc = 0
    for i in range(num_step):
        auc += 1.0 / num_step * y[i]
    return auc


def keypoint_epe(pred, gt, mask):
    """Calculate the end-point error.

    Note:
        batch_size: N
        num_keypoints: K

    Args:
        pred (np.ndarray[N, K, 2]): Predicted keypoint location.
        gt (np.ndarray[N, K, 2]): Groundtruth keypoint location.
        mask (np.ndarray[N, K]): Visibility of the target. False for invisible
            joints, and True for visible. Invisible joints will be ignored for
            accuracy calculation.

    Returns:
        float: Average end-point error.
    """
    distances = _calc_distances(
        pred, gt, mask, np.tile(np.array([[1, 1]]), (pred.shape[0], 1)))
    distance_valid = distances[distances != -1]
    valid_num = len(distance_valid)
    return distance_valid.sum() / valid_num


def _taylor(heatmap, coord):
    """Distribution aware coordinate decoding method.

    Note:
        heatmap height: H
        heatmap width: W

    Args:
        heatmap (np.ndarray[H, W]): Heatmap of a particular joint type.
        coord (np.ndarray[2,]): Coordinates of the predicted keypoints.

    Returns:
        np.ndarray[2,]: Updated coordinates.
    """
    H, W = heatmap.shape[:2]
    px, py = int(coord[0]), int(coord[1])
    if 1 < px < W - 2 and 1 < py < H - 2:
        dx = 0.5 * (heatmap[py][px + 1] - heatmap[py][px - 1])
        dy = 0.5 * (heatmap[py + 1][px] - heatmap[py - 1][px])
        dxx = 0.25 * (
            heatmap[py][px + 2] - 2 * heatmap[py][px] + heatmap[py][px - 2])
        dxy = 0.25 * (
            heatmap[py + 1][px + 1] - heatmap[py - 1][px + 1] -
            heatmap[py + 1][px - 1] + heatmap[py - 1][px - 1])
        dyy = 0.25 * (
            heatmap[py + 2 * 1][px] - 2 * heatmap[py][px] +
            heatmap[py - 2 * 1][px])
        derivative = np.array([[dx], [dy]])
        hessian = np.array([[dxx, dxy], [dxy, dyy]])
        if dxx * dyy - dxy**2 != 0:
            hessianinv = np.linalg.inv(hessian)
            offset = -hessianinv @ derivative
            offset = np.squeeze(np.array(offset.T), axis=0)
            coord += offset
    return coord


def post_dark(coords, batch_heatmaps):
    """DARK post-pocessing.

    Note:
        batch_size: N
        num_keypoints: K

    Args:
        coords (np.ndarray[N, K, 2]): Coords in shape of batchsize*num_kps*2.
        batch_heatmaps (np.ndarray[N, K, H, W]): batch_heatmaps

    Returns:
        res (np.ndarray): Refined coords in shape of batchsize*num_kps*2.
    """
    if not isinstance(batch_heatmaps, np.ndarray):
        batch_heatmaps = batch_heatmaps.cpu().numpy()
    shape_pad = list(batch_heatmaps.shape)
    shape_pad[2] = shape_pad[2] + 2
    shape_pad[3] = shape_pad[3] + 2
    coord_shape = list(coords.shape)
    for i in range(shape_pad[0]):
        for j in range(shape_pad[1]):
            mapij = batch_heatmaps[0, j, :, :]
            mapij = cv2.GaussianBlur(mapij, (3, 3), 0)
            batch_heatmaps[0, j, :, :] = mapij
    batch_heatmaps = np.clip(batch_heatmaps, 0.001, 50)
    batch_heatmaps = np.log(batch_heatmaps)
    batch_heatmaps_pad = np.zeros(shape_pad, dtype=float)
    batch_heatmaps_pad[:, :, 1:-1, 1:-1] = batch_heatmaps
    batch_heatmaps_pad[:, :, 1:-1, -1] = batch_heatmaps[:, :, :, -1]
    batch_heatmaps_pad[:, :, -1, 1:-1] = batch_heatmaps[:, :, -1, :]
    batch_heatmaps_pad[:, :, 1:-1, 0] = batch_heatmaps[:, :, :, 0]
    batch_heatmaps_pad[:, :, 0, 1:-1] = batch_heatmaps[:, :, 0, :]
    batch_heatmaps_pad[:, :, -1, -1] = batch_heatmaps[:, :, -1, -1]
    batch_heatmaps_pad[:, :, 0, 0] = batch_heatmaps[:, :, 0, 0]
    batch_heatmaps_pad[:, :, 0, -1] = batch_heatmaps[:, :, 0, -1]
    batch_heatmaps_pad[:, :, -1, 0] = batch_heatmaps[:, :, -1, 0]
    i_ = np.zeros((coord_shape[0], coord_shape[1]))
    ix1 = np.zeros((coord_shape[0], coord_shape[1]))
    iy1 = np.zeros((coord_shape[0], coord_shape[1]))
    ix1y1 = np.zeros((coord_shape[0], coord_shape[1]))
    ix1_y1_ = np.zeros((coord_shape[0], coord_shape[1]))
    ix1_ = np.zeros((coord_shape[0], coord_shape[1]))
    iy1_ = np.zeros((coord_shape[0], coord_shape[1]))
    coords = coords.astype(np.int32)
    for i in range(coord_shape[0]):
        for j in range(coord_shape[1]):
            i_[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1] + 1,
                                          coords[i, j, 0] + 1]
            ix1[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1] + 1,
                                           coords[i, j, 0] + 2]
            ix1_[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1] + 1,
                                            coords[i, j, 0]]
            iy1[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1] + 2,
                                           coords[i, j, 0] + 1]
            iy1_[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1],
                                            coords[i, j, 0] + 1]
            ix1y1[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1] + 2,
                                             coords[i, j, 0] + 2]
            ix1_y1_[i, j] = batch_heatmaps_pad[0, j, coords[i, j, 1],
                                               coords[i, j, 0]]
    dx = 0.5 * (ix1 - ix1_)
    dy = 0.5 * (iy1 - iy1_)
    derivative = np.zeros((coord_shape[0], coord_shape[1], 2))
    derivative[:, :, 0] = dx
    derivative[:, :, 1] = dy
    derivative.reshape((coord_shape[0], coord_shape[1], 2, 1))
    dxx = ix1 - 2 * i_ + ix1_
    dyy = iy1 - 2 * i_ + iy1_
    dxy = 0.5 * (ix1y1 - ix1 - iy1 + i_ + i_ - ix1_ - iy1_ + ix1_y1_)
    hessian = np.zeros((coord_shape[0], coord_shape[1], 2, 2))
    hessian[:, :, 0, 0] = dxx
    hessian[:, :, 1, 0] = dxy
    hessian[:, :, 0, 1] = dxy
    hessian[:, :, 1, 1] = dyy
    inv_hessian = np.zeros(hessian.shape)
    for i in range(coord_shape[0]):
        for j in range(coord_shape[1]):
            hessian_tmp = hessian[i, j, :, :] + 1e-8 * np.eye(2)
            inv_hessian[i, j, :, :] = np.linalg.inv(hessian_tmp)
    coords = coords.astype(np.float)
    for i in range(coord_shape[0]):
        for j in range(coord_shape[1]):
            derivative_tmp = derivative[i, j, :][:, np.newaxis]
            shift = np.matmul(inv_hessian[i, j, :, :], derivative_tmp)
            coords[i, j, :] = coords[i, j, :] - shift.reshape((-1))
    return coords


def _gaussian_blur(heatmaps, kernel=11):
    """Modulate heatmap distribution with Gaussian.
     sigma = 0.3*((kernel_size-1)*0.5-1)+0.8
     sigma~=3 if k=17
     sigma=2 if k=11;
     sigma~=1.5 if k=7;
     sigma~=1 if k=3;

    Note:
        batch_size: N
        num_keypoints: K
        heatmap height: H
        heatmap width: W

    Args:
        heatmaps (np.ndarray[N, K, H, W]): model predicted heatmaps.
        kernel (int): Gaussian kernel size (K) for modulation, which should
            match the heatmap gaussian sigma when training.
            K=17 for sigma=3 and k=11 for sigma=2.

    Returns:
        np.ndarray[N, K, H, W]: Modulated heatmap distribution.
    """
    assert kernel % 2 == 1

    border = (kernel - 1) // 2
    batch_size = heatmaps.shape[0]
    num_joints = heatmaps.shape[1]
    height = heatmaps.shape[2]
    width = heatmaps.shape[3]
    for i in range(batch_size):
        for j in range(num_joints):
            origin_max = np.max(heatmaps[i, j])
            dr = np.zeros((height + 2 * border, width + 2 * border),
                          dtype=np.float32)
            dr[border:-border, border:-border] = heatmaps[i, j].copy()
            dr = cv2.GaussianBlur(dr, (kernel, kernel), 0)
            heatmaps[i, j] = dr[border:-border, border:-border].copy()
            heatmaps[i, j] *= origin_max / np.max(heatmaps[i, j])
    return heatmaps


def keypoints_from_heatmaps(heatmaps,
                            center,
                            scale,
                            post_process=True,
                            unbiased=False,
                            kernel=11,
                            kpd=3.5,
                            use_udp=False,
                            target_type='GaussianHeatMap'):
    """Get final keypoint predictions from heatmaps and transform them back to
    the image.

    Note:
        batch_size: N
        num_keypoints: K
        heatmap height: H
        heatmap width: W

    Args:
        heatmaps (np.ndarray[N, K, H, W]): model predicted heatmaps.
        center (np.ndarray[N, 2]): Center of the bounding box (x, y).
        scale (np.ndarray[N, 2]): Scale of the bounding box
            wrt height/width.
        post_process (bool): Option to use post processing or not.
        unbiased (bool): Option to use unbiased decoding.
            Paper ref: Zhang et al. Distribution-Aware Coordinate
            Representation for Human Pose Estimation (CVPR 2020).
        kernel (int): Gaussian kernel size (K) for modulation, which should
            match the heatmap gaussian sigma when training.
            K=17 for sigma=3 and k=11 for sigma=2.
        kpd (float): Keypoint pose distance for UDP.
        use_udp (bool): Use unbiased data processing.
        target_type (str): 'GaussianHeatMap' or 'CombinedTarget'.
            CombinedTarget: The combination of classification target
            (response map) and regression target (offset map).
            Paper ref: Huang et al. The Devil is in the Details: Delving into
            Unbiased Data Processing for Human Pose Estimation (CVPR 2020).


    Returns:
        tuple: A tuple containing keypoint predictions and scores.

        - preds (np.ndarray[N, K, 2]): Predicted keypoint location in images.
        - maxvals (np.ndarray[N, K, 1]): Scores (confidence) of the keypoints.
    """

    N, K, H, W = heatmaps.shape
    if use_udp:
        if target_type == 'GaussianHeatMap':
            coords, maxvals = _get_max_preds(heatmaps)
            if post_process:
                coords = post_dark(coords, heatmaps)
        elif target_type == 'CombinedTarget':
            net_output = heatmaps.copy()
            kps_pos_distance_x = kpd / 64 * H
            kps_pos_distance_y = kpd / 64 * H
            heatmaps = net_output[:, ::3, :]
            offset_x = net_output[:, 1::3, :] * kps_pos_distance_x
            offset_y = net_output[:, 2::3, :] * kps_pos_distance_y
            for i in range(heatmaps.shape[0]):
                for j in range(heatmaps.shape[1]):
                    heatmaps[i, j, :, :] = cv2.GaussianBlur(
                        heatmaps[i, j, :, :], (2 * kernel + 1, 2 * kernel + 1),
                        0)
                    offset_x[i, j, :, :] = cv2.GaussianBlur(
                        offset_x[i, j, :, :], (kernel, kernel), 0)
                    offset_y[i, j, :, :] = cv2.GaussianBlur(
                        offset_y[i, j, :, :], (kernel, kernel), 0)

            coords, maxvals = _get_max_preds(heatmaps)
            for n in range(coords.shape[0]):
                for p in range(coords.shape[1]):
                    px = int(coords[n][p][0])
                    py = int(coords[n][p][1])
                    coords[n][p][0] += offset_x[n, p, py, px]
                    coords[n][p][1] += offset_y[n, p, py, px]
        else:
            assert False
        preds = coords.copy()
    else:
        preds, maxvals = _get_max_preds(heatmaps)
        if post_process:
            if unbiased:  # alleviate biased coordinate
                assert kernel > 0
                # apply Gaussian distribution modulation.
                heatmaps = _gaussian_blur(heatmaps, kernel)
                heatmaps = np.maximum(heatmaps, 1e-10)
                heatmaps = np.log(heatmaps)
                for n in range(N):
                    for k in range(K):
                        preds[n][k] = _taylor(heatmaps[n][k], preds[n][k])
            else:
                # add +/-0.25 shift to the predicted locations for higher acc.
                for n in range(N):
                    for k in range(K):
                        heatmap = heatmaps[n][k]
                        px = int(preds[n][k][0])
                        py = int(preds[n][k][1])
                        if 1 < px < W - 1 and 1 < py < H - 1:
                            diff = np.array([
                                heatmap[py][px + 1] - heatmap[py][px - 1],
                                heatmap[py + 1][px] - heatmap[py - 1][px]
                            ])
                            preds[n][k] += np.sign(diff) * .25

    # Transform back to the image
    for i in range(N):
        preds[i] = transform_preds(
            preds[i], center[i], scale[i], [W, H], use_udp=use_udp)

    return preds, maxvals
