#!/usr/bin/env bash
set -x

timestamp=`date +"%y%m%d.%H%M%S"`

WORK_DIR=work_dirs/toponet
CONFIG=projects/configs/toponet_r50_8x1_24e_olv2_subset_A.py

CHECKPOINT=${WORK_DIR}/latest.pth

GPUS=$1
PORT=${PORT:-28510}

# Ensure repo root is on PYTHONPATH so `projects.*` imports work
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH}"


python -m torch.distributed.run --nproc_per_node=$GPUS --master_port=$PORT \
    tools/test.py $CONFIG $CHECKPOINT --launcher pytorch \
    --out-dir ${WORK_DIR}/test --eval openlane_v2 ${@:2} \
    2>&1 | tee ${WORK_DIR}/test.${timestamp}.log
