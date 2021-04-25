import json
import os
import re
import time
import warnings

import cv2
import numpy as np
import xmltodict
from xtcocotools.coco import COCO

np.random.seed(0)


def list_all_files(root_dir, ext='.xml'):
    """List all files in the root directory and all its sub directories.

    :param root_dir: root directory
    :param ext: filename extension
    :return: list of files
    """
    files = []
    file_list = os.listdir(root_dir)
    for i in range(0, len(file_list)):
        path = os.path.join(root_dir, file_list[i])
        if os.path.isdir(path):
            files.extend(list_all_files(path))
        if os.path.isfile(path):
            if path.lower().endswith(ext):
                files.append(path)
    return files


def get_anno_info():
    keypoints_info = [
        'L_Eye',
        'R_Eye',
        'L_EarBase',
        'R_EarBase',
        'Nose',
        'Throat',
        'TailBase',
        'Withers',
        'L_F_Elbow',
        'R_F_Elbow',
        'L_B_Elbow',
        'R_B_Elbow',
        'L_F_Knee',
        'R_F_Knee',
        'L_B_Knee',
        'R_B_Knee',
        'L_F_Paw',
        'R_F_Paw',
        'L_B_Paw',
        'R_B_Paw',
    ]
    skeleton_info = [[1, 2], [1, 3], [2, 4], [1, 5], [2, 5], [5, 6], [6, 8],
                     [7, 8], [6, 9], [9, 13], [13, 17], [6, 10], [10, 14],
                     [14, 18], [7, 11], [11, 15], [15, 19], [7, 12], [12, 16],
                     [16, 20]]
    category_info = [{
        'supercategory': 'animal',
        'id': 0,
        'name': 'cat',
        'keypoints': keypoints_info,
        'skeleton': skeleton_info
    }, {
        'supercategory': 'animal',
        'id': 1,
        'name': 'cow',
        'keypoints': keypoints_info,
        'skeleton': skeleton_info
    }, {
        'supercategory': 'animal',
        'id': 2,
        'name': 'dog',
        'keypoints': keypoints_info,
        'skeleton': skeleton_info
    }, {
        'supercategory': 'animal',
        'id': 3,
        'name': 'horse',
        'keypoints': keypoints_info,
        'skeleton': skeleton_info
    }, {
        'supercategory': 'animal',
        'id': 4,
        'name': 'sheep',
        'keypoints': keypoints_info,
        'skeleton': skeleton_info
    }]

    return keypoints_info, skeleton_info, category_info


def xml2coco_trainval(file_list, img_root, save_path, start_ann_id=0):
    """Save annotations in coco-format.

    :param file_list: list of data annotation files.
    :param img_root: the root dir to load images.
    :param save_path: the path to save transformed annotation file.
    :param start_ann_id: the starting point to count the annotation id.
    :param val_num: the number of annotated objects for validation.
    """
    images = []
    annotations = []
    img_ids = []
    ann_ids = []

    ann_id = start_ann_id

    name2id = {
        'L_Eye': 0,
        'R_Eye': 1,
        'L_EarBase': 2,
        'R_EarBase': 3,
        'Nose': 4,
        'Throat': 5,
        'TailBase': 6,
        'Withers': 7,
        'L_F_Elbow': 8,
        'R_F_Elbow': 9,
        'L_B_Elbow': 10,
        'R_B_Elbow': 11,
        'L_F_Knee': 12,
        'R_F_Knee': 13,
        'L_B_Knee': 14,
        'R_B_Knee': 15,
        'L_F_Paw': 16,
        'R_F_Paw': 17,
        'L_B_Paw': 18,
        'R_B_Paw': 19
    }
    cat2id = {'cat': 0, 'cow': 1, 'dog': 2, 'horse': 3, 'sheep': 4}

    for file in file_list:
        category_id = cat2id[file.split('/')[-2]]

        data_anno = xmltodict.parse(open(file).read())['annotation']

        img_id = int(data_anno['image'].split('_')[0] +
                     data_anno['image'].split('_')[1])

        if img_id not in img_ids:
            image_name = 'VOC2012/JPEGImages/' + data_anno['image'] + '.jpg'
            img = cv2.imread(os.path.join(img_root, image_name))

            image = {}
            image['id'] = img_id
            image['file_name'] = image_name
            image['height'] = img.shape[0]
            image['width'] = img.shape[1]

            images.append(image)
            img_ids.append(img_id)
        else:
            pass

        keypoint_anno = data_anno['keypoints']['keypoint']
        assert len(keypoint_anno) == 20

        keypoints = np.zeros([20, 3], dtype=np.float32)

        for kpt_anno in keypoint_anno:
            keypoint_name = kpt_anno['@name']
            keypoint_id = name2id[keypoint_name]

            visibility = int(kpt_anno['@visible'])

            if visibility == 0:
                continue
            else:
                keypoints[keypoint_id, 0] = float(kpt_anno['@x'])
                keypoints[keypoint_id, 1] = float(kpt_anno['@y'])
                keypoints[keypoint_id, 2] = 2

        anno = {}
        anno['keypoints'] = keypoints.reshape(-1).tolist()
        anno['image_id'] = img_id
        anno['id'] = ann_id
        anno['num_keypoints'] = int(sum(keypoints[:, 2] > 0))

        visible_bounds = data_anno['visible_bounds']
        anno['bbox'] = [
            float(visible_bounds['@xmin']),
            float(visible_bounds['@ymin']),
            float(visible_bounds['@width']),
            float(visible_bounds['@height'])
        ]
        anno['iscrowd'] = 0
        anno['area'] = float(anno['bbox'][2] * anno['bbox'][3])
        anno['category_id'] = category_id

        annotations.append(anno)
        ann_ids.append(ann_id)
        ann_id += 1

    cocotype = {}

    cocotype['info'] = {}
    cocotype['info'][
        'description'] = 'AnimalPose dataset Generated by MMPose Team'
    cocotype['info']['version'] = '1.0'
    cocotype['info']['year'] = time.strftime('%Y', time.localtime())
    cocotype['info']['date_created'] = time.strftime('%Y/%m/%d',
                                                     time.localtime())

    cocotype['images'] = images
    cocotype['annotations'] = annotations

    keypoints_info, skeleton_info, category_info = get_anno_info()

    cocotype['categories'] = category_info

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    json.dump(cocotype, open(save_path, 'w'), indent=4)
    print('number of images:', len(img_ids))
    print('number of annotations:', len(ann_ids))
    print(f'done {save_path}')


