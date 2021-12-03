<div align="center">
    <img src="resources/mmpose-logo.png" width="400"/>
</div>

## Introduction

English | [简体中文](README_CN.md)

[![Documentation](https://readthedocs.org/projects/mmpose/badge/?version=latest)](https://mmpose.readthedocs.io/en/latest/?badge=latest)
[![actions](https://github.com/open-mmlab/mmpose/workflows/build/badge.svg)](https://github.com/open-mmlab/mmpose/actions)
[![codecov](https://codecov.io/gh/open-mmlab/mmpose/branch/master/graph/badge.svg)](https://codecov.io/gh/open-mmlab/mmpose)
[![PyPI](https://img.shields.io/pypi/v/mmpose)](https://pypi.org/project/mmpose/)
[![LICENSE](https://img.shields.io/github/license/open-mmlab/mmpose.svg)](https://github.com/open-mmlab/mmpose/blob/master/LICENSE)
[![Average time to resolve an issue](https://isitmaintained.com/badge/resolution/open-mmlab/mmpose.svg)](https://github.com/open-mmlab/mmpose/issues)
[![Percentage of issues still open](https://isitmaintained.com/badge/open/open-mmlab/mmpose.svg)](https://github.com/open-mmlab/mmpose/issues)

MMPose is an open-source toolbox for pose estimation based on PyTorch.
It is a part of the [OpenMMLab project](https://github.com/open-mmlab).

The master branch works with **PyTorch 1.5+**.

https://user-images.githubusercontent.com/15977946/124654387-0fd3c500-ded1-11eb-84f6-24eeddbf4d91.mp4

### Major Features

- **Support diverse tasks**

  We support a wide spectrum of mainstream pose analysis tasks in current research community, including 2d multi-person human pose estimation, 2d hand pose estimation, 2d face landmark detection, 133 keypoint whole-body human pose estimation, 3d human mesh recovery, fashion landmark detection and animal pose estimation.
  See [demo.md](demo/README.md) for more information.

- **Higher efficiency and higher accuracy**

  MMPose implements multiple state-of-the-art (SOTA) deep learning models, including both top-down & bottom-up approaches. We achieve faster training speed and higher accuracy than other popular codebases, such as [HRNet](https://github.com/leoxiaobin/deep-high-resolution-net.pytorch).
  See [benchmark.md](docs/benchmark.md) for more information.

- **Support for various datasets**

  The toolbox directly supports multiple popular and representative datasets, COCO, AIC, MPII, MPII-TRB, OCHuman etc.
  See [data_preparation.md](docs/data_preparation.md) for more information.

- **Well designed, tested and documented**

  We decompose MMPose into different components and one can easily construct a customized
  pose estimation framework by combining different modules.
  We provide detailed documentation and API reference, as well as unittests.

## [Model Zoo](https://mmpose.readthedocs.io/en/latest/modelzoo.html)

Supported algorithms:

<details open>
<summary>(click to collapse)</summary>

- [x] [DeepPose](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#deeppose-cvpr-2014) (CVPR'2014)
- [x] [CPM](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#cpm-cvpr-2016) (CVPR'2016)
- [x] [Hourglass](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#hourglass-eccv-2016) (ECCV'2016)
- [x] [MSPN](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#mspn-arxiv-2019) (ArXiv'2019)
- [x] [RSN](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#rsn-eccv-2020) (ECCV'2020)
- [x] [SimpleBaseline2D](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#simplebaseline2d-eccv-2018) (ECCV'2018)
- [x] [HRNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#hrnet-cvpr-2019) (CVPR'2019)
- [x] [HRNetv2](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#hrnetv2-tpami-2019) (TPAMI'2019)
- [x] [LiteHRNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#litehrnet-cvpr-2021) (CVPR'2021)
- [x] [SCNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#scnet-cvpr-2020) (CVPR'2020)
- [x] [Associative Embedding](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#associative-embedding-nips-2017) (NeurIPS'2017)
- [x] [HigherHRNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#higherhrnet-cvpr-2020) (CVPR'2020)
- [x] [HMR](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#hmr-cvpr-2018) (CVPR'2018)
- [x] [SimpleBaseline3D](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#simplebaseline3d-iccv-2017) (ICCV'2017)
- [x] [InterNet](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#internet-eccv-2020) (ECCV'2020)
- [x] [VideoPose3D](https://mmpose.readthedocs.io/en/latest/papers/algorithms.html#videopose3d-cvpr-2019) (CVPR'2019)
- [x] [ViPNAS](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#vipnas-cvpr-2021) (CVPR'2021)

</details>

Supported techniques:

<details open>
<summary>(click to collapse)</summary>

- [x] [Wingloss](https://mmpose.readthedocs.io/en/latest/papers/techniques.html#wingloss-cvpr-2018) (CVPR'2018)
- [x] [DarkPose](https://mmpose.readthedocs.io/en/latest/papers/techniques.html#darkpose-cvpr-2020) (CVPR'2020)
- [x] [UDP](https://mmpose.readthedocs.io/en/latest/papers/techniques.html#udp-cvpr-2020) (CVPR'2020)
- [x] [FP16](https://mmpose.readthedocs.io/en/latest/papers/techniques.html#fp16-arxiv-2017) (ArXiv'2017)
- [x] [Albumentations](https://mmpose.readthedocs.io/en/latest/papers/techniques.html#albumentations-information-2020) (Information'2020)

</details>

Supported [datasets](https://mmpose.readthedocs.io/en/latest/datasets.html):

<details open>
<summary>(click to collapse)</summary>

- [x] [COCO](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#coco-eccv-2014) \[[homepage](http://cocodataset.org/)\] (ECCV'2014)
- [x] [COCO-WholeBody](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#coco-wholebody-eccv-2020) \[[homepage](https://github.com/jin-s13/COCO-WholeBody/)\] (ECCV'2020)
- [x] [Halpe](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#halpe-cvpr-2020) \[[homepage](https://github.com/Fang-Haoshu/Halpe-FullBody/)\] (CVPR'2020)
- [x] [MPII](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#mpii-cvpr-2014) \[[homepage](http://human-pose.mpi-inf.mpg.de/)\] (CVPR'2014)
- [x] [MPII-TRB](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#mpii-trb-iccv-2019) \[[homepage](https://github.com/kennymckormick/Triplet-Representation-of-human-Body)\] (ICCV'2019)
- [x] [AI Challenger](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#ai-challenger-arxiv-2017) \[[homepage](https://github.com/AIChallenger/AI_Challenger_2017)\] (ArXiv'2017)
- [x] [OCHuman](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#ochuman-cvpr-2019) \[[homepage](https://github.com/liruilong940607/OCHumanApi)\] (CVPR'2019)
- [x] [CrowdPose](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#crowdpose-cvpr-2019) \[[homepage](https://github.com/Jeff-sjtu/CrowdPose)\] (CVPR'2019)
- [x] [PoseTrack18](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#posetrack18-cvpr-2018) \[[homepage](https://posetrack.net/users/download.php)\] (CVPR'2018)
- [x] [MHP](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#mhp-acm-mm-2018) \[[homepage](https://lv-mhp.github.io/dataset)\] (ACM MM'2018)
- [x] [sub-JHMDB](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#jhmdb-iccv-2013) \[[homepage](http://jhmdb.is.tue.mpg.de/dataset)\] (ICCV'2013)
- [x] [Human3.6M](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#human3-6m-tpami-2014) \[[homepage](http://vision.imar.ro/human3.6m/description.php)\] (TPAMI'2014)
- [x] [300W](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#300w-imavis-2016) \[[homepage](https://ibug.doc.ic.ac.uk/resources/300-W/)\] (IMAVIS'2016)
- [x] [WFLW](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#wflw-cvpr-2018) \[[homepage](https://wywu.github.io/projects/LAB/WFLW.html)\] (CVPR'2018)
- [x] [AFLW](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#aflw-iccvw-2011) \[[homepage](https://www.tugraz.at/institute/icg/research/team-bischof/lrs/downloads/aflw/)\] (ICCVW'2011)
- [x] [COFW](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#cofw-iccv-2013) \[[homepage](http://www.vision.caltech.edu/xpburgos/ICCV13/)\] (ICCV'2013)
- [x] [OneHand10K](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#onehand10k-tcsvt-2019) \[[homepage](https://www.yangangwang.com/papers/WANG-MCC-2018-10.html)\] (TCSVT'2019)
- [x] [FreiHand](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#freihand-iccv-2019) \[[homepage](https://lmb.informatik.uni-freiburg.de/projects/freihand/)\] (ICCV'2019)
- [x] [RHD](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#rhd-iccv-2017) \[[homepage](https://lmb.informatik.uni-freiburg.de/resources/datasets/RenderedHandposeDataset.en.html)\] (ICCV'2017)
- [x] [CMU Panoptic HandDB](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#cmu-panoptic-handdb-cvpr-2017) \[[homepage](http://domedb.perception.cs.cmu.edu/handdb.html)\] (CVPR'2017)
- [x] [InterHand2.6M](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#interhand2-6m-eccv-2020) \[[homepage](https://mks0601.github.io/InterHand2.6M/)\] (ECCV'2020)
- [x] [DeepFashion](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#deepfashion-cvpr-2016) \[[homepage](http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion/LandmarkDetection.html)\] (CVPR'2016)
- [x] [Animal-Pose](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#animal-pose-iccv-2019) \[[homepage](https://sites.google.com/view/animal-pose/)\] (ICCV'2019)
- [x] [AP-10K](https://arxiv.org/abs/2108.12617) \[[homepage](https://github.com/AlexTheBad/AP-10K)\] (NeurIPS'2021)
- [x] [Horse-10](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#horse-10-wacv-2021) \[[homepage](http://www.mackenziemathislab.org/horse10)\] (WACV'2021)
- [x] [MacaquePose](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#macaquepose-biorxiv-2020) \[[homepage](http://www.pri.kyoto-u.ac.jp/datasets/macaquepose/index.html)\] (bioRxiv'2020)
- [x] [Vinegar Fly](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#vinegar-fly-nature-methods-2019) \[[homepage](https://github.com/jgraving/DeepPoseKit-Data)\] (Nature Methods'2019)
- [x] [Desert Locust](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#desert-locust-elife-2019) \[[homepage](https://github.com/jgraving/DeepPoseKit-Data)\] (Elife'2019)
- [x] [Grévy’s Zebra](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#grevys-zebra-elife-2019) \[[homepage](https://github.com/jgraving/DeepPoseKit-Data)\] (Elife'2019)
- [x] [ATRW](https://mmpose.readthedocs.io/en/latest/papers/datasets.html#atrw-acm-mm-2020) \[[homepage](https://cvwc2019.github.io/challenge.html)\] (ACM MM'2020)

</details>

Supported backbones:

<details>
<summary>(click to expand)</summary>

- [x] [AlexNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#alexnet-neurips-2012) (NeurIPS'2012)
- [x] [VGG](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#vgg-iclr-2015) (ICLR'2015)
- [x] [ResNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#resnet-cvpr-2016) (CVPR'2016)
- [x] [ResNetV1D](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#resnetv1d-cvpr-2019) (CVPR'2019)
- [x] [ResNeSt](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#resnest-arxiv-2020) (ArXiv'2020)
- [x] [ResNext](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#resnext-cvpr-2017) (CVPR'2017)
- [x] [SEResNet](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#seresnet-cvpr-2018) (CVPR'2018)
- [x] [ShufflenetV1](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#shufflenetv1-cvpr-2018) (CVPR'2018)
- [x] [ShufflenetV2](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#shufflenetv2-eccv-2018) (ECCV'2018)
- [x] [MobilenetV2](https://mmpose.readthedocs.io/en/latest/papers/backbones.html#mobilenetv2-cvpr-2018) (CVPR'2018)

</details>

Results and models are available in the *README.md* of each method's config directory.
A summary can be found in the [**model zoo**](https://mmpose.readthedocs.io/en/latest/modelzoo.html) page.
We will keep up with the latest progress of the community, and support more popular algorithms and frameworks.

If you have any feature requests, please feel free to leave a comment in [Issues](https://github.com/open-mmlab/mmpose/issues/9).

## Benchmark

We demonstrate the superiority of our MMPose framework in terms of speed and accuracy on the standard COCO keypoint detection benchmark.

| Model | Input size| MMPose (s/iter) | [HRNet](https://github.com/leoxiaobin/deep-high-resolution-net.pytorch) (s/iter) | MMPose (mAP) | [HRNet](https://github.com/leoxiaobin/deep-high-resolution-net.pytorch) (mAP) |
| :--- | :---------------: | :---------------: |:--------------------: | :----------------------------: | :-----------------: |
| resnet_50  | 256x192  | **0.28** | 0.64 | **0.718** | 0.704 |
| resnet_50  | 384x288  | **0.81** | 1.24 | **0.731** | 0.722 |
| resnet_101 | 256x192  | **0.36** | 0.84 | **0.726** | 0.714 |
| resnet_101 | 384x288  | **0.79** | 1.53 | **0.748** | 0.736 |
| resnet_152 | 256x192  | **0.49** | 1.00 | **0.735** | 0.720 |
| resnet_152 | 384x288  | **0.96** | 1.65 | **0.750** | 0.743 |
| hrnet_w32  | 256x192  | **0.54** | 1.31 | **0.746** | 0.744 |
| hrnet_w32  | 384x288  | **0.76** | 2.00 | **0.760** | 0.758 |
| hrnet_w48  | 256x192  | **0.66** | 1.55 | **0.756** | 0.751 |
| hrnet_w48  | 384x288  | **1.23** | 2.20 | **0.767** | 0.763 |

More details about the benchmark are available on [benchmark.md](docs/benchmark.md).

## Inference speed summary

We show the summary of complexity information and inference speed for the major models in MMPose, including FLOPs, parameter counts and inference speeds on both CPU and GPU devices with different batch sizes.

<details open>
<summary>(click to collapse)</summary>

| Algorithm | Model | config | Input size | mAP | Flops (GFLOPs) | Params (M) | GPU Inference Speed<br>(FPS)| GPU Inference Speed<br>(FPS, bs=10) | CPU Inference Speed<br>(FPS) | CPU Inference Speed<br>(FPS, bs=10) |
| :--- | :---------------: | :-----------------: |:--------------------: | :----------------------------: | :-----------------: | :---------------: |:--------------------: | :----------------------------: | :-----------------: | :-----------------: |
| topdown_heatmap | Alexnet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/alexnet_coco_256x192.py) | (3, 192, 256) | 0.397 | 1.42 | 5.62 | 229.21 ± 16.91 | 33.52 ± 1.14 | 13.92 ± 0.60 | 1.38 ± 0.02 |
| topdown_heatmap | CPM | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/cpm_coco_256x192.py) | (3, 192, 256) | 0.623 | 63.81 | 31.3 | 11.35 ± 0.22 | 3.87 ± 0.07 | 0.31 ± 0.01 | 0.03 ± 0.00 |
| topdown_heatmap | CPM | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/cpm_coco_384x288.py) | (3, 288, 384) | 0.65 | 143.57 | 31.3 | 7.09 ± 0.14 | 2.10 ± 0.05 | 0.14 ± 0.00 | 0.01 ± 0.00 |
| topdown_heatmap | Hourglass | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hourglass52_coco_256x256.py) | (3, 256, 256) | 0.726 | 28.67 | 94.85 | 25.50 ± 1.68 | 3.99 ± 0.07 | 0.92 ± 0.03 | 0.09 ± 0.00 |
| topdown_heatmap | Hourglass | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hourglass52_coco_384x384.py) | (3, 384, 384) | 0.746 | 64.5 | 94.85 | 14.74 ± 0.8 | 1.86 ± 0.06 | 0.43 ± 0.03 | 0.04 ± 0.00 |
| topdown_heatmap | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hrnet_w32_coco_256x192.py) | (3, 192, 256) | 0.746 | 7.7 | 28.54 | 22.73 ± 1.12 | 6.60 ± 0.14 | 2.73 ± 0.11 | 0.32 ± 0.00 |
| topdown_heatmap | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hrnet_w32_coco_384x288.py) | (3, 288, 384) | 0.76 | 17.33 | 28.54 | 22.78 ± 1.21 | 3.28 ± 0.08 | 1.35 ± 0.05 | 0.14 ± 0.00 |
| topdown_heatmap | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hrnet_w48_coco_256x192.py) | (3, 192, 256) | 0.756 | 15.77 | 63.6 | 22.01 ± 1.10 | 3.74 ± 0.10 | 1.46 ± 0.05 | 0.16 ± 0.00 |
| topdown_heatmap | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/hrnet_w48_coco_384x288.py) | (3, 288, 384) | 0.767 | 35.48 | 63.6 | 15.03 ± 1.03 | 1.80 ± 0.03 | 0.68 ± 0.02 | 0.07 ± 0.00 |
| topdown_heatmap | LiteHRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/litehrnet_30_coco_256x192.py) | (3, 192, 256) | 0.675 | 0.42 | 1.76 | 11.86 ± 0.38 | 9.77 ± 0.23 | 5.84 ± 0.39 | 0.80 ± 0.00 |
| topdown_heatmap | LiteHRNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/litehrnet_30_coco_384x288.py) | (3, 288, 384) | 0.7 | 0.95 | 1.76 | 11.52 ± 0.39 | 5.18 ± 0.11 | 3.45 ± 0.22 | 0.37 ± 0.00 |
| topdown_heatmap | MobilenetV2 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/mobilenetv2_coco_256x192.py) | (3, 192, 256) | 0.646 | 1.59 | 9.57 | 91.82 ± 10.98 | 17.85 ± 0.32 | 10.44 ± 0.80 | 1.05 ± 0.01 |
| topdown_heatmap | MobilenetV2 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/mobilenetv2_coco_384x288.py) | (3, 288, 384) | 0.673 | 3.57 | 9.57 | 71.27 ± 6.82 | 8.00 ± 0.15  | 5.01 ± 0.32 | 0.46 ± 0.00 |
| topdown_heatmap | MSPN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/mspn50_coco_256x192.py) | (3, 192, 256) | 0.723 | 5.11 | 25.11 | 59.65 ± 3.74 | 9.51 ± 0.15  | 3.98 ± 0.21 | 0.43 ± 0.00 |
| topdown_heatmap | MSPN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/2xmspn50_coco_256x192.py) | (3, 192, 256) | 0.754 | 11.35 | 56.8 | 30.64 ± 2.61 | 4.74 ± 0.12 | 1.85 ± 0.08 | 0.20 ± 0.00 |
| topdown_heatmap | MSPN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/3xmspn50_coco_256x192.py) | (3, 192, 256) | 0.758 | 17.59 | 88.49 | 20.90 ± 1.82 | 3.22 ± 0.08 | 1.23 ± 0.04 | 0.13 ± 0.00 |
| topdown_heatmap | MSPN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/4xmspn50_coco_256x192.py) | (3, 192, 256) | 0.764 | 23.82 | 120.18 | 15.79 ± 1.14  | 2.45 ± 0.05 | 0.90 ± 0.03 | 0.10 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest50_coco_256x192.py) | (3, 192, 256) | 0.721 | 6.73 | 35.93 | 48.36 ± 4.12 | 7.48 ± 0.13 | 3.00 ± 0.13 | 0.33 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest50_coco_384x288.py) | (3, 288, 384) | 0.737 | 15.14 | 35.93 | 30.30 ± 2.30 | 3.62 ± 0.09 | 1.43 ± 0.05 | 0.13 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest101_coco_256x192.py) | (3, 192, 256) | 0.725 | 10.38 | 56.61 | 29.21 ± 1.98 | 5.30 ± 0.12 | 2.01 ± 0.08 | 0.22 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest101_coco_384x288.py) | (3, 288, 384) | 0.746 | 23.36 | 56.61 | 19.02 ± 1.40 | 2.59 ± 0.05  | 0.97 ± 0.03 | 0.09 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest200_coco_256x192.py) | (3, 192, 256) | 0.732 | 17.5 | 78.54 | 16.11 ± 0.71 | 3.29 ± 0.07  | 1.33 ± 0.02 | 0.14 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest200_coco_384x288.py) | (3, 288, 384) | 0.754 | 39.37 | 78.54 | 11.48 ± 0.68 | 1.58 ± 0.02 | 0.63 ± 0.01 | 0.06 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest269_coco_256x192.py) | (3, 192, 256) | 0.738 | 22.45 | 119.27 | 12.02 ± 0.47 | 2.60 ± 0.05 | 1.03 ± 0.01 | 0.11 ± 0.00 |
| topdown_heatmap | ResNest | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnest269_coco_384x288.py) | (3, 288, 384) | 0.755 | 50.5 | 119.27 | 8.82 ± 0.42  | 1.24 ± 0.02 | 0.49 ± 0.01 | 0.05 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res50_coco_256x192.py) | (3, 192, 256) | 0.718 | 5.46 | 34 | 64.23 ± 6.05 | 9.33 ± 0.21 | 4.00 ± 0.10 | 0.41 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res50_coco_384x288.py) | (3, 288, 384) | 0.731 | 12.29 | 34 | 36.78 ± 3.05 | 4.48 ± 0.12 | 1.92 ± 0.04 | 0.19 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res101_coco_256x192.py) | (3, 192, 256) | 0.726 | 9.11 | 52.99 | 43.35 ± 4.36 | 6.44 ± 0.14 | 2.57 ± 0.05 | 0.27 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res101_coco_384x288.py) | (3, 288, 384) | 0.748 | 20.5 | 52.99 | 23.29 ± 1.83 | 3.12 ± 0.09 | 1.23 ± 0.03 | 0.11 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res152_coco_256x192.py) | (3, 192, 256) | 0.735 | 12.77 | 68.64 | 32.31 ± 2.84 | 4.88 ± 0.17 | 1.89 ± 0.03 | 0.20 ± 0.00 |
| topdown_heatmap | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/res152_coco_384x288.py) | (3, 288, 384) | 0.75 | 28.73 | 68.64 | 17.32 ± 1.17 | 2.40 ± 0.04 | 0.91 ± 0.01 | 0.08 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d50_coco_256x192.py) | (3, 192, 256) | 0.722 | 5.7 | 34.02 | 63.44 ± 6.09 | 9.09 ± 0.10 | 3.82 ± 0.10 | 0.39 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d50_coco_384x288.py) | (3, 288, 384) | 0.73 | 12.82 | 34.02 | 36.21 ± 3.10 | 4.30 ± 0.12 | 1.82 ± 0.04 | 0.16 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d101_coco_256x192.py) | (3, 192, 256) | 0.731 | 9.35 | 53.01 | 41.48 ± 3.76 | 6.33 ± 0.15 | 2.48 ± 0.05 | 0.26 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d101_coco_384x288.py) | (3, 288, 384) | 0.748 | 21.04 | 53.01 | 23.49 ± 1.76 | 3.07 ± 0.07 | 1.19 ± 0.02 | 0.11 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d152_coco_256x192.py) | (3, 192, 256) | 0.737 | 13.01 | 68.65 | 31.96 ± 2.87 | 4.69 ± 0.18 | 1.87 ± 0.02 | 0.19 ± 0.00 |
| topdown_heatmap | ResNetV1d | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnetv1d152_coco_384x288.py) | (3, 288, 384) | 0.752 | 29.26 | 68.65 | 17.31 ± 1.13 | 2.32 ± 0.04 | 0.88 ± 0.01 | 0.08 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext50_coco_256x192.py) | (3, 192, 256) | 0.714 | 5.61 | 33.47 | 48.34 ± 3.85 | 7.66 ± 0.13 | 3.71 ± 0.10 | 0.37 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext50_coco_384x288.py) | (3, 288, 384) | 0.724 | 12.62 | 33.47 | 30.66 ± 2.38 | 3.64 ± 0.11 | 1.73 ± 0.03 | 0.15 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext101_coco_256x192.py) | (3, 192, 256) | 0.726 | 9.29 | 52.62 | 27.33 ± 2.35 | 5.09 ± 0.13 | 2.45 ± 0.04 | 0.25 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext101_coco_384x288.py) | (3, 288, 384) | 0.743 | 20.91 | 52.62 | 18.19 ± 1.38  | 2.42 ± 0.04 | 1.15 ± 0.01 | 0.10 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext152_coco_256x192.py) | (3, 192, 256) | 0.73 | 12.98 | 68.39 | 19.61 ± 1.61 | 3.80 ± 0.13 | 1.83 ± 0.02 | 0.18 ± 0.00 |
| topdown_heatmap | ResNext | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/resnext152_coco_384x288.py) | (3, 288, 384) | 0.742 | 29.21 | 68.39 | 13.14 ± 0.75 | 1.82 ± 0.03 | 0.85 ± 0.01 | 0.08 ± 0.00 |
| topdown_heatmap | RSN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/rsn18_coco_256x192.py) | (3, 192, 256) | 0.704 | 2.27 | 9.14 | 47.80 ± 4.50 | 13.68 ± 0.25 | 6.70 ± 0.28 | 0.70 ± 0.00 |
| topdown_heatmap | RSN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/rsn50_coco_256x192.py) | (3, 192, 256) | 0.723 | 4.11 | 19.33 | 27.22 ± 1.61 | 8.81 ± 0.13 | 3.98 ± 0.12 | 0.45 ± 0.00 |
| topdown_heatmap | RSN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/2xrsn50_coco_256x192.py) | (3, 192, 256) | 0.745 | 8.29 | 39.26 | 13.88 ± 0.64 | 4.78 ± 0.13 | 2.02 ± 0.04 | 0.23 ± 0.00 |
| topdown_heatmap | RSN | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/3xrsn50_coco_256x192.py) | (3, 192, 256) | 0.75 | 12.47 | 59.2 | 9.40 ± 0.32 | 3.37 ± 0.09 | 1.34 ± 0.03 | 0.15 ± 0.00 |
| topdown_heatmap | SCNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/scnet50_coco_256x192.py) | (3, 192, 256) | 0.728 | 5.31 | 34.01 | 40.76 ± 3.08 | 8.35 ± 0.19 | 3.82 ± 0.08 | 0.40 ± 0.00 |
| topdown_heatmap | SCNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/scnet50_coco_384x288.py) | (3, 288, 384) | 0.751 | 11.94 | 34.01 | 32.61 ± 2.97 | 4.19 ± 0.10 | 1.85 ± 0.03 | 0.17 ± 0.00 |
| topdown_heatmap | SCNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/scnet101_coco_256x192.py) | (3, 192, 256) | 0.733 | 8.51 | 53.01 | 24.28 ± 1.19 | 5.80 ± 0.13 | 2.49 ± 0.05 | 0.27 ± 0.00  |
| topdown_heatmap | SCNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/scnet101_coco_384x288.py) | (3, 288, 384) | 0.752 | 19.14 | 53.01 | 20.43 ± 1.76 | 2.91 ± 0.06 | 1.23 ± 0.02 | 0.12 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet50_coco_256x192.py) | (3, 192, 256) | 0.728 | 5.47 | 36.53 | 54.83 ± 4.94 | 8.80 ± 0.12 | 3.85 ± 0.10 | 0.40 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet50_coco_384x288.py) | (3, 288, 384) | 0.748 | 12.3 | 36.53 | 33.00 ± 2.67 | 4.26 ± 0.12 | 1.86 ± 0.04 | 0.17 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet101_coco_256x192.py) | (3, 192, 256) | 0.734 | 9.13 | 57.77 | 33.90 ± 2.65 | 6.01 ± 0.13 | 2.48 ± 0.05 | 0.26 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet101_coco_384x288.py) | (3, 288, 384) | 0.753 | 20.53 | 57.77 | 20.57 ± 1.57 | 2.96 ± 0.07 | 1.20 ± 0.02 | 0.11 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet152_coco_256x192.py) | (3, 192, 256) | 0.73 | 12.79 | 75.26 | 24.25 ± 1.95 | 4.45 ± 0.10 | 1.82 ± 0.02 | 0.19 ± 0.00 |
| topdown_heatmap | SeresNet | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/seresnet152_coco_384x288.py) | (3, 288, 384) | 0.753 | 28.76 | 75.26 | 15.11 ± 0.99  | 2.25 ± 0.04 | 0.88 ± 0.01 | 0.08 ± 0.00 |
| topdown_heatmap | ShuffleNetV1 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/shufflenetv1_coco_256x192.py) | (3, 192, 256) | 0.585 | 1.35 | 6.94 | 80.79 ± 8.95 | 21.91 ± 0.46 | 11.84 ± 0.59 | 1.25 ± 0.01 |
| topdown_heatmap | ShuffleNetV1 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/shufflenetv1_coco_384x288.py) | (3, 288, 384) | 0.622 | 3.05 | 6.94 | 63.45 ± 5.21 | 9.84 ± 0.10 | 6.01 ± 0.31 | 0.57 ± 0.00 |
| topdown_heatmap | ShuffleNetV2 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/shufflenetv2_coco_256x192.py) | (3, 192, 256) | 0.599 | 1.37 | 7.55 | 82.36 ± 7.30 | 22.68 ± 0.53 | 12.40 ± 0.66 | 1.34 ± 0.02 |
| topdown_heatmap | ShuffleNetV2 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/shufflenetv2_coco_384x288.py) | (3, 288, 384) | 0.636 | 3.08 | 7.55 | 63.63 ± 5.72 | 10.47 ± 0.16 | 6.32 ± 0.28 | 0.63 ± 0.01  |
| topdown_heatmap | VGG | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/vgg16_bn_coco_256x192.py) | (3, 192, 256) | 0.698 | 16.22 | 18.92 | 51.91 ± 2.98 | 6.18 ± 0.13 | 1.64 ± 0.03 | 0.15 ± 0.00 |
| topdown_heatmap | VIPNAS + Res50 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/vipnas_res50_coco_256x192.py) | (3, 192, 256) | 0.711 | 1.49 | 7.29 | 34.88 ± 2.45 | 10.29 ± 0.13 | 6.51 ± 0.17 | 0.65 ± 0.00 |
| topdown_heatmap | VIPNAS + MobileNetV3 | [config](/configs/body/2d_kpt_sview_rgb_img/topdown_heatmap/coco/vipnas_mbv3_coco_256x192.py) | (3, 192, 256) | 0.7 | 0.76 | 5.9 | 53.62 ± 6.59 | 11.54 ± 0.18 | 1.26 ± 0.02 | 0.13 ± 0.00 |
| Associative Embedding | HigherHRNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/higherhrnet_w32_coco_512x512.py) | (3, 512, 512) | 0.677 | 46.58 | 28.65 | 7.80 ± 0.67 | / | 0.28 ± 0.02 | / |
| Associative Embedding | HigherHRNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/higherhrnet_w32_coco_640x640.py) | (3, 640, 640) | 0.686 | 72.77 | 28.65 | 5.30 ± 0.37 | / | 0.17 ± 0.01 | / |
| Associative Embedding | HigherHRNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/higherhrnet_w48_coco_512x512.py) | (3, 512, 512) | 0.686 | 96.17 | 63.83 | 4.55 ± 0.35 | / | 0.15 ± 0.01 | / |
| Associative Embedding | Hourglass | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/hourglass_ae_coco_512x512.py) | (3, 512, 512) | 0.613 | 221.58 | 138.86 | 3.55 ± 0.24 | / | 0.08 ± 0.00 | / |
| Associative Embedding | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/hrnet_w32_coco_512x512.py) | (3, 512, 512) | 0.654 | 41.1 | 28.54 | 8.93 ± 0.76 | / | 0.33 ± 0.02 | / |
| Associative Embedding | HRNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/hrnet_w48_coco_512x512.py) | (3, 512, 512) | 0.665 | 84.12 | 63.6 | 5.27 ± 0.43 | / | 0.18 ± 0.01 | / |
| Associative Embedding | MobilenetV2 | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/mobilenetv2_coco_512x512.py) | (3, 512, 512) | 0.38 | 8.54 | 9.57 | 21.24 ± 1.34 | / | 0.81 ± 0.06 | / |
| Associative Embedding | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/res50_coco_512x512.py) | (3, 512, 512) | 0.466 | 29.2 | 34 | 11.71 ± 0.97 | / | 0.41 ± 0.02 | / |
| Associative Embedding | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/res50_coco_640x640.py) | (3, 640, 640) | 0.479 | 45.62 | 34 | 8.20 ± 0.58 | / | 0.26 ± 0.02 | / |
| Associative Embedding | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/res101_coco_512x512.py) | (3, 512, 512) | 0.554 | 48.67 | 53 | 8.26 ± 0.68 | / | 0.28 ± 0.02 | / |
| Associative Embedding | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/associative_embedding/coco/res152_coco_512x512.py) | (3, 512, 512) | 0.595 | 68.17 | 68.64 | 6.25 ± 0.53 | / | 0.21 ± 0.01 | / |
| DeepPose | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/deeppose/coco/res50_coco_256x192.py) | (3, 192, 256) | 0.526 | 4.04 | 23.58 | 82.20 ± 7.54 | / | 5.50 ± 0.18 | / |
| DeepPose | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/deeppose/coco/res101_coco_256x192.py) | (3, 192, 256) | 0.56 | 7.69 | 42.57 | 48.93 ± 4.02 | / | 3.10 ± 0.07 | / |
| DeepPose | ResNet | [config](/configs/body/2d_kpt_sview_rgb_img/deeppose/coco/res152_coco_256x192.py) | (3, 192, 256) | 0.583 | 11.34 | 58.21 | 35.06 ± 3.50 | / | 2.19 ± 0.04 | / |

</details>

More details about the inference speed summary are available on [inference_speed_summary.md](docs/inference_speed_summary.md).

## Installation

Please refer to [install.md](docs/install.md) for installation.

## Data Preparation

Please refer to [data_preparation.md](docs/data_preparation.md) for a general knowledge of data preparation.

## Get Started

Please see [getting_started.md](docs/getting_started.md) for the basic usage of MMPose.
There are also tutorials:

- [learn about configs](docs/tutorials/0_config.md)
- [finetune model](docs/tutorials/1_finetune.md)
- [add new dataset](docs/tutorials/2_new_dataset.md)
- [customize data pipelines](docs/tutorials/3_data_pipeline.md)
- [add new modules](docs/tutorials/4_new_modules.md)
- [export a model to ONNX](docs/tutorials/5_export_model.md)
- [customize runtime settings](docs/tutorials/6_customize_runtime.md)

## FAQ

Please refer to [FAQ](docs/faq.md) for frequently asked questions.

## License

This project is released under the [Apache 2.0 license](LICENSE).

## Citation

If you find this project useful in your research, please consider cite:

```bibtex
@misc{mmpose2020,
    title={OpenMMLab Pose Estimation Toolbox and Benchmark},
    author={MMPose Contributors},
    howpublished = {\url{https://github.com/open-mmlab/mmpose}},
    year={2020}
}
```

## Contributing

We appreciate all contributions to improve MMPose. Please refer to [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the contributing guideline.

## Acknowledgement

MMPose is an open source project that is contributed by researchers and engineers from various colleges and companies.
We appreciate all the contributors who implement their methods or add new features, as well as users who give valuable feedbacks.
We wish that the toolbox and benchmark could serve the growing research community by providing a flexible toolkit to reimplement existing methods and develop their own new models.

## Projects in OpenMMLab

- [MMCV](https://github.com/open-mmlab/mmcv): OpenMMLab foundational library for computer vision.
- [MIM](https://github.com/open-mmlab/mim): MIM Installs OpenMMLab Packages.
- [MMClassification](https://github.com/open-mmlab/mmclassification): OpenMMLab image classification toolbox and benchmark.
- [MMDetection](https://github.com/open-mmlab/mmdetection): OpenMMLab detection toolbox and benchmark.
- [MMDetection3D](https://github.com/open-mmlab/mmdetection3d): OpenMMLab next-generation platform for general 3D object detection.
- [MMSegmentation](https://github.com/open-mmlab/mmsegmentation): OpenMMLab semantic segmentation toolbox and benchmark.
- [MMAction2](https://github.com/open-mmlab/mmaction2): OpenMMLab next-generation action understanding toolbox and benchmark.
- [MMTracking](https://github.com/open-mmlab/mmtracking): OpenMMLab video perception toolbox and benchmark.
- [MMPose](https://github.com/open-mmlab/mmpose): OpenMMLab pose estimation toolbox and benchmark.
- [MMEditing](https://github.com/open-mmlab/mmediting): OpenMMLab image and video editing toolbox.
- [MMOCR](https://github.com/open-mmlab/mmocr): A Comprehensive Toolbox for Text Detection, Recognition and Understanding.
- [MMGeneration](https://github.com/open-mmlab/mmgeneration): OpenMMLab next-generation toolbox for generative models.
