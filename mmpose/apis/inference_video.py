# Copyright (c) OpenMMLab. All rights reserved.
import copy
import os

import numpy as np
import torch
from mmcv.parallel import collate, scatter
from PIL import Image

from mmpose.apis.inference import _box2cs, _xywh2xyxy, _xyxy2xywh
from mmpose.datasets.dataset_info import DatasetInfo
from mmpose.datasets.pipelines import Compose
from mmpose.utils.hooks import OutputHook

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


def inference_top_down_video_pose_model(model,
                                        frames_or_paths,
                                        person_results=None,
                                        bbox_thr=None,
                                        format='xywh',
                                        dataset_info=None,
                                        return_heatmap=False,
                                        outputs=None):
    """Inference a single frame with a list of person bounding boxes and
    several support frames.

    Note:
        - num_frames: F
        - num_people: P
        - num_keypoints: K
        - bbox height: H
        - bbox width: W

    Args:
        model (nn.Module): The loaded pose model.
        frames_or_paths (str| np.ndarray): Frame filenames or loaded frames.
        person_results (list(dict), optional): a list of detected persons that
            contains ``bbox`` and/or ``track_id``:

            - ``bbox`` (4, ) or (5, ): The person bounding box, which contains
                4 box coordinates (and score).
            - ``track_id`` (int): The unique id for each human instance. If
                not provided, a dummy person result with a bbox covering
                the entire image will be used. Default: None.
        bbox_thr (float | None): Threshold for bounding boxes. Only bboxes
            with higher scores will be fed into the pose detector.
            If bbox_thr is None, all boxes will be used.
        format (str): bbox format ('xyxy' | 'xywh'). Default: 'xywh'.

            - `xyxy` means (left, top, right, bottom),
            - `xywh` means (left, top, width, height).
        dataset_info (DatasetInfo): A class containing all dataset info.
        return_heatmap (bool) : Flag to return heatmap, default: False
        outputs (list(str) | tuple(str)) : Names of layers whose outputs
            need to be returned. Default: None.

    Returns:
        tuple:
        - pose_results (list[dict]): The bbox & pose info. \
            Each item in the list is a dictionary, \
            containing the bbox: (left, top, right, bottom, [score]) \
            and the pose (ndarray[Kx3]): x, y, score.
        - returned_outputs (list[dict[np.ndarray[N, K, H, W] | \
            torch.Tensor[N, K, H, W]]]): \
            Output feature maps from layers specified in `outputs`. \
            Includes 'heatmap' if `return_heatmap` is True.
    """
    # only two kinds of bbox format is supported
    assert format in ['xyxy', 'xywh']
    assert isinstance(frames_or_paths, (list, tuple))

    # get dataset info
    dataset_info = DatasetInfo(model.cfg.dataset_info)

    pose_results = []
    returned_outputs = []

    if person_results is None:
        # create dummy person results
        if isinstance(frames_or_paths[0], str):
            width, height = Image.open(frames_or_paths[0]).size
        else:
            height, width = frames_or_paths[0].shape[:2]
        person_results = [{'bbox': np.array([0, 0, width, height])}]

    if len(person_results) == 0:
        return pose_results, returned_outputs

    # Change for-loop preprocess each bbox to preprocess all bboxes at once.
    bboxes = np.array([box['bbox'] for box in person_results])

    # Select bboxes by score threshold
    if bbox_thr is not None:
        assert bboxes.shape[1] == 5
        valid_idx = np.where(bboxes[:, 4] > bbox_thr)[0]
        bboxes = bboxes[valid_idx]
        person_results = [person_results[i] for i in valid_idx]

    if format == 'xyxy':
        bboxes_xyxy = bboxes
        bboxes_xywh = _xyxy2xywh(bboxes)
    else:
        # format is already 'xywh'
        bboxes_xywh = bboxes
        bboxes_xyxy = _xywh2xyxy(bboxes)

    # if bbox_thr remove all bounding box
    if len(bboxes_xywh) == 0:
        return [], []

    with OutputHook(model, outputs=outputs, as_tensor=False) as h:
        # poses is results['pred'] # N x 17x 3
        poses, heatmap = _inference_single_video_pose_model(
            model,
            frames_or_paths,
            bboxes_xywh,
            dataset_info=dataset_info,
            return_heatmap=return_heatmap)

        if return_heatmap:
            h.layer_outputs['heatmap'] = heatmap

        returned_outputs.append(h.layer_outputs)

    assert len(poses) == len(person_results), print(
        len(poses), len(person_results), len(bboxes_xyxy))
    for pose, person_result, bbox_xyxy in zip(poses, person_results,
                                              bboxes_xyxy):
        pose_result = person_result.copy()
        pose_result['keypoints'] = pose
        pose_result['bbox'] = bbox_xyxy
        pose_results.append(pose_result)

    return pose_results, returned_outputs


