在smerf的环境上测试toponet
然后将其改为mmcv高版本的，适应mambev
最后将两者整合
修改数据源
mkdir -p work_dirs/toponet

projects下建立__init__.py
touch projects/__init__.py

pip install similaritymeasures
pip install ortools==9.3.10497  openmim  iso3166  chardet

修改config里的数据路径
data_root = 'data/OpenLane-V2/OpenLane-V2_sample/'
ann_file=data_root + 'data_dict_sample_train.pkl',


在训练脚本把python路径加入
# Ensure repo root is on PYTHONPATH so `projects.*` imports work
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"

ModuleNotFoundError: No module named 'openlanev2.evaluation'
需要配置opendatalane
# pip install openlanev2==2.0.0

1.1.0版本用不了
可以把1.1.0版本的setup拷过来，然后注释掉ortools的版本需求
pip install .  (这个命令需要你文件里有这个仓库)

git clone -b v1.1.0 --depth 1 https://github.com/OpenDriveLab/OpenLane-V2.git

python -m pip install -e .

train：
./tools/dist_train.sh 1
sample占用15G显存

OpenLane-V2 Score - 0.27335537949675315
    DET_l - 0.3505411148071289
    DET_t - 0.5260204672813416
    TOP_ll - 0.0
    TOP_lt - 0.04702823179791976
F-Score for 3D Lane - 0.18971515360216024
2025-12-11 23:33:20,008 - mmdet - INFO - Exp name: toponet_r50_8x1_24e_olv2_subset_A.py
2025-12-11 23:33:20,008 - mmdet - INFO - Epoch(val) [24][64]    OpenLane-V2 Score: 0.2734, DET_l: 0.3505411148071289, DET_t: 0.5260204672813416, TOP_ll: 0.0000, TOP_lt: 0.0470

test：
也加上
# Ensure repo root is on PYTHONPATH so `projects.*` imports work
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"

sample推理占用15G显存

./tools/dist_test.sh 1 --show
2025-12-12 00:06:58,614 - mmdet - INFO - Starting openlanev2 evaluate...
calculating distances:: 100%|███████████████████| 64/64 [00:22<00:00,  2.88it/s]
OpenLane-V2 Score - 0.27335368821495765
    DET_l - 0.3505343496799469
    DET_t - 0.5260204672813416
    TOP_ll - 0.0
    TOP_lt - 0.04702823179791976
F-Score for 3D Lane - 0.18993735269718107
{'OpenLane-V2 Score': 0.27335368821495765, 'DET_l': 0.35053435, 'DET_t': 0.52602047, 'TOP_ll': 0.0, 'TOP_lt': 0.04702823179791976}

#### 补充python路径的理由：

因为 Python 不会“自动知道”你的仓库在哪儿，projects.* 这种 import 只有在「仓库根目录在 sys.path 里」时才会生效，这段代码就是在手动帮你把“仓库根目录”塞进 PYTHONPATH。

咱们一点点拆开来看。

1. Python 是怎么找模块的？

当你在代码里写：

from projects.toponet.datasets import xxx


Python 会按顺序在 sys.path 里的这些路径里去找：

import sys
print(sys.path)


里面大概会有：

当前脚本所在目录（sys.path[0]）

一些标准库路径

site-packages（装第三方库的地方）

以及环境变量 PYTHONPATH 里配置的额外路径（如果有的话）

只有当某个路径下存在这样的结构时：

<某个路径>/
  projects/
    __init__.py
    toponet/
      __init__.py
      ...


from projects.xxx import ... 才能成功。

2. 你的仓库结构 vs Python 的搜索路径

TopoNet 一般是这种结构（简化）：

REPO_ROOT/
  projects/
    toponet/
      __init__.py
      ...
  scripts/
    train.sh
    run_xxx.py


关键点：
👉 projects 这个包是在“仓库根目录”下面的，而不是在你运行脚本的当前目录下面。

但是你运行脚本的时候，常常是这样：

cd REPO_ROOT/scripts
python run_xxx.py


这时候：

sys.path[0] = REPO_ROOT/scripts

Python 会在 REPO_ROOT/scripts 下面找 projects 目录（找不到）

也不会自动去上一级目录 REPO_ROOT 里找

所以就会出现：ModuleNotFoundError: No module named 'projects' 之类的问题。

3. 那段 shell 脚本到底做了什么？
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"


逐行解释：

SCRIPT_DIR=...

得到当前这个脚本（比如 train.sh）所在的目录路径：REPO_ROOT/scripts

REPO_ROOT=...

SCRIPT_DIR/.. 就是这个目录的上一级，也就是仓库根目录 REPO_ROOT

export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"

把“仓库根目录”这个路径加到环境变量 PYTHONPATH 的最前面

这样一来，Python 启动时会把 REPO_ROOT 加入 sys.path

Python 再去 import：
就能在 REPO_ROOT/projects 下面找到 projects 包了

所以一句话总结：
👉 这几行是在告诉 Python：‘喂，我的代码包在这个仓库根目录下面，你要从这里开始找。’

