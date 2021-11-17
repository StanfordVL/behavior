#!/usr/bin/env bash

DOCKER_NAME="my_submission"

while [[ $# -gt 0 ]]
do
key="${1}"

case $key in
      --docker-name)
      shift
      DOCKER_NAME="${1}"
      echo ${DOCKER_NAME}
      shift
      ;;
      --dataset-path)
      shift
      DATASET_PATH="${1}"
      echo ${DATASET_PATH}
      shift
      ;;
    *) # unknown arg
      echo unknown arg ${1}
      exit
      ;;
esac
done


docker run -v ${DATASET_PATH}/igibson.key:/opt/iGibson/igibson/data/igibson.key -v ${DATASET_PATH}/ig_dataset:/opt/iGibson/igibson/data/ig_dataset -v $(pwd)/results:/results \
    --gpus=all \
    ${DOCKER_NAME} \
    /bin/bash -c \
    "export CONFIG_FILE=/opt/iGibson/igibson/examples/configs/behavior_onboard_sensing.yaml; export SPLIT=minival; export OUTPUT_DIR=/results; bash submission.sh"

# for older docker versions, use --runtime=nvidia instead of --gpus=all