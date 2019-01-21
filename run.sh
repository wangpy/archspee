#!/bin/bash
source $PWD/env/bin/activate
python --version
export PYTHONPATH=$PWD:$PWD/third_party/snowboy:$PWD/third_party/pixels
python archspee/main.py
