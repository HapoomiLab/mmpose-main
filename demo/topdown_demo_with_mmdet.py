# Copyright (c) OpenMMLab. All rights reserved.
import mimetypes
import os
import tempfile
from argparse import ArgumentParser

import json_tricks as json
import mmcv
import mmengine
import numpy as np
from mmengine.registry import init_default_scope

from mmpose.apis import inference_topdown
from mmpose.apis import init_model as init_pose_estimator
from mmpose.evaluation.functional import nms
from mmpose.registry import VISUALIZERS
from mmpose.structures import merge_data_samples, split_instances

try:
    from mmdet.apis import inference_detector, init_detector
    has_mmdet = True
except (ImportError, ModuleNotFoundError):
    has_mmdet = False


def process_one_image(args, img_path, detector, pose_estimator, visualizer,
                      show_interval):
    """Visualize predicted keypoints (and heatmaps) of one image."""

    # predict bbox
    init_default_scope(detector.cfg.get('default_scope', 'mmdet'))
    det_result = inference_detector(detector, img_path)
    pred_instance = det_result.pred_instances.cpu().numpy()
    bboxes = np.concatenate(
        (pred_instance.bboxes, pred_instance.scores[:, None]), axis=1)
    bboxes = bboxes[np.logical_and(pred_instance.labels == args.det_cat_id,
                                   pred_instance.scores > args.bbox_thr)]
    bboxes = bboxes[nms(bboxes, args.nms_thr), :4]

    # predict keypoints
    pose_results = inference_topdown(pose_estimator, img_path, bboxes)
    data_samples = merge_data_samples(pose_results)

    # show the results
    img = mmcv.imread(img_path, channel_order='rgb')

    out_file = None
    if args.output_root:
        out_file = f'{args.output_root}/{os.path.basename(img_path)}'

    visualizer.add_datasample(
        'result',
        img,
        data_sample=data_samples,
        draw_gt=False,
        draw_heatmap=args.draw_heatmap,
        draw_bbox=args.draw_bbox,
        show=args.show,
        wait_time=show_interval,
        out_file=out_file,
        kpt_score_thr=args.kpt_thr)

    return data_samples.pred_instances


def main():
    """Visualize the demo images.

    Using mmdet to detect the human.
    """
    parser = ArgumentParser()
    parser.add_argument('det_config', help='Config file for detection')
    parser.add_argument('det_checkpoint', help='Checkpoint file for detection')
    parser.add_argument('pose_config', help='Config file for pose')
    parser.add_argument('pose_checkpoint', help='Checkpoint file for pose')
    parser.add_argument(
        '--input', type=str, default='', help='Image/Video file')
    parser.add_argument(
        '--show',
        action='store_true',
        default=False,
        help='whether to show img')
    parser.add_argument(
        '--output-root',
        type=str,
        default='',
        help='root of the output img file. '
        'Default not saving the visualization images.')
    parser.add_argument(
        '--save-predictions',
        action='store_true',
        default=False,
        help='whether to save predicted results')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--det-cat-id',
        type=int,
        default=0,
        help='Category id for bounding box detection model')
    parser.add_argument(
        '--bbox-thr',
        type=float,
        default=0.3,
        help='Bounding box score threshold')
    parser.add_argument(
        '--nms-thr',
        type=float,
        default=0.3,
        help='IoU threshold for bounding box NMS')
    parser.add_argument(
        '--kpt-thr', type=float, default=0.3, help='Keypoint score threshold')
    parser.add_argument(
        '--draw-heatmap',
        action='store_true',
        default=False,
        help='Draw heatmap predicted by the model')
    parser.add_argument(
        '--radius',
        type=int,
        default=3,
        help='Keypoint radius for visualization')
    parser.add_argument(
        '--thickness',
        type=int,
        default=1,
        help='Link thickness for visualization')
    parser.add_argument(
        '--draw-bbox', action='store_true', help='Draw bboxes of instances')

    assert has_mmdet, 'Please install mmdet to run the demo.'

    args = parser.parse_args()

    assert args.show or (args.output_root != '')
    assert args.input != ''
    assert args.det_config is not None
    assert args.det_checkpoint is not None
    if args.output_root:
        mmengine.mkdir_or_exist(args.output_root)
    if args.save_predictions:
        assert args.output_root != ''
        args.pred_save_path = f'{args.output_root}/results_' \
            f'{os.path.splitext(os.path.basename(args.input))[0]}.json'

    # build detector
    detector = init_detector(
        args.det_config, args.det_checkpoint, device=args.device)

    # build pose estimator
    pose_estimator = init_pose_estimator(
        args.pose_config,
        args.pose_checkpoint,
        device=args.device,
        cfg_options=dict(
            model=dict(test_cfg=dict(output_heatmaps=args.draw_heatmap))))

    # init visualizer
    pose_estimator.cfg.visualizer.radius = args.radius
    pose_estimator.cfg.visualizer.line_width = args.thickness
    visualizer = VISUALIZERS.build(pose_estimator.cfg.visualizer)
    # the dataset_meta is loaded from the checkpoint and
    # then pass to the model in init_pose_estimator
    visualizer.set_dataset_meta(pose_estimator.dataset_meta)

    input_type = mimetypes.guess_type(args.input)[0].split('/')[0]
    if input_type == 'image':
        pred_instances = process_one_image(
            args,
            args.input,
            detector,
            pose_estimator,
            visualizer,
            show_interval=0)
        pred_instances_list = split_instances(pred_instances)

    elif input_type == 'video':
        tmp_folder = tempfile.TemporaryDirectory()
        video = mmcv.VideoReader(args.input)
        progressbar = mmengine.ProgressBar(len(video))
        video.cvt2frames(tmp_folder.name, show_progress=False)
        output_root = args.output_root
        args.output_root = tmp_folder.name
        pred_instances_list = []

        for frame_id, img_fname in enumerate(os.listdir(tmp_folder.name)):
            pred_instances = process_one_image(
                args,
                f'{tmp_folder.name}/{img_fname}',
                detector,
                pose_estimator,
                visualizer,
                show_interval=1)
            progressbar.update()
            pred_instances_list.append(
                dict(
                    frame_id=frame_id,
                    instances=split_instances(pred_instances)))

        if output_root:
            mmcv.frames2video(
                tmp_folder.name,
                f'{output_root}/{os.path.basename(args.input)}',
                fps=video.fps,
                fourcc='mp4v',
                show_progress=False)
        tmp_folder.cleanup()

    else:
        args.save_predictions = False
        raise ValueError(
            f'file {os.path.basename(args.input)} has invalid format.')

    if args.save_predictions:
        with open(args.pred_save_path, 'w') as f:
            json.dump(
                dict(
                    meta_info=pose_estimator.dataset_meta,
                    instance_info=pred_instances_list),
                f,
                indent='\t')
        print(f'predictions have been saved at {args.pred_save_path}')


if __name__ == '__main__':
    main()
