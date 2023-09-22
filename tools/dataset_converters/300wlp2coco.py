import json
import os
import os.path as osp
import shutil
import time

import cv2
import numpy as np
from scipy.io import loadmat


# Move all images to one folder
def move_img(img_path, save_img):
    path_list = ['AFW', 'HELEN', 'IBUG', 'LFPW']
    # 保存路径
    if not os.path.isdir(save_img):
        os.makedirs(save_img)

    for people_name in path_list:
        # 读取文件夹中图片
        Image_dir = os.path.join(img_path, people_name)
        img_list = os.listdir(Image_dir)
        for img_name in img_list:
            if 'jpg' in img_name:
                old_img_path = Image_dir + '/' + img_name
                shutil.move(old_img_path, save_img + '/' + img_name)


# split 300w-lp data
def split_data(file_img, train_path, val_path,
               test_path, shuffle=True, ratio1=0.8, ratio2=0.1):
    img_list = os.listdir(file_img)
    if shuffle:
        np.random.shuffle(img_list)

    n_total = len(img_list)
    offset_train = int(n_total * ratio1)
    offset_val = int(n_total * ratio2) + offset_train
    train_img = img_list[:offset_train]
    val_img = img_list[offset_train:offset_val]
    test_img = img_list[offset_val:]
    for img in train_img:
        shutil.move(file_img + '/' + img, train_path + '/' + img)
    for img in val_img:
        shutil.move(file_img + '/' + img, val_path + '/' + img)
    for img in test_img:
        shutil.move(file_img + '/' + img, test_path + '/' + img)


def default_dump(obj):
    """Convert numpy classes to JSON serializable objects."""
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def convert_300WLP_to_coco(root_path, img_pathDir, out_file):
    annotations = []
    images = []
    cnt = 0
    if 'trainval' in img_pathDir:
        img_dir_list = ['train', 'val']
    else:
        img_dir_list = [img_pathDir]

    for tv in img_dir_list:

        img_dir = osp.join(root_path, tv)
        landmark_dir = os.path.join(root_path, '300W_LP', 'landmarks')
        img_list = os.listdir(img_dir)

        for idx, img_name in enumerate(img_list):
            cnt += 1
            img_path = osp.join(img_dir, img_name)
            type_name = img_name.split('_')[0]
            ann_name = img_name.split('.')[0] + '_pts.mat'
            ann_path = osp.join(landmark_dir, type_name, ann_name)
            data_info = loadmat(ann_path)

            img = cv2.imread(img_path)

            keypoints = data_info['pts_2d']
            keypoints_all = []
            for i in range(keypoints.shape[0]):
                x, y = keypoints[i][0], keypoints[i][1]
                keypoints_all.append([x, y, 2])
            keypoints = np.array(keypoints_all)

            x1, y1, _ = np.amin(keypoints, axis=0)
            x2, y2, _ = np.amax(keypoints, axis=0)
            w, h = x2 - x1, y2 - y1
            bbox = [x1, y1, w, h]

            image = {}
            image['id'] = cnt
            image['file_name'] = img_name
            image['height'] = img.shape[0]
            image['width'] = img.shape[1]
            images.append(image)

            ann = {}
            ann['keypoints'] = keypoints.reshape(-1).tolist()
            ann['image_id'] = cnt
            ann['id'] = cnt
            ann['num_keypoints'] = len(keypoints)
            ann['bbox'] = bbox
            ann['iscrowd'] = 0
            ann['area'] = int(ann['bbox'][2] * ann['bbox'][3])
            ann['category_id'] = 1

            annotations.append(ann)

    cocotype = {}

    cocotype['info'] = {}
    cocotype['info']['description'] = 'LaPa Generated by MMPose Team'
    cocotype['info']['version'] = 1.0
    cocotype['info']['year'] = time.strftime('%Y', time.localtime())
    cocotype['info']['date_created'] = time.strftime('%Y/%m/%d',
                                                     time.localtime())

    cocotype['images'] = images
    cocotype['annotations'] = annotations
    cocotype['categories'] = [{
        'supercategory': 'person',
        'id': 1,
        'name': 'face',
        'keypoints': [],
        'skeleton': []
    }]

    json.dump(
        cocotype,
        open(out_file, 'w'),
        ensure_ascii=False,
        default=default_dump)
    print(f'done {out_file}')


if __name__ == "__main__":
    # 1.Move all images to one folder
    # 2.split 300W-LP data
    # 3.convert json
    img_path = './300W-LP/300W-LP'
    save_img = './300W-LP/images'
    move_img(img_path, save_img)

    file_img = './300W-LP/images'
    train_path = './300W-LP/train'
    val_path = './300W-LP/val'
    test_path = './300W-LP/test'
    split_data(save_img, train_path, val_path, test_path)

    root_path = './300W-LP'
    anno_path_json = osp.join(root_path, 'annotations')
    if not osp.exists(anno_path_json):
        os.makedirs(anno_path_json)
    for tv in ['val', 'test', 'train']:
        print(f'processing {tv}')
        convert_300WLP_to_coco(root_path, tv, anno_path_json + '/' + f'face_landmarks_300wlp_{tv}.json')
