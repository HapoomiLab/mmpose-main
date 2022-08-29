# Migration

MMPose 1.0 has made significant BC-breaking changes, with modules redesigned and reorganized to reduce code redundancy and improve efficiency. For developers who have some deep-learning knowledge, this tutorial provides a migration guide.

Whether you are **a user of the previous version of MMPose**, or **a new user wishing to migrate your Pytorch project to MMPose**, you can learn how to build a project based on MMpose 1.0 with this tutorial.

This  tutorial covers what developers will care about when using MMPose 1.0:

- Overall code architecture

- How to manage modules with configs

- How to use my own custom datasets

- How to add new modules(backbone, head, loss function, etc.)

## Overall code architecture

Generally speaking, there are **five parts** developers will use during project development:

- **General:** Environment, Hook, Checkpoint, Logger, Timer, etc.

- **Data:** Dataset、Dataloader、Data Augmentations, etc.

- **Training:** Optimizer、Learning Rate, etc.

- **Model:** Backbone、Neck、Head、Loss functions, etc.

- **Evaluation:** Metrics

Among them, modules related to **General**, **Training** and **Evaluation** are often provided by the training frameworks, developers only need to call APIs and adjust the parameters.  Developers mainly focus on implementing the **Data** and **Model** parts.

## Step1: Configs

In MMPose, we use a Python file as config for the definition, parameter management of the whole project. Therefore, we strongly recommend the developers who use MMPose for the first time to refer to \[Config\].

Note that all the new modules need to be registered using `Registry`, and `import` in `__init__.py` in the corresponding directory.

## Step2: Data

The organization of data in MMPose contains:

- Dataset Information

- Dataset

- Pipeline

### Dataset Information

In MMPose, **data is organized in COCO style**, and we define a base class `BaseCocoStyleDataset` under `$MMPOSE/mmpose/datasets/base`.

Please refer to \[COCO\] for more details about the COCO data format.

The data format of bbox is in `xyxy` instead of `xywh`, which is consistent with the format used in MMDetection.

If your data is originally stored in COCO format, then you can use our implementation directly.

If not, you need to define the key point information of the data (key point order, skeleton information, weights, sigmas of annotation information) in the`$MMPOSE/configs/_base_/datasets`.

For the conversion between different bbox formats, we also provide many useful utils, such as `bbox_xyxy2xywh`, `bbox_xywh2xyxy`, `bbox_xyxy2cs`, etc., defined in `$MMPOSE/mmpose/structures/bbox/transforms.py`, which can help you to convert your own data formats.

Take the MPII dataset (`$MMPOSE/configs/_base_/datasets/mpii.py`) as an example.

```Python
dataset_info = dict(
    dataset_name='mpii',
    paper_info=dict(
        author='Mykhaylo Andriluka and Leonid Pishchulin and '
        'Peter Gehler and Schiele, Bernt',
        title='2D Human Pose Estimation: New Benchmark and '
        'State of the Art Analysis',
        container='IEEE Conference on Computer Vision and '
        'Pattern Recognition (CVPR)',
        year='2014',
        homepage='http://human-pose.mpi-inf.mpg.de/',
    ),
    keypoint_info={
        0:
        dict(
            name='right_ankle',
            id=0,
            color=[255, 128, 0],
            type='lower',
            swap='left_ankle'),
        ## omitted
    },
    skeleton_info={
        0:
        dict(link=('right_ankle', 'right_knee'), id=0, color=[255, 128, 0]),
        ## omitted
    },
    joint_weights=[
        1.5, 1.2, 1., 1., 1.2, 1.5, 1., 1., 1., 1., 1.5, 1.2, 1., 1., 1.2, 1.5
    ],
    # Adapted from COCO dataset.
    sigmas=[
        0.089, 0.083, 0.107, 0.107, 0.083, 0.089, 0.026, 0.026, 0.026, 0.026,
        0.062, 0.072, 0.179, 0.179, 0.072, 0.062
    ])
```

### Dataset

When your data is not stored in COCO format, you need to implement the `Dataset` class in `$MMPOSE/mmpose/datasets/datasets`, and convert the data into COCO format.