不加它的话，Python 只知道你当前目录是 scripts/，不会自动往上推一层。

4. 有没有别的写法，不用每次改 PYTHONPATH？

有几种替代方案，你可以按喜好选：

✅ 方法 A：把项目“装成一个包”（推荐）

在仓库根目录执行：

conda activate smerf
pip install -e .


或者普通安装：

pip install .


只要 setup.py 或 pyproject.toml 里配置了：

packages=find_packages()


并且包含了 projects/toponet/... 这些包，那么安装后：

projects 这个包会出现在 site-packages 对应路径里；

以后在任何地方只要用这个环境运行 Python，from projects.toponet... 都能正常 import；

就不需要再手动改 PYTHONPATH 了。

✅ 方法 B：从仓库根目录用 -m 运行

比如：

cd REPO_ROOT
python -m projects.toponet.scripts.run_xxx


这样：

sys.path[0] = REPO_ROOT

仓库根目录自然在搜索路径里，projects 包能被找到。

不用改 PYTHONPATH，但命令比较长，且 必须在 REPO_ROOT 下面运行。

✅ 方法 C：每次在 shell 脚本里设 PYTHONPATH（你现在用的办法）

优点：

简单粗暴，项目不需要规范打包；

放个 train.sh，里面先 export PYTHONPATH=... 然后再 python xxx.py 就完事。

缺点：

每个脚本都要写；

换环境或别的工程时要记得同步这些设置。

#### 开始在新环境下测试：

新环境版本mambev：
mmcv==2.1.0
mmdet==3.3.0
mmdet3d==1.4.0
mmengine==0.10.4

旧环境版本toponet：没有mmengine
mmcv-full==1.5.2
mmsegmentation==0.29.1
mmdet3d==1.0.0rc6

首先找出Toponet用到mmcv的地方
在projects和train，test文件里
### bevformer:modeles
from mmcv import ConfigDict, deprecated_api_warning
from mmcv.cnn import Linear, build_activation_layer, build_norm_layer
from mmcv.runner.base_module import BaseModule, ModuleList, Sequential

from mmcv.cnn.bricks.registry import (ATTENTION, FEEDFORWARD_NETWORK, POSITIONAL_ENCODING,
                                      TRANSFORMER_LAYER, TRANSFORMER_LAYER_SEQUENCE)
from mmcv.cnn import xavier_init, constant_init
from mmcv.cnn.bricks.registry import (ATTENTION,
                                      TRANSFORMER_LAYER_SEQUENCE)
from mmcv.cnn.bricks.transformer import TransformerLayerSequence
import math
from mmcv.runner.base_module import BaseModule, ModuleList, Sequential
from mmcv.utils import (ConfigDict, build_from_cfg, deprecated_api_warning,
                        to_2tuple)

from mmcv.utils import ext_loader
from .multi_scale_deformable_attn_function import MultiScaleDeformableAttnFunction_fp32, \
    MultiScaleDeformableAttnFunction_fp16

from mmcv.cnn.bricks.registry import (ATTENTION,
                                      TRANSFORMER_LAYER,
                                      TRANSFORMER_LAYER_SEQUENCE)
from mmcv.cnn.bricks.transformer import TransformerLayerSequence
from mmcv.runner import force_fp32, auto_fp16
import mmcv
from mmcv.utils import TORCH_VERSION, digit_version
from mmcv.utils import ext_loader
ext_module = ext_loader.load_ext(
    '_ext', ['ms_deform_attn_backward', 'ms_deform_attn_forward'])

from mmcv.utils import ext_loader
ext_module = ext_loader.load_ext(
    '_ext', ['ms_deform_attn_backward', 'ms_deform_attn_forward'])


from mmcv.ops.multi_scale_deform_attn import multi_scale_deformable_attn_pytorch
from mmcv.cnn import xavier_init, constant_init
from mmcv.cnn.bricks.registry import (ATTENTION,
                                      TRANSFORMER_LAYER,
                                      TRANSFORMER_LAYER_SEQUENCE)
from mmcv.cnn.bricks.transformer import build_attention
import math
from mmcv.runner import force_fp32, auto_fp16

from mmcv.runner.base_module import BaseModule, ModuleList, Sequential

from mmcv.utils import ext_loader
from .multi_scale_deformable_attn_function import MultiScaleDeformableAttnFunction_fp32, \
    MultiScaleDeformableAttnFunction_fp16
ext_module = ext_loader.load_ext(
    '_ext', ['ms_deform_attn_backward', 'ms_deform_attn_forward'])


from mmcv.ops.multi_scale_deform_attn import multi_scale_deformable_attn_pytorch
from mmcv.cnn import xavier_init, constant_init
from mmcv.cnn.bricks.registry import ATTENTION
import math
from mmcv.runner.base_module import BaseModule, ModuleList, Sequential
from mmcv.utils import (ConfigDict, build_from_cfg, deprecated_api_warning,
                        to_2tuple)
from mmcv.utils import ext_loader
ext_module = ext_loader.load_ext(
    '_ext', ['ms_deform_attn_backward', 'ms_deform_attn_forward'])

