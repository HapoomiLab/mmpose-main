# Copyright (c) OpenMMLab. All rights reserved.
import os
import os.path as osp
import warnings
from collections import OrderedDict, defaultdict

import json_tricks as json
import numpy as np
from mmcv import Config
from poseval import eval_helpers
from poseval.evaluateAP import evaluateAP

from ....core.post_processing import oks_nms, soft_oks_nms
from ...builder import DATASETS
from .topdown_coco_dataset import TopDownCocoDataset


@DATASETS.register_module()
class TopDownPoseTrack18PoseWarperDataset(TopDownCocoDataset):

    def __init__(self,
                 ann_file,
                 img_prefix,
                 data_cfg,
                 pipeline,
                 dataset_info=None,
                 test_mode=False):
        if dataset_info is None:
            warnings.warn(
                'dataset_info is missing. '
                'Check https://github.com/open-mmlab/mmpose/pull/663 '
                'for details.', DeprecationWarning)
            cfg = Config.fromfile('configs/_base_/datasets/posetrack18.py')
            dataset_info = cfg._cfg_dict['dataset_info']

        super(TopDownCocoDataset, self).__init__(
            ann_file,
            img_prefix,
            data_cfg,
            pipeline,
            dataset_info=dataset_info,
            test_mode=test_mode)

        self.timestep_delta = data_cfg['timestep_delta']
        self.timestep_delta_rand = data_cfg['timestep_delta_rand']
        self.timestep_delta_range = data_cfg['timestep_delta_range']

        self.use_gt_bbox = data_cfg['use_gt_bbox']
        self.bbox_file = data_cfg['bbox_file']
        self.det_bbox_thr = data_cfg.get('det_bbox_thr', 0.0)
        self.use_nms = data_cfg.get('use_nms', True)
        self.soft_nms = data_cfg['soft_nms']
        self.nms_thr = data_cfg['nms_thr']
        self.oks_thr = data_cfg['oks_thr']
        self.vis_thr = data_cfg['vis_thr']

        self.ann_info['use_different_joint_weights'] = False
        self.db = self._get_db()

        print(f'=> num_images: {self.num_images}')
        print(f'=> load {len(self.db)} samples')

    def _get_db(self):
        """Load dataset."""
        if (not self.test_mode) or self.use_gt_bbox:
            # use ground truth bbox
            gt_db = self._load_coco_keypoint_annotations()
        else:
            # use bbox from detection
            gt_db = self._load_coco_person_detection_results()
        return gt_db

    def _load_coco_keypoint_annotations(self):
        """Ground truth bbox and keypoints."""
        gt_db = []
        for img_id in self.img_ids:
            gt_db.extend(self._load_coco_keypoint_annotation_kernel(img_id))
        return gt_db

    def _load_coco_keypoint_annotation_kernel(self, img_id):
        """load annotation from COCOAPI.

        Note:
            bbox:[x1, y1, w, h]
        Args:
            img_id: coco image id
        Returns:
            dict: db entry
        """
        img_ann = self.coco.loadImgs(img_id)[0]
        width = img_ann['width']
        height = img_ann['height']
        num_joints = self.ann_info['num_joints']

        file_name = img_ann['file_name']
        nframes = int(img_ann['nframes'])
        frame_id = int(img_ann['frame_id'])

        ann_ids = self.coco.getAnnIds(imgIds=img_id, iscrowd=False)
        objs = self.coco.loadAnns(ann_ids)

        # sanitize bboxes
        valid_objs = []
        for obj in objs:
            if 'bbox' not in obj:
                continue
            x, y, w, h = obj['bbox']
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(width - 1, x1 + max(0, w - 1))
            y2 = min(height - 1, y1 + max(0, h - 1))
            if ('area' not in obj or obj['area'] > 0) and x2 > x1 and y2 > y1:
                obj['clean_bbox'] = [x1, y1, x2 - x1, y2 - y1]
                valid_objs.append(obj)
        objs = valid_objs

        bbox_id = 0
        rec = []
        for obj in objs:
            if 'keypoints' not in obj:
                continue
            if max(obj['keypoints']) == 0:
                continue
            if 'num_keypoints' in obj and obj['num_keypoints'] == 0:
                continue
            joints_3d = np.zeros((num_joints, 3), dtype=np.float32)
            joints_3d_visible = np.zeros((num_joints, 3), dtype=np.float32)

            keypoints = np.array(obj['keypoints']).reshape(-1, 3)
            joints_3d[:, :2] = keypoints[:, :2]
            joints_3d_visible[:, :2] = np.minimum(1, keypoints[:, 2:3])

            center, scale = self._xywh2cs(*obj['clean_bbox'][:4])

            image_files = []
            cur_image_file = os.path.join(self.img_prefix,
                                          self.id2name[img_id])
            image_files.append(cur_image_file)

            prev_nm = file_name.split('/')[-1]
            ref_idx = int(prev_nm.replace('.jpg', ''))

            # training mode, choose an extra supporting frame
            if not self.test_mode:
                T = self.timestep_delta_range
                if self.timestep_delta_rand:
                    delta = -T + np.random.randint(T * 2 + 1)
                else:
                    delta = self.timestep_delta

                sup_idx = ref_idx + delta
                sup_idx = np.clip(sup_idx, 0, nframes - 1)
                sup_image_file = cur_image_file.replace(
                    prev_nm,
                    str(sup_idx).zfill(6) + '.jpg')

                if os.path.exists(sup_image_file):
                    sup_image_file = sup_image_file
                else:
                    sup_image_file = cur_image_file

                image_files.append(sup_image_file)
            else:
                # testing mode, using multiple frames
                # number of adjacent frames (one side)
                num_adj_frames = int((self.timestep_delta_range - 1) / 2)

                for i in range(num_adj_frames):
                    prev_idx = ref_idx - (i + 1)
                    next_idx = ref_idx + (i + 1)

                    prev_idx = np.clip(prev_idx, 0, nframes - 1)
                    next_idx = np.clip(next_idx, 0, nframes - 1)

                    prev_image_file = cur_image_file.replace(
                        prev_nm,
                        str(prev_idx).zfill(6) + '.jpg')
                    next_image_file = cur_image_file.replace(
                        prev_nm,
                        str(next_idx).zfill(6) + '.jpg')

                    if os.path.exists(prev_image_file):
                        image_files.append(prev_image_file)
                    else:
                        image_files.append(cur_image_file)

                    if os.path.exists(next_image_file):
                        image_files.append(next_image_file)
                    else:
                        image_files.append(cur_image_file)

            rec.append({
                'image_file': image_files,
                'center': center,
                'scale': scale,
                'bbox': obj['clean_bbox'][:4],
                'rotation': 0,
                'joints_3d': joints_3d,
                'joints_3d_visible': joints_3d_visible,
                'dataset': self.dataset_name,
                'bbox_score': 1,
                'bbox_id': bbox_id,
                'nframes': nframes,
                'frame_id': frame_id,
            })
            bbox_id = bbox_id + 1

        return rec

    def _load_coco_person_detection_results(self):
        """Load Posetrack person detection results.

        Only in test mode.
        """
        num_joints = self.ann_info['num_joints']
        all_boxes = None
        with open(self.bbox_file, 'r') as f:
            all_boxes = json.load(f)

        if not all_boxes:
            raise ValueError('=> Load %s fail!' % self.bbox_file)

        print(f'=> Total boxes: {len(all_boxes)}')

        kpt_db = []
        bbox_id = 0
        for det_res in all_boxes:
            if det_res['category_id'] != 1:
                continue

            score = det_res['score']
            if score < self.det_bbox_thr:
                continue

            box = det_res['bbox']

            # deal with different bbox file formats
            if 'nframes' in det_res and 'frame_id' in det_res:
                nframes = int(det_res['nframes'])
                frame_id = int(det_res['frame_id'])
            elif 'image_name' in det_res:
                img_id = self.name2id[det_res['image_name']]
                img_ann = self.coco.loadImgs(img_id)[0]
                nframes = int(img_ann['nframes'])
                frame_id = int(img_ann['frame_id'])
            else:
                img_id = det_res['image_id']
                img_ann = self.coco.loadImgs(img_id)[0]
                nframes = int(img_ann['nframes'])
                frame_id = int(img_ann['frame_id'])

            image_files = []
            if 'image_name' in det_res:
                file_name = det_res['image_name']
            else:
                file_name = self.id2name[det_res['image_id']]

            cur_image_file = os.path.join(self.img_prefix, file_name)
            image_files.append(cur_image_file)

            num_adj_frames = int((self.timestep_delta_range - 1) / 2)

            for i in range(num_adj_frames):
                prev_nm = file_name.split('/')[-1]
                ref_idx = int(prev_nm.replace('.jpg', ''))
                prev_idx = ref_idx - (i + 1)
                next_idx = ref_idx + (i + 1)

                prev_idx = np.clip(prev_idx, 0, nframes - 1)
                next_idx = np.clip(next_idx, 0, nframes - 1)

                prev_image_file = cur_image_file.replace(
                    prev_nm,
                    str(prev_idx).zfill(6) + '.jpg')
                next_image_file = cur_image_file.replace(
                    prev_nm,
                    str(next_idx).zfill(6) + '.jpg')

                if os.path.exists(prev_image_file):
                    image_files.append(prev_image_file)
                else:
                    image_files.append(cur_image_file)

                if os.path.exists(next_image_file):
                    image_files.append(next_image_file)
                else:
                    image_files.append(cur_image_file)

            center, scale = self._xywh2cs(*box[:4])
            joints_3d = np.zeros((num_joints, 3), dtype=np.float32)
            joints_3d_visible = np.ones((num_joints, 3), dtype=np.float32)
            kpt_db.append({
                'image_file': image_files,
                'center': center,
                'scale': scale,
                'rotation': 0,
                'bbox': box[:4],
                'bbox_score': score,
                'dataset': self.dataset_name,
                'joints_3d': joints_3d,
                'joints_3d_visible': joints_3d_visible,
                'bbox_id': bbox_id,
                'nframes': nframes,
                'frame_id': frame_id
            })
            bbox_id = bbox_id + 1
        print(f'=> Total boxes after filter '
              f'low score@{self.det_bbox_thr}: {bbox_id}')
        return kpt_db

    def evaluate(self, outputs, res_folder, metric='mAP', **kwargs):
        """Evaluate coco keypoint results. The pose prediction results will be
        saved in `${res_folder}/result_keypoints.json`.

        Note:
            num_keypoints: K

        Args:
            outputs (list(preds, boxes, image_paths))
                :preds (np.ndarray[N,K,3]): The first two dimensions are
                    coordinates, score is the third dimension of the array.
                :boxes (np.ndarray[N,6]): [center[0], center[1], scale[0]
                    , scale[1],area, score]
                :image_paths (list[str]): For example, ['val/010016_mpii_test
                    /000024.jpg']
                :heatmap (np.ndarray[N, K, H, W]): model output heatmap.
                :bbox_id (list(int))
            res_folder (str): Path of directory to save the results.
            metric (str | list[str]): Metric to be performed. Defaults: 'mAP'.

        Returns:
            dict: Evaluation results for evaluation metric.
        """
        metrics = metric if isinstance(metric, list) else [metric]
        allowed_metrics = ['mAP']
        for metric in metrics:
            if metric not in allowed_metrics:
                raise KeyError(f'metric {metric} is not supported')

        pred_folder = osp.join(res_folder, 'preds')
        os.makedirs(pred_folder, exist_ok=True)
        gt_folder = osp.join(
            osp.dirname(self.ann_file),
            osp.splitext(self.ann_file.split('_')[-1])[0])

        kpts = defaultdict(list)

        for output in outputs:
            preds = output['preds']
            boxes = output['boxes']
            image_paths = output['image_paths']
            bbox_ids = output['bbox_ids']

            batch_size = len(image_paths)
            for i in range(batch_size):
                if not isinstance(image_paths[i], list):
                    image_id = self.name2id[image_paths[i]
                                            [len(self.img_prefix):]]
                else:
                    image_id = self.name2id[image_paths[i][0]
                                            [len(self.img_prefix):]]

                kpts[image_id].append({
                    'keypoints': preds[i],
                    'center': boxes[i][0:2],
                    'scale': boxes[i][2:4],
                    'area': boxes[i][4],
                    'score': boxes[i][5],
                    'image_id': image_id,
                    'bbox_id': bbox_ids[i]
                })
        kpts = self._sort_and_unique_bboxes(kpts)

        # rescoring and oks nms
        num_joints = self.ann_info['num_joints']
        vis_thr = self.vis_thr
        oks_thr = self.oks_thr
        valid_kpts = defaultdict(list)
        for image_id in kpts.keys():
            img_kpts = kpts[image_id]
            for n_p in img_kpts:
                box_score = n_p['score']
                kpt_score = 0
                valid_num = 0
                for n_jt in range(0, num_joints):
                    t_s = n_p['keypoints'][n_jt][2]
                    if t_s > vis_thr:
                        kpt_score = kpt_score + t_s
                        valid_num = valid_num + 1
                if valid_num != 0:
                    kpt_score = kpt_score / valid_num
                # rescoring
                n_p['score'] = kpt_score * box_score

            if self.use_nms:
                nms = soft_oks_nms if self.soft_nms else oks_nms
                keep = nms(img_kpts, oks_thr, sigmas=self.sigmas)
                valid_kpts[image_id].append(
                    [img_kpts[_keep] for _keep in keep])
            else:
                valid_kpts[image_id].append(img_kpts)

        self._write_posetrack18_keypoint_results(valid_kpts, gt_folder,
                                                 pred_folder)

        info_str = self._do_python_keypoint_eval(gt_folder, pred_folder)
        name_value = OrderedDict(info_str)

        return name_value

    @staticmethod
    def _write_posetrack18_keypoint_results(keypoint_results, gt_folder,
                                            pred_folder):
        """Write results into a json file.

        Args:
            keypoint_results (dict): keypoint results organized by image_id.
            gt_folder (str): Path of directory for official gt files.
            pred_folder (str): Path of directory to save the results.
        """
        categories = []

        cat = {}
        cat['supercategory'] = 'person'
        cat['id'] = 1
        cat['name'] = 'person'
        cat['keypoints'] = [
            'nose', 'head_bottom', 'head_top', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee',
            'right_knee', 'left_ankle', 'right_ankle'
        ]
        cat['skeleton'] = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13],
                           [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10],
                           [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5],
                           [4, 6], [5, 7]]
        categories.append(cat)

        json_files = [
            pos for pos in os.listdir(gt_folder) if pos.endswith('.json')
        ]
        for json_file in json_files:

            with open(osp.join(gt_folder, json_file), 'r') as f:
                gt = json.load(f)

            annotations = []
            images = []

            for image in gt['images']:
                im = {}
                im['id'] = image['id']
                im['file_name'] = image['file_name']
                images.append(im)

                img_kpts = keypoint_results[im['id']]

                if len(img_kpts) == 0:
                    continue
                for track_id, img_kpt in enumerate(img_kpts[0]):
                    ann = {}
                    ann['image_id'] = img_kpt['image_id']
                    ann['keypoints'] = np.array(
                        img_kpt['keypoints']).reshape(-1).tolist()
                    ann['scores'] = np.array(ann['keypoints']).reshape(
                        [-1, 3])[:, 2].tolist()
                    ann['score'] = float(img_kpt['score'])
                    ann['track_id'] = track_id
                    annotations.append(ann)

            info = {}
            info['images'] = images
            info['categories'] = categories
            info['annotations'] = annotations

            with open(osp.join(pred_folder, json_file), 'w') as f:
                json.dump(info, f, sort_keys=True, indent=4)

    def _do_python_keypoint_eval(self, gt_folder, pred_folder):
        """Keypoint evaluation using poseval."""

        argv = ['', gt_folder + '/', pred_folder + '/']

        print('Loading data')
        gtFramesAll, prFramesAll = eval_helpers.load_data_dir(argv)

        print('# gt frames  :', len(gtFramesAll))
        print('# pred frames:', len(prFramesAll))

        # evaluate per-frame multi-person pose estimation (AP)
        # compute AP
        print('Evaluation of per-frame multi-person pose estimation')
        apAll, _, _ = evaluateAP(gtFramesAll, prFramesAll, None, False, False)

        # print AP
        print('Average Precision (AP) metric:')
        eval_helpers.printTable(apAll)

        stats = eval_helpers.getCum(apAll)

        stats_names = [
            'Head AP', 'Shou AP', 'Elb AP', 'Wri AP', 'Hip AP', 'Knee AP',
            'Ankl AP', 'Total AP'
        ]

        info_str = list(zip(stats_names, stats))

        return info_str
