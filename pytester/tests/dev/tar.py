# !/usr/bin/env python
# -*-coding: utf-8 -*-

import os
import tarfile


def tar_all_files_omit_parent_folder(source_folder, output):
    with tarfile.open(output, "w") as tar:
        for filename in os.listdir(source_folder):
            tar.add(os.path.abspath(os.path.join(source_folder, filename)), filename)
