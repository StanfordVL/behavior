#!/usr/bin/env bash

DOCKER_NAME="my_submission"
DATASET_PATH="/tmp"

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


docker run -v ${DATASET_PATH}/igibson.key:/opt/iGibson/igibson/data/igibson.key -v ${DATASET_PATH}/ig_dataset:/opt/iGibson/igibson/data/ig_dataset \
    \
    ${DOCKER_NAME} \
    /bin/bash -c \
    "export CONFIG_FILE=/opt/behavior/behavior/configs/behavior_onboard_sensing.yaml; export SPLIT=minival; cd /opt/iGibson/igibson/examples/learning/; python stable_baselines3_example.py"

# for older docker versions, use --runtime=nvidia instead of --gpus=all