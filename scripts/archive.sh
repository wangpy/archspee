#!/bin/bash
sudo find . -name '*.pyc' -delete
sudo find . -name '__pycache__' -delete
rm -f ../archspee.tgz
tar -pczvlf ../archspee.tgz --exclude=env *
