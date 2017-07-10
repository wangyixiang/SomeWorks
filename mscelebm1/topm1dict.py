# -*- coding: utf-8 -*-

import codecs

TOPM1 = r"/3T/original_datasets/MsCelebV1/Top1M_MidList.Name.tsv"

EN_KEY = "en"
FR_KEY = "fr"
DE_KEY = "de"
ES_KEY = "es"
IT_KEY = "it"
ZH_KEY = "zh"
ZH_HANT_KEY = "zh-Hant"
JP_KEY = "jp"
KO_KEY = "ko"
TH_KEY = "th"
MS_KEY = "ms"
VI_KEY = "vi"
mid_dict = {}

with codecs.open(TOPM1, encoding="utf-8") as topfile:
    for line in topfile:
        try:
            fields = line.split("\t", 1)
            if len(fields) != 2:
                print(line)
                continue

            nc_dict = mid_dict[fields[0].strip()]
        except KeyError:
            nc_dict = mid_dict[fields[0].strip()] = {}

        nc_fields = fields[1].rsplit("@", 1)
        if len(nc_fields) != 2:
            print(line)
            continue
        nc_dict[nc_fields[1].strip()] = nc_fields[0].strip().strip('"')
