_base_ = [
    '../../../../_base_/default_runtime.py',
    '../../../../_base_/datasets/campus.py'
]
checkpoint_config = dict(interval=1)
evaluation = dict(
    interval=1, metric='pcp', save_best='pcp', recall_threshold=500)

optimizer = dict(
    type='Adam',
    lr=0.0001,
)
optimizer_config = dict(grad_clip=None)

# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[10, 20])
total_epochs = 30
log_config = dict(
    interval=50, hooks=[
        dict(type='TextLoggerHook'),
    ])

space_size = [12000.0, 12000.0, 2000.0]
space_center = [3000.0, 4500.0, 1000.0]
cube_size = [80, 80, 20]
sub_space_size = [2000.0, 2000.0, 2000.0]
sub_cube_size = [64, 64, 64]
image_size = [800, 640]
heatmap_size = [200, 160]

num_joints = 17

data_root = 'data/campus'
train_data_cfg = dict(
    space_size=space_size,
    space_center=space_center,
    cube_size=cube_size,
    image_size=image_size,
    heatmap_size=[heatmap_size],
    num_joints=num_joints,
    cam_list=[0, 1, 2],
    num_cameras=3,
    subset='train',
    width=360,
    height=288,
    root_id=[2, 3],
    coco_lhip_idx=11,
    coco_rhip_idx=12,
    max_nposes=10,
    min_nposes=1,
    num_train_sampels=3000,
    maximum_person=10,
    cam_file=f'{data_root}/calibration_campus.json',
    test_pose_db_file=f'{data_root}/pred_campus_maskrcnn_hrnet_coco.pkl',
    train_pose_db_file=f'{data_root}/panoptic_training_pose.pkl',
    gt_pose_db_file=f'{data_root}/actorsGT.mat',
)

test_data_cfg = train_data_cfg.copy()
test_data_cfg.update(dict(subset='test'))

# model settings
model = dict(
    type='DetectAndRegress',
    backbone=None,
    pretrained=None,
    human_detector=dict(
        type='VoxelCenterDetector',
        image_size=image_size,
        heatmap_size=heatmap_size,
        space_size=space_size,
        cube_size=cube_size,
        space_center=space_center,
        center_net=dict(
            type='V2VNet', input_channels=num_joints, output_channels=1),
        center_head=dict(
            type='CuboidCenterHead',
            space_size=space_size,
            space_center=space_center,
            cube_size=cube_size,
            max_num=10,
            max_pool_kernel=3),
        train_cfg=dict(dist_threshold=500.0),
        test_cfg=dict(center_threshold=0.1),
    ),
    pose_regressor=dict(
        type='VoxelSinglePose',
        image_size=image_size,
        heatmap_size=heatmap_size,
        sub_space_size=sub_space_size,
        sub_cube_size=sub_cube_size,
        num_joints=num_joints,
        pose_net=dict(
            type='V2VNet',
            input_channels=num_joints,
            output_channels=num_joints),
        pose_head=dict(type='CuboidPoseHead', beta=100.0)))

train_pipeline = [
    dict(
        type='MultiItemProcess',
        pipeline=[
            dict(
                type='AffineJoints',
                item='joints',
                visible_item='joints_visible'),
            dict(
                type='GenerateInputHeatmaps',
                item='joints',
                visible_item='joints_visible',
                obscured=0.0,
                from_pred=False,
                sigma=3,
                scale=1.0,
                base_size=96,
                target_type='gaussian',
                heatmap_cfg=dict(
                    base_scale=0.9,
                    offset=0.03,
                    threshold=0.6,
                    extra=[
                        dict(
                            joint_ids=[7, 8], scale_factor=0.5, threshold=0.1),
                        dict(
                            joint_ids=[9, 10],
                            scale_factor=0.2,
                            threshold=0.1,
                        ),
                        dict(
                            joint_ids=[
                                0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16
                            ],
                            scale_factor=0.5,
                            threshold=0.05)
                    ]))
        ]),
    dict(
        type='DiscardDuplicatedItems',
        keys_list=[
            'joints_3d', 'joints_3d_visible', 'ann_info', 'roots_3d',
            'num_persons', 'sample_id'
        ]),
    dict(
        type='GenerateVoxel3DHeatmapTarget',
        sigma=200.0,
        joint_indices=[[11, 12]]),
    dict(
        type='Collect',
        keys=['sample_id', 'input_heatmaps', 'targets_3d'],
        meta_keys=[
            'num_persons', 'joints_3d', 'camera', 'center', 'scale',
            'joints_3d_visible', 'roots_3d', 'sample_id'
        ]),
]

val_pipeline = [
    dict(
        type='MultiItemProcess',
        pipeline=[
            dict(type='AffineJoints', item='joints'),
            dict(
                type='GenerateInputHeatmaps',
                item='joints',
                from_pred=True,
                scale=1.0,
                sigma=3,
                base_size=96,
                target_type='gaussian'),
        ]),
    dict(
        type='DiscardDuplicatedItems',
        keys_list=[
            'joints_3d', 'joints_3d_visible', 'joints_2d', 'joints_2d_visible',
            'ann_info', 'sample_id'
        ]),
    dict(
        type='Collect',
        keys=['sample_id', 'input_heatmaps'],
        meta_keys=['sample_id', 'camera', 'center', 'scale']),
]

test_pipeline = val_pipeline

data_root = 'data/campus'
data = dict(
    samples_per_gpu=1,
    workers_per_gpu=4,
    val_dataloader=dict(samples_per_gpu=1),
    test_dataloader=dict(samples_per_gpu=1),
    train=dict(
        type='Body3DMviewDirectCampusDataset',
        ann_file=None,
        img_prefix=data_root,
        data_cfg=train_data_cfg,
        pipeline=train_pipeline,
        dataset_info={{_base_.dataset_info}}),
    val=dict(
        type='Body3DMviewDirectCampusDataset',
        ann_file=None,
        img_prefix=data_root,
        data_cfg=test_data_cfg,
        pipeline=val_pipeline,
        dataset_info={{_base_.dataset_info}}),
    test=dict(
        type='Body3DMviewDirectCampusDataset',
        ann_file=None,
        img_prefix=data_root,
        data_cfg=test_data_cfg,
        pipeline=test_pipeline,
        dataset_info={{_base_.dataset_info}}),
)
