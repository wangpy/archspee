#!/bin/bash
if [[ -z "${DISPLAY}" ]]; then
  export DISPLAY=:0
fi
source $PWD/env/bin/activate
python --version
export PYTHONPATH=$PWD:$PWD/third_party/snowboy:$PWD/third_party/pixels
python archspee/main.py
