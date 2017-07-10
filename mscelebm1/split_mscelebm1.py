# -*- coding: utf-8 -*-

import os

SRC_DIR = r"/3T/intern_datasets/JPGFacesAligned"
DST_DIR = r"/3T/intern_datasets/mscelebm1/"
ALIGNED_MID_DIR = r"alignedfreebasemid"

for mid_filename in ["mscelebm1_1", "mscelebm1_2", "mscelebm1_3", "mscelebm1_4"]:
    with open(os.path.join(ALIGNED_MID_DIR, mid_filename)) as midfile:
        for line in midfile:
            if len(line.strip()) != 0:
                try:
                    os.rename(os.path.join(SRC_DIR, line.strip()), os.path.join(DST_DIR, mid_filename, line.strip()))
                except OSError:
                    print("wrong with ", os.path.join(SRC_DIR, line.strip()))