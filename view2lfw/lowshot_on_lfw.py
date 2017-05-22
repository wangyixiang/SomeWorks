import argparse
import sys
import numpy as np
import dlib
from skimage import io
import time
from sklearn import metrics
from scipy.optimize import brentq
from scipy import interpolate

import lfw


def main(args):
    pairs_file = r"./pairs.txt"
    lfw_dir = r"./lfw-deepfunneled"
    # pairs_file = r"C:\sources\PycharmProjects\facenet\data\pairs.txt"
    # lfw_dir = r"D:\datasets\lfw\lfw-deepfunneled"
    pairs = lfw.read_pairs(pairs_file)
    lfw_paths, same_list = lfw.get_paths(lfw_dir, pairs, "jpg")
    embedding_list, real_same_list = dlib_generate_embedding(lfw_paths, same_list)
    tpr, fpr, accuracy = evaluate(embedding_list, real_same_list)
    print('Accuracy: %1.3f+-%1.3f' % (np.mean(accuracy), np.std(accuracy)))

    auc = metrics.auc(fpr, tpr)
    print('Area Under Curve (AUC): %1.3f' % auc)
    # eer = brentq(lambda x: 1. - x - interpolate.interp1d(fpr, tpr)(x), 0., 1.)
    # print('Equal Error Rate (EER): %1.3f' % eer)


def parse_args():
    parser = argparse.ArgumentParser()

    return parser.parse_args(sys.argv[1:])


def dlib_generate_embedding(image_paths, actual_issame, embedding_size=128):
    predictor_dat_path = r"./shape_predictor_68_face_landmarks.dat"
    face_rec_dat_path = r"./orig_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./1000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./4000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./10000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./20000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./origplus20000_dlib_face_recognition_resnet_model_v1.dat"
    # predictor_dat_path = r"C:\sources\dlib\examples\build\Release\shape_predictor_68_face_landmarks.dat"
    # face_rec_dat_path = r"C:\sources\dlib\examples\build\Release\orig_dlib_face_recognition_resnet_model_v1.dat"

    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_dat_path)
    face_rec = dlib.face_recognition_model_v1(face_rec_dat_path)
    embedding_list = []
    non_only_one_list = []

    for i, img_path in enumerate(image_paths):
        img = io.imread(img_path)
        dets = detector(img, 1)
        if i % 1000 == 0:
            print(i, time.asctime(time.localtime(time.time())))
        if len(dets) != 1:
            # print('%s failed on face detection, please check it.' % img_path)
            # If we can't detect only one face, we temporarily don't need it.
            non_only_one_list.append(i)
            embedding_list.append(None)
            continue
        shape = shape_predictor(img, dets[0])
        face_embedding = face_rec.compute_face_descriptor(img, shape)
        embedding_list.append(np.array(face_embedding))

    non_only_one_list.reverse()
    print("skip %i pairs" % len(non_only_one_list))
    for _, del_id in enumerate(non_only_one_list):
        # !!! be careful here. !!!
        # 1) we are using python 2 here, python 3 will NOT handle the following as we need.
        # 2) the order is important on manipulating the list.
        real_id = del_id / 2
        del actual_issame[real_id]
        del embedding_list[real_id*2 + 1]
        del embedding_list[real_id*2]

    return embedding_list, actual_issame

def evaluate(embedding_list, actual_issame, nrof_folds=10):
    # Calculate evaluation metrics
    embeddings = np.asarray(embedding_list)
    thresholds = np.arange(0, 4, 0.01)
    embeddings1 = embeddings[0::2]
    embeddings2 = embeddings[1::2]
    tpr, fpr, accuracy = lfw.calculate_roc(thresholds, embeddings1, embeddings2,
        np.asarray(actual_issame), nrof_folds=nrof_folds)
    return tpr, fpr, accuracy

if __name__ == "__main__":
    main(parse_args())
