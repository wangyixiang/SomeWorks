# -*- coding: utf-8 -*-

import os

MSCELEBM1_DIR = "/3T/datasets/MsCelebV1/JPGFacesAligned"
LOWSHOT_DIR = "/3T/datasets/MsCelebV1/lowshot/TrainData_Base"

freebasemid_list = os.listdir(MSCELEBM1_DIR)
freebasemid_set = set(freebasemid_list)
lowshot_list = os.listdir(LOWSHOT_DIR)
lowshot_list.sort()
lowshot_set = set(lowshot_list)

freebasemid_set.difference_update(lowshot_list)
remain_list = list(freebasemid_set)
remain_list.sort()
mid_list = []
mid_file_count = 1
for i, _ in enumerate(remain_list):
    mid_list.append(remain_list[i])
    if len(mid_list) == 20000:
        with open(r"./alignedfreebasemid/mscelebm1_%d" % mid_file_count, 'w') as f:
            for _, mid in enumerate(mid_list):
                f.write(mid + "\n")
        mid_file_count += 1
        mid_list = []
else:
    if not len(mid_list) == 0:
        with open(r"./alignedfreebasemid/mscelebm1_%d" % mid_file_count, 'w') as f:
            for _, mid in enumerate(mid_list):
                f.write(mid + "\n")

with open(r"./alignedfreebasemid/mscelebm1_lowshot", 'w') as f:
    for _, mid in enumerate(lowshot_list):
        f.write(mid + "\n")