def xml2coco_test(file_list, img_root, save_path, start_ann_id=0):
    """Save annotations in coco-format.

    :param file_list: list of data annotation files.
    :param img_root: the root dir to load images.
    :param save_path: the path to save transformed annotation file.
    :param start_ann_id: the starting point to count the annotation id.
    """
    images = []
    annotations = []
    img_ids = []
    ann_ids = []

    ann_id = start_ann_id

    name2id = {
        'L_eye': 0,
        'R_eye': 1,
        'L_ear': 2,
        'R_ear': 3,
        'Nose': 4,
        'Throat': 5,
        'Tail': 6,
        'withers': 7,
        'L_F_elbow': 8,
        'R_F_elbow': 9,
        'L_B_elbow': 10,
        'R_B_elbow': 11,
        'L_F_knee': 12,
        'R_F_knee': 13,
        'L_B_knee': 14,
        'R_B_knee': 15,
        'L_F_paw': 16,
        'R_F_paw': 17,
        'L_B_paw': 18,
        'R_B_paw': 19
    }

    cat2id = {'cat': 0, 'cow': 1, 'dog': 2, 'horse': 3, 'sheep': 4}

    for file in file_list:
        data_anno = xmltodict.parse(open(file).read())['annotation']

        category_id = cat2id[data_anno['category']]

        img_id = category_id * 1000 + int(
            re.findall(r'\d+', data_anno['image'])[0])

        assert img_id not in img_ids

        # prepare images
        image_name = os.path.join('animalpose_image_part2',
                                  data_anno['category'], data_anno['image'])
        img = cv2.imread(os.path.join(img_root, image_name))

        image = {}
        image['id'] = img_id
        image['file_name'] = image_name
        image['height'] = img.shape[0]
        image['width'] = img.shape[1]

        images.append(image)
        img_ids.append(img_id)

        # prepare annotations
        keypoint_anno = data_anno['keypoints']['keypoint']
        keypoints = np.zeros([20, 3], dtype=np.float32)

        for kpt_anno in keypoint_anno:
            keypoint_name = kpt_anno['@name']
            keypoint_id = name2id[keypoint_name]

            visibility = int(kpt_anno['@visible'])

            if visibility == 0:
                continue
            else:
                keypoints[keypoint_id, 0] = float(kpt_anno['@x'])
                keypoints[keypoint_id, 1] = float(kpt_anno['@y'])
                keypoints[keypoint_id, 2] = 2

        anno = {}
        anno['keypoints'] = keypoints.reshape(-1).tolist()
        anno['image_id'] = img_id
        anno['id'] = ann_id
        anno['num_keypoints'] = int(sum(keypoints[:, 2] > 0))

        visible_bounds = data_anno['visible_bounds']
        anno['bbox'] = [
            float(visible_bounds['@xmin']),
            float(visible_bounds['@xmax']
                  ),  # typo in original xml: should be 'ymin'
            float(visible_bounds['@width']),
            float(visible_bounds['@height'])
        ]
        anno['iscrowd'] = 0
        anno['area'] = float(anno['bbox'][2] * anno['bbox'][3])
        anno['category_id'] = category_id

        annotations.append(anno)
        ann_ids.append(ann_id)
        ann_id += 1

    cocotype = {}

    cocotype['info'] = {}
    cocotype['info'][
        'description'] = 'AnimalPose dataset Generated by MMPose Team'
    cocotype['info']['version'] = '1.0'
    cocotype['info']['year'] = time.strftime('%Y', time.localtime())
    cocotype['info']['date_created'] = time.strftime('%Y/%m/%d',
                                                     time.localtime())

    cocotype['images'] = images
    cocotype['annotations'] = annotations

    keypoints_info, skeleton_info, category_info = get_anno_info()

    cocotype['categories'] = category_info

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    json.dump(cocotype, open(save_path, 'w'), indent=4)
    print('=========================================================')
    print('number of images:', len(img_ids))
    print('number of annotations:', len(ann_ids))
    print(f'done {save_path}')


