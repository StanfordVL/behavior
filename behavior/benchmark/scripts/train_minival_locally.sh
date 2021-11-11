#!/usr/bin/env bash

DOCKER_NAME="my_submission"

while [[ $# -gt 0 ]]
do
key="${1}"

case $key in
      --docker-name)
      shift
      DOCKER_NAME="${1}"
      shift
      ;;
    *) # unknown arg
      echo unkown arg ${1}
      exit
      ;;
esac
done


docker run -v $(pwd)/igibson.key:/opt/iGibson/igibson/data/igibson.key -v $(pwd)/ig_dataset:/opt/iGibson/igibson/data/ig_dataset \
    --gpus=all \
    ${DOCKER_NAME} \
    /bin/bash -c \
    "export CONFIG_FILE=/opt/iGibson/igibson/examples/configs/behavior_onboard_sensing.yaml; export SPLIT=minival; cd /opt/iGibson/igibson/examples/demo; python stable_baselines3_behavior_example.py"

# for older docker versions, use --runtime=nvidia instead of --gpus=all