def _inference_single_video_pose_model(model,
                                       frames_or_paths,
                                       bboxes,
                                       dataset_info=None,
                                       return_heatmap=False):
    """Inference human bounding boxes of one frame.

    Note:
        - num_bboxes: N
        - num_keypoints: K
        - num_frames: F

    Args:
        model (nn.Module): The loaded pose model.
        frames_or_paths (str | np.ndarray): Frame filenames or loaded frames.
        bboxes (list | np.ndarray): All bounding boxes (with scores),
            shaped (N, 4) or (N, 5). (left, top, width, height, [score])
            where N is number of bounding boxes of the frame to inference.
        dataset_info (DatasetInfo): A class containing all dataset info.
        rreturn_heatmap (bool): Flag to return heatmap, default: False

    Returns:
        ndarray[NxKx3]: Predicted pose x, y, score.
        heatmap[N, K, H, W]: Model output heatmap.
    """

    cfg = model.cfg

    # the input sample is a list of frames
    assert isinstance(frames_or_paths, (list, tuple))
    # the length of input frames must equal to frame weight in the config
    assert len(frames_or_paths) == len(cfg.data_cfg.frame_weight_test)

    device = next(model.parameters()).device
    if device.type == 'cpu':
        device = -1

    # build the data pipeline
    pipeline = copy.deepcopy(cfg.test_pipeline)
    test_pipeline = Compose(pipeline)

    assert len(bboxes[0]) in [4, 5]

    if dataset_info is not None:
        dataset_name = dataset_info.dataset_name
        flip_pairs = dataset_info.flip_pairs

    batch_data = []
    for bbox in bboxes:
        center, scale = _box2cs(cfg, bbox)

        # prepare data
        data = {
            'center':
            center,
            'scale':
            scale,
            'bbox_score':
            bbox[4] if len(bbox) == 5 else 1,
            'bbox_id':
            0,  # need to be assigned if batch_size > 1
            'dataset':
            dataset_name,
            'joints_3d':
            np.zeros((cfg.data_cfg.num_joints, 3), dtype=np.float32),
            'joints_3d_visible':
            np.zeros((cfg.data_cfg.num_joints, 3), dtype=np.float32),
            'rotation':
            0,
            'frame_weight':
            cfg.data_cfg.frame_weight_test,
            'ann_info': {
                'image_size': np.array(cfg.data_cfg['image_size']),
                'num_joints': cfg.data_cfg.num_joints,
                'flip_pairs': flip_pairs
            }
        }

        if isinstance(frames_or_paths[0], np.ndarray):
            data['img'] = frames_or_paths
        else:
            data['image_file'] = frames_or_paths

        data = test_pipeline(data)
        batch_data.append(data)

    batch_data = collate(batch_data, samples_per_gpu=len(batch_data))
    batch_data = scatter(batch_data, [device])[0]

    # forward the model
    with torch.no_grad():
        result = model(
            img=batch_data['img'],
            img_metas=batch_data['img_metas'],
            return_loss=False,
            return_heatmap=return_heatmap)

    return result['preds'], result['output_heatmap']
