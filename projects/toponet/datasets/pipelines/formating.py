#---------------------------------------------------------------------------------------#
# Graph-based Topology Reasoning for Driving Scenes (https://arxiv.org/abs/2304.05277)  #
# Source code: https://github.com/OpenDriveLab/TopoNet                                  #
# Copyright (c) OpenDriveLab. All rights reserved.                                      #
#---------------------------------------------------------------------------------------#

import numpy as np
# from mmcv.parallel import DataContainer as DC
# from mmdet.datasets.builder import PIPELINES
# from mmdet.datasets.pipelines import to_tensor
# from mmdet3d.datasets.pipelines import DefaultFormatBundle3D


from mmdet3d.registry import TRANSFORMS
from mmdet.datasets.transforms import to_tensor
from mmdet3d.datasets.pipelines import DefaultFormatBundle3D


# @PIPELINES.register_module()
@TRANSFORMS.register_module()
class CustomFormatBundle3DLane(DefaultFormatBundle3D):
    """Custom formatting bundle for 3D Lane.
    """

    def __init__(self, class_names, **kwargs):
        super(CustomFormatBundle3DLane, self).__init__(class_names, **kwargs)

    def transform(self, results):
        """Call function to transform and format common fields in results.

        Args:
            results (dict): Result dict contains the data to convert.

        Returns:
            dict: The result dict contains the data that is formatted with
                default bundle.
        """
        if 'gt_lanes_3d' in results:
            results['gt_lanes_3d'] = to_tensor(results['gt_lanes_3d'])
        if 'gt_lane_labels_3d' in results:
            results['gt_lane_labels_3d'] = to_tensor(results['gt_lane_labels_3d'])
        if 'gt_lane_adj' in results:
            results['gt_lane_adj'] = to_tensor(results['gt_lane_adj'])
        if 'gt_lane_lcte_adj' in results:
            results['gt_lane_lcte_adj'] = to_tensor(results['gt_lane_lcte_adj'])
        results = super(CustomFormatBundle3DLane, self).transform(results)
        return results

    def __repr__(self):
        """str: Return a string that describes the module."""
        repr_str = self.__class__.__name__
        repr_str += f'(class_names={self.class_names}, '
        repr_str += f'with_gt={self.with_gt}, with_label={self.with_label})'
        return repr_str