def split_train_val(work_dir, trainval_file, train_file, val_file,
                    val_ann_num):
    """Split train-val json file into training and validation files.

    :param work_dir: path to load train-val json file, and save split files.
    :param trainval_file: The input json file combining both train and val.
    :param trainval_file: The output json file for training.
    :param trainval_file: The output json file for validation.
    :param val_ann_num: the number of validation annotations.
    """

    coco = COCO(os.path.join(work_dir, trainval_file))

    img_list = list(coco.imgs.keys())
    np.random.shuffle(img_list)

    count = 0

    images_train = []
    images_val = []
    annotations_train = []
    annotations_val = []

    for img_id in img_list:
        ann_ids = coco.getAnnIds(img_id)

        if count + len(ann_ids) <= val_ann_num:
            # for validation
            count += len(ann_ids)
            images_val.append(coco.imgs[img_id])
            for ann_id in ann_ids:
                annotations_val.append(coco.anns[ann_id])

        else:
            images_train.append(coco.imgs[img_id])
            for ann_id in ann_ids:
                annotations_train.append(coco.anns[ann_id])

    if count == val_ann_num:
        print(f'We have found {count} annotations for validation.')
    else:
        warnings.warn(
            f'We only found {count} annotations, instead of {val_ann_num}.')

    cocotype_train = {}
    cocotype_val = {}

    keypoints_info, skeleton_info, category_info = get_anno_info()

    cocotype_train['info'] = {}
    cocotype_train['info'][
        'description'] = 'AnimalPose dataset Generated by MMPose Team'
    cocotype_train['info']['version'] = '1.0'
    cocotype_train['info']['year'] = time.strftime('%Y', time.localtime())
    cocotype_train['info']['date_created'] = time.strftime(
        '%Y/%m/%d', time.localtime())
    cocotype_train['images'] = images_train
    cocotype_train['annotations'] = annotations_train
    cocotype_train['categories'] = category_info

    json.dump(
        cocotype_train,
        open(os.path.join(work_dir, train_file), 'w'),
        indent=4)
    print('=========================================================')
    print('number of images:', len(images_train))
    print('number of annotations:', len(annotations_train))
    print(f'done {train_file}')

    cocotype_val['info'] = {}
    cocotype_val['info'][
        'description'] = 'AnimalPose dataset Generated by MMPose Team'
    cocotype_val['info']['version'] = '1.0'
    cocotype_val['info']['year'] = time.strftime('%Y', time.localtime())
    cocotype_val['info']['date_created'] = time.strftime(
        '%Y/%m/%d', time.localtime())
    cocotype_val['images'] = images_val
    cocotype_val['annotations'] = annotations_val
    cocotype_val['categories'] = category_info

    json.dump(
        cocotype_val, open(os.path.join(work_dir, val_file), 'w'), indent=4)
    print('=========================================================')
    print('number of images:', len(images_val))
    print('number of annotations:', len(annotations_val))
    print(f'done {val_file}')


dataset_dir = 'data/animalpose/'

# We choose the images from PascalVOC for train + val
# In total, train+val: 3608 images, 5117 annotations
xml2coco_trainval(
    list_all_files(os.path.join(dataset_dir, 'PASCAL2011_animal_annotation')),
    dataset_dir,
    os.path.join(dataset_dir, 'annotations', 'animalpose_trainval.json'),
    start_ann_id=1000000)

# train: 2798 images, 4000 annotations
# val: 810 images, 1117 annotations
split_train_val(
    os.path.join(dataset_dir, 'annotations'),
    'animalpose_trainval.json',
    'animalpose_train.json',
    'animalpose_val.json',
    val_ann_num=1117)

# We choose the remaining 1000 images for test
# 1000 images, 1000 annotations
xml2coco_test(
    list_all_files(os.path.join(dataset_dir, 'animalpose_anno2')),
    dataset_dir,
    os.path.join(dataset_dir, 'annotations', 'animalpose_test.json'),
    start_ann_id=0)
