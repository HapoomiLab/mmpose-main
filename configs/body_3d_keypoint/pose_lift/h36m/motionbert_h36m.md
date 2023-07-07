<!-- [BACKBONE] -->

<details>
<summary align="right"><a href="https://arxiv.org/abs/2210.06551">MotionBERT (2022)</a></summary>

```bibtex
 @misc{Zhu_Ma_Liu_Liu_Wu_Wang_2022,
 title={Learning Human Motion Representations: A Unified Perspective},
 author={Zhu, Wentao and Ma, Xiaoxuan and Liu, Zhaoyang and Liu, Libin and Wu, Wayne and Wang, Yizhou},
 year={2022},
 month={Oct},
 language={en-US}
 }
```

</details>

<!-- [DATASET] -->

<details>
<summary align="right"><a href="https://ieeexplore.ieee.org/abstract/document/6682899/">Human3.6M (TPAMI'2014)</a></summary>

```bibtex
@article{h36m_pami,
author = {Ionescu, Catalin and Papava, Dragos and Olaru, Vlad and Sminchisescu, Cristian},
title = {Human3.6M: Large Scale Datasets and Predictive Methods for 3D Human Sensing in Natural Environments},
journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
publisher = {IEEE Computer Society},
volume = {36},
number = {7},
pages = {1325-1339},
month = {jul},
year = {2014}
}
```

</details>

Testing results on Human3.6M dataset with ground truth 2D detections

| Arch                                                                                    | MPJPE | average MPJPE | P-MPJPE |                                           ckpt                                           |
| :-------------------------------------------------------------------------------------- | :---: | :-----------: | :-----: | :--------------------------------------------------------------------------------------: |
| [MotionBERT\*](/configs/body_3d_keypoint/pose_lift/h36m/pose-lift_motionbert-243frm_8xb32-120e_h36m.py) | 35.3  |     35.3      |  27.7   | [ckpt](https://download.openmmlab.com/mmpose/v1/body_3d_keypoint/pose_lift/h36m/motionbert_h36m-f554954f_20230531.pth) |
| [MotionBERT-finetuned\*](/configs/body_3d_keypoint/pose_lift/h36m/pose-lift_motionbert-243frm_8xb32-120e_h36m.py) | 27.5  |     27.4      |  21.6   | [ckpt](https://download.openmmlab.com/mmpose/v1/body_3d_keypoint/pose_lift/h36m/motionbert_ft_h36m-d80af323_20230531.pth) |

Testing results on Human3.6M dataset from the [official repo](https://github.com/Walter0807/MotionBERT) with ground truth 2D detections

| Arch                                                                                    | MPJPE | average MPJPE | P-MPJPE |                                           ckpt                                           |
| :-------------------------------------------------------------------------------------- | :---: | :-----------: | :-----: | :--------------------------------------------------------------------------------------: |
| [MotionBERT\*](/configs/body_3d_keypoint/pose_lift/h36m/pose-lift_motionbert-243frm_8xb32-120e_h36m.py) | 40.5  |     39.9      |  34.1   | [ckpt](https://download.openmmlab.com/mmpose/v1/body_3d_keypoint/pose_lift/h36m/motionbert_h36m-f554954f_20230531.pth) |
| [MotionBERT-finetuned\*](/configs/body_3d_keypoint/pose_lift/h36m/pose-lift_motionbert-243frm_8xb32-120e_h36m.py) | 38.2  |     37.7      |  32.6   | [ckpt](https://download.openmmlab.com/mmpose/v1/body_3d_keypoint/pose_lift/h36m/motionbert_ft_h36m-d80af323_20230531.pth) |

*Models with * are converted from the [official repo](https://github.com/Walter0807/MotionBERT). The config files of these models are only for validation. We don't ensure these config files' training accuracy and welcome you to contribute your reproduction results.*
