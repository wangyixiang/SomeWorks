# -*- coding: utf-8 -*-

import os
import shutil

MSCELEBM1_ROOT = r"/home/minsh/labels/mscelebm1"
ASIAN_MALE = "asian_male"
ASIAN_FEMALE = "asian_female"


categories = [ASIAN_FEMALE, ASIAN_MALE]


def is_splitable(x):
    try:
        x.rsplit("-", maxsplit=4)[1]
        return True
    except:
        return False


def put_jobs_to_check_dir(job_dir, label_categories, check_dir):
    for category_dir in label_categories:
        mid_dirs = os.listdir(os.path.join(job_dir, category_dir))
        all_job_sets = set(mid_dirs)
        stored_mids_dirs = os.listdir(os.path.join(MSCELEBM1_ROOT, category_dir))
        stored_job_sets = set(stored_mids_dirs)
        mids_to_copy = all_job_sets.difference(all_job_sets.intersection(stored_job_sets))
        for mid_dir in mids_to_copy:
            src_dir = os.path.join(job_dir, category_dir, mid_dir)
            dst_dir = os.path.join(check_dir, category_dir, mid_dir)
            if os.path.isdir(src_dir):
                shutil.copytree(src_dir, dst_dir)
            else:
                print(src_dir)


def get_result_to_git(checked_dirs, categories):
    def get_key(x):
        try:
            return int(x.rsplit("-", maxsplit=3)[1].strip())
        except Exception as exc:
            print(x)
            raise exc
    for checked_dir in checked_dirs:
        for category_dir in categories:
            mids_dir = os.listdir(os.path.join(checked_dir, category_dir))
            for mid_dir in mids_dir:
                mid_photos = os.listdir(os.path.join(checked_dir, category_dir, mid_dir))
                mid_photos = list(filter(is_splitable, mid_photos))
                mid_photos.sort(key=get_key)

                with open(os.path.join(MSCELEBM1_ROOT, category_dir, mid_dir), "w") as f:
                    for mid_photo in mid_photos:
                        f.write(os.path.join("mscelebm1", category_dir, mid_dir, mid_photo) + "\n")


DAIZL_JOB_DIR = r"/3T/intern_datasets/daizl/msdataset/category"
DAIZL_CHECK_DIR = "/3T/check_intern_job/daizl/not_exist"
# copy daizl's works to check directory
def get_daizl_jobs(job_dir=DAIZL_JOB_DIR, check_dir=DAIZL_CHECK_DIR):
    put_jobs_to_check_dir(job_dir, categories, check_dir)


def get_check_result_to_git_from_daizl(checked_dir=DAIZL_CHECK_DIR):
    get_result_to_git([checked_dir], categories)


LVJING_JOB_DIR = r"/3T/intern_datasets/lvjing/msdataset/category"
LVJING_CHECK_DIR = "/3T/check_intern_job/lvjing/not_exist"
# copy lvjing's works to check directory
def get_lvjing_jobs(job_dir=LVJING_JOB_DIR, check_dir=LVJING_CHECK_DIR):
    put_jobs_to_check_dir(job_dir, categories, check_dir)


def get_check_result_to_git_from_lvjing(checked_dir=LVJING_CHECK_DIR):
    get_result_to_git([checked_dir], categories)


def get_check_result_to_git_from_3399999(checked_dir, categories):
    get_result_to_git([checked_dir], categories)


if __name__ == "__main__":
    get_check_result_to_git_from_3399999(r"/6T/datasetgeneration", ["wangyixiang3399999"])