Let's take the implementation of the MPII dataset (`$MMPOSE/mmpose/datasets/datasets/body/mpii_dataset.py`) as an example.

```Python
@DATASETS.register_module()
class MpiiDataset(BaseCocoStyleDataset):
    METAINFO: dict = dict(from_file='configs/_base_/datasets/mpii.py')

    def __init__(self,
                 ## omitted
                 headbox_file: Optional[str] = None,
                 ## omitted):

        if headbox_file:
            if data_mode != 'topdown':
                raise ValueError(
                    f'{self.__class__.__name__} is set to {data_mode}: '
                    'mode, while "headbox_file" is only '
                    'supported in topdown mode.')

            if not test_mode:
                raise ValueError(
                    f'{self.__class__.__name__} has `test_mode==False` '
                    'while "headbox_file" is only '
                    'supported when `test_mode==True`.')

            headbox_file_type = headbox_file[-3:]
            allow_headbox_file_type = ['mat']
            if headbox_file_type not in allow_headbox_file_type:
                raise KeyError(
                    f'The head boxes file type {headbox_file_type} is not '
                    f'supported. Should be `mat` but got {headbox_file_type}.')
        self.headbox_file = headbox_file

        super().__init__(
            ## omitted
            )

    def _load_annotations(self) -> List[dict]:
        """Load data from annotations in MPII format."""
        check_file_exist(self.ann_file)
        with open(self.ann_file) as anno_file:
            anns = json.load(anno_file)

        if self.headbox_file:
            check_file_exist(self.headbox_file)
            headbox_dict = loadmat(self.headbox_file)
            headboxes_src = np.transpose(headbox_dict['headboxes_src'],
                                         [2, 0, 1])
            SC_BIAS = 0.6

        data_list = []
        ann_id = 0

        # mpii bbox scales are normalized with factor 200.
        pixel_std = 200.

        for idx, ann in enumerate(anns):
            center = np.array(ann['center'], dtype=np.float32)
            scale = np.array([ann['scale'], ann['scale']],
                             dtype=np.float32) * pixel_std

            # Adjust center/scale slightly to avoid cropping limbs
            if center[0] != -1:
                center[1] = center[1] + 15. / pixel_std * scale[1]

            # MPII uses matlab format, index is 1-based,
            # we should first convert to 0-based index
            center = center - 1

            # unify shape with coco datasets
            center = center.reshape(1, -1)
            scale = scale.reshape(1, -1)
            bbox = bbox_cs2xyxy(center, scale)

            # load keypoints in shape [1, K, 2] and keypoints_visible in [1, K]
            keypoints = np.array(ann['joints']).reshape(1, -1, 2)
            keypoints_visible = np.array(ann['joints_vis']).reshape(1, -1)

            data_info = {
                'id': ann_id,
                'img_id': int(ann['image'].split('.')[0]),
                'img_path': osp.join(self.data_prefix['img'], ann['image']),
                'bbox_center': center,
                'bbox_scale': scale,
                'bbox': bbox,
                'bbox_score': np.ones(1, dtype=np.float32),
                'keypoints': keypoints,
                'keypoints_visible': keypoints_visible,
            }

            if self.headbox_file:
                # calculate the diagonal length of head box as norm_factor
                headbox = headboxes_src[idx]
                head_size = np.linalg.norm(headbox[1] - headbox[0], axis=0)
                head_size *= SC_BIAS
                data_info['head_size'] = head_size.reshape(1, -1)

            data_list.append(data_info)
            ann_id = ann_id + 1

        return data_list
```

When supporting MPII dataset, since we need to use `head_size` to calculate `PCKh`, we add `headbox_file` to `__init__()` and override`_load_annotations()`.

### Pipeline

In a keypoint detection task, data will be transformed in three scale spaces:

- **Original Image Space:** the space where the images are stored . The sizes of different images are not necessarily the same

- **Input Image Space:** the image space used for model training. All **images** and **annotations** will be transformed into this space, such as `256x256`, `256x192`, etc.

- **Output Space:** the space used for model training, and also the scale space where model outputs are located, such as`64x64(Heatmap)`，`1x1(Regression)`, etc.

Here is a diagram to show the flow of data transformation in the three scale spaces:

![migration-en](https://user-images.githubusercontent.com/13503330/187190213-cad87b5f-0a95-4f1f-b722-15896914ded4.png)

In MMPose, the modules used for data transformations are under `$MMPOSE/mmpose/datasets/transforms`, and their workflow is shown as follows:

![transforms-en](https://user-images.githubusercontent.com/13503330/187190352-a7662346-b8da-4256-9192-c7a84b15cbb5.png)

#### Augmentation

Commonly used transforms are defined in `$MMPOSE/mmpose/datasets/transforms/common_transforms.py`, such as `RandomFlip`, `RandomHalfBody`, etc.

For top-down methods, `Shift`, `Rotate`and `Resize` are implemented by `RandomBBoxTransform`**.** For bottom-up methods, `BottomupRandomAffine` is used.

Note that most data transforms depend on `bbox_center` and `bbox_scale`, which can be obtained by `GetBBoxCenterScale`.

All transforms in this part will only generate the transformation matrix and will not perform the actual transformation on the input data.

#### Transformation

The matrix will be used to perform affine transformation on the images and annotations.

For top-down methods, it is done by `TopdownAffine` and by `BottomupRandomAffine` for bottom-up methods.

#### Encoding

After the data is transformed from the original image space into the input space, it it necessary to use `GenerateTarget` to obtain the training target(e.g. Gaussian Heatmaps). We name this process **Encoding**. Conversely, the process of getting the corresponding coordinates from Gaussian Heatmaps is called **Decoding**.

In MMPose, we collect Encoding and Decoding processes into a **Codec**, in which `encode()` and `decode()` are implemented.

Note that we unify the data format of top-down and bottom-up methods, which means that a new dimension is added to represent different instances in the same image, in shape `[batch_size, num_instances, num_keypoints, dim_coordinates]`：

- top-down：`[B, 1, K, D]`

- Bottom-up: `[B, N, K, D]`

The provided codecs are stored under `$MMPOSE/mmpose/codecs`. If you wish to customize a new codec, you can refer to \[Codec\] for more details.

#### Packing

After the data is transformed, you need to pack it by using `PackPoseInputs`.

This method converts the data stored in the dictionary `results` into the formats required for MMEngine training, such as `InstanceData`, `PixelData`, `PoseDataSample`, etc.

The packed `PoseDataSample` contains:

- Original image information：used for Evaluation

- Data in input space and output space：used for visualization in training，and calculation of loss and accuracy

- BBox information：used for transformation between different scale spaces

Here is an example of typical pipelines：

```Python
# pipelines
train_pipeline = [
    dict(type='LoadImage', file_client_args=file_client_args),
    dict(type='GetBBoxCenterScale'),
    dict(type='RandomBBoxTransform'),
    dict(type='RandomFlip', direction='horizontal'),
    dict(type='RandomHalfBody'),
    dict(type='TopdownAffine', input_size=codec['input_size']),
    dict(type='GenerateTarget', target_type='heatmap', encoder=codec),
    dict(type='PackPoseInputs')
]
test_pipeline = [
    dict(type='LoadImage', file_client_args=file_client_args),
    dict(type='GetBBoxCenterScale'),
    dict(type='TopdownAffine', input_size=codec['input_size']),
    dict(type='PackPoseInputs')
]
```

## Step3: Model

In MMPose 1.0, the model consists of the following components:

- Data Preprocessor：perform data normalization and channel transposition

- Backbone：used for feature extraction

- Neck：GAP，FPN, etc. are optional

- Head：used to implement the core algorithm and loss function

We define a base class `BasePoseEstimator` for the model under `$MMPOSE/models/pose_estimators/base.py`. All models should inherit from this base class and overload the corresponding methods.

Depending on the algorithm, MMPose classifies the models into `TopdownPoseEstimator`, `BottomupPoseEstimator`, etc. Three modes are provided in the inference:

- `mode == 'loss'`：return the result of loss function for model training

- `mode == 'predict'`：return the prediction result in the input space, used for model inference

- `mode == 'tensor'`：return the model output in the output space, i.e. model forward propagatin only, for model export

Developers should build the components by calling the corresponding registry. Taking the top-down model as an example:

```Python
@MODELS.register_module()
class TopdownPoseEstimator(BasePoseEstimator):
    def __init__(self,
                 backbone: ConfigType,
                 neck: OptConfigType = None,
                 head: OptConfigType = None,
                 train_cfg: OptConfigType = None,
                 test_cfg: OptConfigType = None,
                 data_preprocessor: OptConfigType = None,
                 init_cfg: OptMultiConfig = None):
        super().__init__(data_preprocessor, init_cfg)

        self.backbone = MODELS.build(backbone)

        if neck is not None:
            self.neck = MODELS.build(neck)

        if head is not None:
            self.head = MODELS.build(head)
```

### Data Preprocessor

Starting from MMPose 1.0, we have added data normalization and channel transposition as modules to the model, which has the advantage of further enabling end-to-end model training and prediction, allowing trained models to directly use resized images as input, without the need for users to implement the normalization preprocessing.

A typical `data_preprocessor` in the config is as follows:

```Python
data_preprocessor=dict(
        type='PoseDataPreprocessor',
        mean=[123.675, 116.28, 103.53],
        std=[58.395, 57.12, 57.375],
        bgr_to_rgb=True),
```

It will transpose the channel order of the input image from `bgr` to `rgb` and normalize the data according to `mean` and `std`.

### Backbone

MMPose provides some commonly used backbones under `$MMPOSE/mmpose/models/backbones`.

In practice, developers often use pre-trained backbone weights for transfer learning, which can improve the performance of the model on small datasets.

In MMPose, you can use the pre-trained weights by setting `init_cfg` in config:

```Python
init_cfg=dict(
    type='Pretrained',
    checkpoint='YOUR_MODEL_WEIGHTS.pth'),
```

`checkpoint` can be either a local path or a download link. Thus, if you wish to use a pre-trained model provided by Torchvision(e.g. ResNet50), you can simply use:

```Python
init_cfg=dict(
    type='Pretrained',
    checkpoint='torchvision://resnet50')
```

In addition to these commonly used backbones, you can easily use backbones from repositories in the OpenMMLab ecosystem such as MMClassification, which all share the same config system and provide pre-trained weights.

It should be emphasized that if you add a new backbone, you need to register it at:

```Python
@MODELS.register_module()
class YourBackbone(BaseBackbone):
```

Besides, import it in `$MMPOSE/mmpose/models/backbones/__init__.py`, and add it to `__all__`.

### Neck

Neck is usually a module between Backbone and Head, which is used in some algorithms. Here are some commonly used Neck:

- Global Average Pooling(GAP)

- Feature Pyramid Networks(FPN)

### Head

Generally speaking, Head is often the core of an algorithm, which is used to make predictions and perform loss calculation.

Modules related to Head in MMPose are defined in the `$MMPOSE/mmpose/models/heads` directory, and developers need to inherit the base class `BaseHead` when customizing Head and override the following methods:

- forward()

- predict()

- loss()

Specifically, the `predict()` should return the result in the input image space, so you should call `self.decode()`, which we have implemented in `BaseHead`, to decode the output. It will call the `decoder` provided by the codec to perform the decoding process.

The `loss()` not only performs the calculation of loss functions, but also the calculation of training-time metrics such as pose accuracy, and is passed through a dictionary `losses`:

```Python
 # calculate accuracy
_, avg_acc, _ = keypoint_pck_accuracy(
    pred=to_numpy(pred_coords),
    gt=to_numpy(keypoint_labels),
    mask=to_numpy(keypoint_weights) > 0,
    thr=0.05,
    norm_factor=np.ones((pred_coords.size(0), 2), dtype=np.float32))

acc_pose = torch.tensor(avg_acc, device=keypoint_labels.device)
losses.update(acc_pose=acc_pose)
```

The data of each batch is packaged into `batch_data_samples`. Taking the Regression-based method as an example, the normalized coordinates and keypoint weights can be obtained as follows:

```Python
keypoint_labels = torch.cat(
    [d.gt_instance_labels.keypoint_labels for d in batch_data_samples])
keypoint_weights = torch.cat([
    d.gt_instance_labels.keypoint_weights for d in batch_data_samples
])
```