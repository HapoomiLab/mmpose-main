import pytest

from mmpose.apis import (get_track_id, inference_top_down_pose_model,
                         init_pose_model, vis_pose_tracking_result)


def test_pose_tracking_demo():
    # COCO demo
    # build the pose model from a config file and a checkpoint file
    pose_model = init_pose_model(
        'configs/top_down/resnet/coco/res50_coco_256x192.py',
        None,
        device='cpu')
    image_name = 'tests/data/coco/000000000785.jpg'
    # test a single image, with a list of bboxes.
    pose_results, _ = inference_top_down_pose_model(
        pose_model, image_name, [[50, 50, 50, 100]], format='xywh')
    pose_results, next_id = get_track_id(pose_results, [], next_id=0)
    # show the results
    vis_pose_tracking_result(pose_model, image_name, pose_results)
    pose_results_last = pose_results

    # AIC demo
    pose_model = init_pose_model(
        'configs/top_down/resnet/aic/res50_aic_256x192.py', None, device='cpu')
    image_name = 'tests/data/aic/054d9ce9201beffc76e5ff2169d2af2f027002ca.jpg'
    # test a single image, with a list of bboxes.
    pose_results, _ = inference_top_down_pose_model(
        pose_model,
        image_name, [[50, 50, 50, 100]],
        format='xywh',
        dataset='TopDownAicDataset')
    pose_results, next_id = get_track_id(pose_results, pose_results_last,
                                         next_id)
    # show the results
    vis_pose_tracking_result(
        pose_model, image_name, pose_results, dataset='TopDownAicDataset')

    # OneHand10K demo
    # build the pose model from a config file and a checkpoint file
    pose_model = init_pose_model(
        'configs/hand/resnet/onehand10k/res50_onehand10k_256x256.py',
        None,
        device='cpu')
    image_name = 'tests/data/onehand10k/9.jpg'
    # test a single image, with a list of bboxes.
    pose_results, _ = inference_top_down_pose_model(
        pose_model,
        image_name, [[10, 10, 30, 30]],
        format='xywh',
        dataset='OneHand10KDataset')
    pose_results, next_id = get_track_id(pose_results, pose_results_last,
                                         next_id)

    # InterHand2D demo
    pose_model = init_pose_model(
        'configs/hand/resnet/interhand2d/res50_interhand2d_all_256x256.py',
        None,
        device='cpu')
    image_name = 'tests/data/interhand2d/image2017.jpg'
    # test a single image, with a list of bboxes.
    pose_results, _ = inference_top_down_pose_model(
        pose_model, image_name, [[50, 50, 50, 100]], format='xywh')
    pose_results, next_id = get_track_id(pose_results, [], next_id=0)
    # show the results
    vis_pose_tracking_result(pose_model, image_name, pose_results)
    # show the results
    vis_pose_tracking_result(
        pose_model, image_name, pose_results, dataset='InterHand2DDataset')

    with pytest.raises(NotImplementedError):
        vis_pose_tracking_result(
            pose_model, image_name, pose_results, dataset='test')
