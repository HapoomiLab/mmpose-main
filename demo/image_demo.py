# Copyright (c) OpenMMLab. All rights reserved.
from argparse import ArgumentParser

import numpy as np
from mmcv.image import imread

from mmpose.apis import inference_topdown, init_model
from mmpose.registry import VISUALIZERS
from mmpose.utils import register_all_modules


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('img', help='Image file')
    parser.add_argument('config', help='Config file')
    parser.add_argument('checkpoint', help='Checkpoint file')
    parser.add_argument('--out-file', default=None, help='Path to output file')
    parser.add_argument(
        '--device', default='cuda:0', help='Device used for inference')
    parser.add_argument(
        '--draw_heatmap',
        action='store_true',
        help='Visualize the predicted heatmap')
    args = parser.parse_args()
    return args


def main(args):
    # register all modules in mmpose into the registries
    register_all_modules()

    # build the model from a config file and a checkpoint file
    if args.draw_heatmap:
        cfg_options = dict(model=dict(test_cfg=dict(output_heatmap=True)))
    else:
        cfg_options = None

    model = init_model(
        args.config,
        args.checkpoint,
        device=args.device,
        cfg_options=cfg_options)

    # init visualizer
    visualizer = VISUALIZERS.build(model.cfg.visualizer)
    visualizer.set_dataset_meta(model.dataset_meta)

    # inference a single image
    bboxes = np.array([[280.79, 44.73, 218.7, 346.68]], dtype=np.float32)
    results = inference_topdown(
        model, args.img, bboxes=bboxes, bbox_format='xywh')

    # show the results
    img = imread(args.img, channel_order='rgb')
    visualizer.add_datasample(
        'result',
        img,
        data_sample=results[0],
        draw_gt=False,
        draw_bbox=True,
        draw_heatmap=args.draw_heatmap,
        show=True,
        out_file=args.out_file)


if __name__ == '__main__':
    args = parse_args()
    main(args)
