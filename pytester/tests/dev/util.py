# !/usr/bin/env python
# -*-coding: utf-8 -*-
import shutil
import os


def copy_folder(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def delete_folder(path):
    shutil.rmtree(path)