### configs:
这个只设计调用，可能dist的写法也有不同

### toponet:
#### core:
from mmdet.core.bbox.builder import BBOX_ASSIGNERS
from mmdet.core.bbox.assigners import AssignResult
from mmdet.core.bbox.assigners import BaseAssigner
from mmdet.core.bbox.match_costs import build_match_cost
from mmdet.models.utils.transformer import inverse_sigmoid

from mmdet.core.bbox import BaseBBoxCoder
from mmdet.core.bbox.builder import BBOX_CODERS

from mmdet.core.bbox.match_costs.builder import MATCH_COST

#### datasets models utiks
from mmcv.parallel import DataContainer as DC
from mmdet.datasets.builder import PIPELINES
from mmdet.datasets.pipelines import to_tensor
from mmdet3d.datasets.pipelines import DefaultFormatBundle3D

import mmcv
from mmdet.datasets.builder import PIPELINES
from mmdet3d.datasets.pipelines import LoadAnnotations3D

from mmdet.datasets.builder import PIPELINES

import mmcv
from mmdet.datasets.builder import PIPELINES
from mmcv.parallel import DataContainer as DC

from mmcv.parallel import DataContainer as DC
from mmdet.datasets import DATASETS
from mmdet3d.datasets import Custom3DDataset

from mmcv.cnn import Linear, bias_init_with_prob, constant_init
from mmcv.runner import force_fp32
from mmdet.core import (bbox_cxcywh_to_xyxy, bbox_xyxy_to_cxcywh,
                        multi_apply, reduce_mean)
from mmdet.models.utils.transformer import inverse_sigmoid
from mmdet.models import HEADS, build_loss
from mmdet.models.dense_heads import DETRHead

import mmcv
from mmcv.cnn import Linear, bias_init_with_prob, build_activation_layer
from mmcv.cnn.bricks.transformer import build_feedforward_network
from mmcv.runner import auto_fp16, force_fp32
from mmcv.utils import TORCH_VERSION, digit_version
from mmdet.core import build_assigner, build_sampler, multi_apply, reduce_mean
from mmdet.models.builder import HEADS, build_loss
from mmdet.models.dense_heads import AnchorFreeHead
from mmdet.models.utils import build_transformer
from mmdet.models.utils.transformer import inverse_sigmoid
from mmdet3d.core.bbox.coders import build_bbox_coder

from mmcv.runner import force_fp32, auto_fp16
from mmdet.models import DETECTORS
from mmdet.models.builder import build_head
from mmdet3d.models.detectors.mvx_two_stage import MVXTwoStageDetector

from mmcv.cnn import xavier_init
from mmcv.cnn.bricks.transformer import build_transformer_layer_sequence, build_positional_encoding
from mmcv.runner.base_module import BaseModule
from mmcv.runner import force_fp32, auto_fp16
from ...utils.builder import BEV_CONSTRUCTOR
from projects.bevformer.modules.temporal_self_attention import TemporalSelfAttention
from projects.bevformer.modules.spatial_cross_attention import MSDeformableAttention3D
from projects.bevformer.modules.decoder import CustomMSDeformableAttention

from mmcv.cnn import Linear, build_activation_layer
from mmcv.cnn.bricks.drop import build_dropout 
from mmcv.cnn.bricks.registry import (TRANSFORMER_LAYER, FEEDFORWARD_NETWORK,
                                      TRANSFORMER_LAYER_SEQUENCE)
from mmcv.cnn.bricks.transformer import BaseTransformerLayer, TransformerLayerSequence
from mmcv.runner.base_module import BaseModule, ModuleList, Sequential

from mmcv.cnn import xavier_init
from mmcv.cnn.bricks.transformer import build_transformer_layer_sequence
from mmcv.runner import auto_fp16, force_fp32
from mmcv.runner.base_module import BaseModule
from mmdet.models.utils.builder import TRANSFORMER

from mmcv.utils import Registry, build_from_cfg

### tools
train:
from mmcv import Config, DictAction
from mmcv.runner import get_dist_info, init_dist

from mmdet import __version__ as mmdet_version
from mmdet3d import __version__ as mmdet3d_version
from mmdet3d.apis import init_random_seed, train_model
from mmdet3d.datasets import build_dataset
from mmdet3d.models import build_model
from mmdet3d.utils import collect_env, get_root_logger
from mmdet.apis import set_random_seed
from mmseg import __version__ as mmseg_version

test:
import mmcv
from mmcv import Config, DictAction
from mmcv.cnn import fuse_conv_bn
from mmcv.parallel import MMDataParallel, MMDistributedDataParallel
from mmcv.runner import (get_dist_info, init_dist, load_checkpoint,
                         wrap_fp16_model)
from mmcv.utils import get_logger
from mmdet.apis import multi_gpu_test, set_random_seed
from mmdet.datasets import replace_ImageToTensor
from mmdet3d.apis import single_gpu_test
from mmdet3d.datasets import build_dataloader, build_dataset
from mmdet3d.models import build_model
