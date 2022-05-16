# Copyright (c) OpenMMLab. All rights reserved.
import mmcv
import numpy as np
import torch

from mmpose.datasets.builder import PIPELINES


@PIPELINES.register_module()
class CropValidClip:
    """Generate the clip from complete video with valid frames.

    Required keys: 'video', 'modalities', 'valid_frames', 'num_frames'.

    Modified keys: 'video', 'valid_frames', 'num_frames'.
    """

    def __init__(self):
        pass

    def __call__(self, results):
        """Crop the valid part from the video."""
        lengths = [(end - start) for start, end in results['valid_frames']]
        length = min(lengths) + 1
        for i, modality in enumerate(results['modalities']):
            start = results['valid_frames'][i][0]
            results['video'][i] = results['video'][i][start:start + length]
            results['num_frames'] = length
        del results['valid_frames']
        return results


@PIPELINES.register_module()
class RandomTemporalCrop:
    """Data augmentation with random temporal crop.

    Required keys: 'video', 'modalities', 'num_frames'.

    Modified keys: 'video', 'num_frames'.
    """

    def __init__(self, length: int = 64):
        self.length = length

    def __call__(self, results):
        """Implement data aumentation with random temporal crop."""
        diff = self.length - results['num_frames']
        start = np.random.randint(
            max(results['num_frames'] - self.length + 1, 1))
        for i, modality in enumerate(results['modalities']):
            video = results['video'][i]
            if diff > 0:
                video = np.pad(video, ((diff // 2, diff - (diff // 2)),
                                       *(((0, 0), ) * (video.ndim - 1))),
                               'edge')
            results['video'][i] = video[start:start + self.length]
        results['num_frames'] = self.length
        return results


@PIPELINES.register_module()
class ResizeGivenShortEdge:
    """Resize the video to make its short edge have given length.

    Required keys: 'video', 'modalities', 'width', 'height'.

    Modified keys: 'video', 'width', 'height'.
    """

    def __init__(self, length: int = 256):
        self.length = length

    def __call__(self, results):
        """Implement data processing with resize given short edge."""
        for i, modality in enumerate(results['modalities']):
            width, height = results['width'][i], results['height'][i]
            video = results['video'][i].transpose(1, 2, 3, 0)
            num_frames = video.shape[-1]
            video = video.reshape(height, width, -1)
            if width < height:
                width, height = self.length, int(self.length * height / width)
            else:
                width, height = int(self.length * width / height), self.length
            video = mmcv.imresize(video,
                                  (width,
                                   height)).reshape(height, width, -1,
                                                    num_frames)
            results['video'][i] = video.transpose(3, 0, 1, 2)
            results['width'][i], results['height'][i] = width, height
        return results


@PIPELINES.register_module()
class RandomAlignedSpatialCrop:
    """Data augmentation with random spatial crop for spatially aligned videos.

    Required keys: 'video', 'modalities', 'width', 'height'.

    Modified keys: 'video', 'width', 'height'.
    """

    def __init__(self, length: int = 224):
        self.length = length

    def __call__(self, results):
        """Implement data augmentation with random spatial crop."""
        assert len(set(results['height'])) == 1, \
            f"the heights {results['height']} are not identical."
        assert len(set(results['width'])) == 1, \
            f"the widths {results['width']} are not identical."
        height, width = results['height'][0], results['width'][0]
        for i, modality in enumerate(results['modalities']):
            video = results['video'][i].transpose(1, 2, 3, 0)
            num_frames = video.shape[-1]
            video = video.reshape(height, width, -1)
            start_h, start_w = np.random.randint(
                height - self.length + 1), np.random.randint(width -
                                                             self.length + 1)
            video = mmcv.imcrop(
                video,
                np.array((start_w, start_h, start_w + self.length - 1,
                          start_h + self.length - 1)))
            results['video'][i] = video.reshape(self.length, self.length, -1,
                                                num_frames).transpose(
                                                    3, 0, 1, 2)
            results['width'][i], results['height'][
                i] = self.length, self.length
        return results


@PIPELINES.register_module()
class CenterSpatialCrop:
    """Data processing by crop the center region of a video.

    Required keys: 'video', 'modalities', 'width', 'height'.

    Modified keys: 'video', 'width', 'height'.
    """

    def __init__(self, length: int = 224):
        self.length = length

    def __call__(self, results):
        """Implement data processing with center crop."""
        for i, modality in enumerate(results['modalities']):
            height, width = results['height'][i], results['width'][i]
            video = results['video'][i].transpose(1, 2, 3, 0)
            num_frames = video.shape[-1]
            video = video.reshape(height, width, -1)
            start_h, start_w = (height - self.length) // 2, (width -
                                                             self.length) // 2
            video = mmcv.imcrop(
                video,
                np.array((start_w, start_h, start_w + self.length - 1,
                          start_h + self.length - 1)))
            results['video'][i] = video.reshape(self.length, self.length, -1,
                                                num_frames).transpose(
                                                    3, 0, 1, 2)
            results['width'][i], results['height'][
                i] = self.length, self.length
        return results


@PIPELINES.register_module()
class MultiModalVideoToTensor:
    """Data processing by converting video arrays to pytorch tensors.

    Required keys: 'video', 'modalities'.

    Modified keys: 'video'.
    """

    def __init__(self):
        pass

    def __call__(self, results):
        """Implement data processing similar to ToTensor."""
        for i, modality in enumerate(results['modalities']):
            video = results['video'][i].transpose(3, 0, 1, 2)
            results['video'][i] = torch.tensor(
                np.ascontiguousarray(video), dtype=torch.float) / 255.0
        return results


@PIPELINES.register_module()
class VideoNormalizeTensor:
    """Data processing by converting video arrays to pytorch tensors.

    Required keys: 'video', 'modalities'.

    Modified keys: 'video'.
    """

    def __init__(self, mean, std):
        self.mean = torch.tensor(mean)
        self.std = torch.tensor(std)

    def __call__(self, results):
        """Implement data normalization."""
        for i, modality in enumerate(results['modalities']):
            if modality == 'rgb':
                video = results['video'][i]
                dim = video.ndim - 1
                video = video.sub(self.mean.view(3, *((1, ) * dim)))
                video = video.div(self.std.view(3, *((1, ) * dim)))
                results['video'][i] = video
        return results
