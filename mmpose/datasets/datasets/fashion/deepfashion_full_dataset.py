import os
from collections import OrderedDict

import numpy as np

from mmpose.datasets.builder import DATASETS
from .fashion_base_dataset import FashionBaseDataset


@DATASETS.register_module()
class DeepFashionFullDataset(FashionBaseDataset):
    """DeepFashion dataset (full-body clothes) for fashion landmark detection.

    `DeepFashion: Powering Robust Clothes Recognition
    and Retrieval with Rich Annotations' CVPR'2016 and
    `Fashion Landmark Detection in the Wild' ECCV'2016

    The dataset loads raw features and apply specified transforms
    to return a dict containing the image tensors and other information.

    Fashion landmark indexes for full-body clothes::

        0: 'left collar',
        1: 'right collar',
        2: 'left sleeve',
        3: 'right sleeve',
        4: 'left waistline',
        5: 'right waistline',
        6: 'left hem',
        7: 'right hem'

    Args:
        ann_file (str): Path to the annotation file.
        img_prefix (str): Path to a directory where images are held.
            Default: None.
        data_cfg (dict): config
        pipeline (list[dict | callable]): A sequence of data transforms.
        test_mode (bool): Store True when building test or
            validation dataset. Default: False.
    """

    def __init__(self,
                 ann_file,
                 img_prefix,
                 data_cfg,
                 pipeline,
                 test_mode=False):

        super().__init__(
            ann_file, img_prefix, data_cfg, pipeline, test_mode=test_mode)

        assert self.ann_info['num_joints'] == 8
        self.ann_info['flip_pairs'] = [[0, 1], [2, 3], [4, 5], [6, 7]]

        self.ann_info['use_different_joint_weights'] = False
        self.ann_info['joint_weights'] = \
            np.ones((self.ann_info['num_joints'], 1), dtype=np.float32)

        self.dataset_name = 'deepfashion_upper'
        self.db = self._get_db()

        print(f'=> num_images: {self.num_images}')
        print(f'=> load {len(self.db)} samples')

    def _get_db(self):
        """Load dataset."""
        gt_db = []
        for img_id in self.img_ids:
            num_joints = self.ann_info['num_joints']

            ann_ids = self.coco.getAnnIds(imgIds=img_id, iscrowd=False)
            objs = self.coco.loadAnns(ann_ids)

            rec = []
            for obj in objs:
                if max(obj['keypoints']) == 0:
                    continue
                joints_3d = np.zeros((num_joints, 3), dtype=np.float32)
                joints_3d_visible = np.zeros((num_joints, 3), dtype=np.float32)

                keypoints = np.array(obj['keypoints']).reshape(-1, 3)
                joints_3d[:, :2] = keypoints[:, :2]
                joints_3d_visible[:, :2] = np.minimum(1, keypoints[:, 2:3])

                # the ori image is 224x224
                center, scale = self._xywh2cs(0, 0, 224, 224, 0.8)

                image_file = os.path.join(self.img_prefix,
                                          self.id2name[img_id])
                rec.append({
                    'image_file': image_file,
                    'center': center,
                    'scale': scale,
                    'rotation': 0,
                    'joints_3d': joints_3d,
                    'joints_3d_visible': joints_3d_visible,
                    'dataset': self.dataset_name,
                    'bbox': obj['bbox'],
                    'bbox_score': 1
                })
            gt_db.extend(rec)
        return gt_db

    def evaluate(self, outputs, res_folder, metric='PCK', **kwargs):
        """Evaluate freihand keypoint results. The pose prediction results will
        be saved in `${res_folder}/result_keypoints.json`.

        Note:
            batch_size: N
            num_keypoints: K
            heatmap height: H
            heatmap width: W

        Args:
            outputs (list(preds, boxes, image_path, output_heatmap))
                :preds (np.ndarray[1,K,3]): The first two dimensions are
                    coordinates, score is the third dimension of the array.
                :boxes (np.ndarray[1,6]): [center[0], center[1], scale[0]
                    , scale[1],area, score]
                :image_path (list[str]): For example, [ 't', 'r', 'a', 'i',
                    'n', 'i', 'n', 'g', '/', 'r', 'g', 'b', '/', '0', '0',
                    '0', '3', '1', '4', '2', '6', '.', 'j', 'p', 'g']
                :output_heatmap (np.ndarray[N, K, H, W]): model outpus.

            res_folder (str): Path of directory to save the results.
            metric (str | list[str]): Metric to be performed.
                Options: 'PCK', 'AUC', 'EPE'.

        Returns:
            dict: Evaluation results for evaluation metric.
        """
        metrics = metric if isinstance(metric, list) else [metric]
        allowed_metrics = ['PCK', 'AUC', 'EPE']
        for metric in metrics:
            if metric not in allowed_metrics:
                raise KeyError(f'metric {metric} is not supported')

        res_file = os.path.join(res_folder, 'result_keypoints.json')

        kpts = []

        for preds, boxes, image_path, _ in outputs:
            str_image_path = ''.join(image_path)
            image_id = self.name2id[str_image_path[len(self.img_prefix):]]

            kpts.append({
                'keypoints': preds[0].tolist(),
                'center': boxes[0][0:2].tolist(),
                'scale': boxes[0][2:4].tolist(),
                'area': float(boxes[0][4]),
                'score': float(boxes[0][5]),
                'image_id': image_id,
            })

        self._write_keypoint_results(kpts, res_file)
        info_str = self._report_metric(res_file, metrics)
        name_value = OrderedDict(info_str)

        return name_value
