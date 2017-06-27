import argparse
import os
import sys
import numpy as np
import dlib
from skimage import io
import time
from sklearn import metrics
from scipy.optimize import brentq
from scipy import interpolate

import lfw

nodetected_dict = {
    "q_1341.jpg": dlib.rectangle(249, 258, 249 + 110, 259 + 93),
    "q_153.jpg": dlib.rectangle(219, 203, 219 + 210, 203 + 228),
    "q_278.jpg": dlib.rectangle(144, 256, 144 + 218, 256 + 183),
    "q_3639.jpg": dlib.rectangle(203, 105, 203 + 245, 105 + 241),
    "q_500.jpg": dlib.rectangle(203, 71, 203 + 181, 71 + 179),
    "q_739.jpg": dlib.rectangle(248, 79, 248 + 122, 79 + 108),
    "q_994.jpg": dlib.rectangle(221, 125, 221 + 210, 125 + 209),
    "d_2655.jpg": dlib.rectangle(23, 83, 23 + 179, 83 + 189),
    "d_3639.jpg": dlib.rectangle(38, 94, 38 + 155, 94 + 153),
    "d_3698.jpg": dlib.rectangle(29, 66, 22 + 172, 66 + 184),
    "d_568.jpg": dlib.rectangle(48, 103, 48 + 144, 103 + 148)
}


def main(args):
    # queryset_path = r"D:\datasets\500500\testdata\query"
    # dataset_path = r"D:\datasets\500500\testdata\database"
    queryset_path = r"./testdata/query"
    dataset_path = r"./testdata/database"

    embedding_list, real_same_list = dlib_generate_embedding(get_q_list(queryset_path), get_d_list(dataset_path))
    tpr, fpr, accuracy = evaluate(embedding_list, real_same_list)
    print('Accuracy: %1.3f+-%1.3f' % (np.mean(accuracy), np.std(accuracy)))

    auc = metrics.auc(fpr, tpr)
    print('Area Under Curve (AUC): %1.3f' % auc)
    # eer = brentq(lambda x: 1. - x - interpolate.interp1d(fpr, tpr)(x), 0., 1.)
    # print('Equal Error Rate (EER): %1.3f' % eer)


def get_q_list(queryset_path):
    q_list = []
    for basename in os.listdir(queryset_path):
        q_list.append(os.path.join(queryset_path, basename).lower())
    return q_list


def get_d_list(dataset_path):
    d_list = []
    for basename in os.listdir(dataset_path):
        d_list.append(os.path.join(dataset_path, basename).lower())
    return d_list


def parse_args():
    parser = argparse.ArgumentParser()

    return parser.parse_args(sys.argv[1:])


# win = dlib.image_window()


def dlib_generate_embedding(query_paths, dataset_paths):
    predictor_dat_path = r"./shape_predictor_68_face_landmarks.dat"
    face_rec_dat_path = r"./orig_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./1000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./4000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./10000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./20000_dlib_face_recognition_resnet_model_v1.dat"
    # predictor_dat_path = r"C:\sources\dlib\build\Release\shape_predictor_68_face_landmarks.dat"
    # face_rec_dat_path = r"C:\sources\dlib\build\Release\orig_dlib_face_recognition_resnet_model_v1.dat"

    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_dat_path)
    face_rec = dlib.face_recognition_model_v1(face_rec_dat_path)
    embedding_dict = {}
    non_only_one_list = []
    more_than_one_list = []

    for i, img_path in enumerate(query_paths + dataset_paths):
        img = io.imread(img_path)
        key = os.path.basename(img_path)
        dets = detector(img, 1)

        # win.clear_overlay()
        # win.set_image(img)

        if i % 1000 == 0:
            print(i, time.asctime(time.localtime(time.time())))
        det = None
        if len(dets) < 1:

            # If we can't detect only one face, we give the position of face.
            try:
                det = nodetected_dict[key]
            except KeyError:
                print('%s failed on face detection, please check it.' % img_path)
                continue

        if len(dets) >= 1:
            det = dets[0]
            # print('%s multi-faces detected during face detection, please check it.' % img_path)
            # If we detected multi-face, we choose the biggest rectangle.
            for k, d in enumerate(dets):
                if (d.right() - d.left()) * (d.bottom() - d.top()) > (det.right() - det.left()) * (det.bottom() - det.top()):
                    det = d

        shape = shape_predictor(img, det)
        face_embedding = face_rec.compute_face_descriptor(img, shape)
        embedding_dict[key] = np.array(face_embedding)

    print("embedding geranating finished", time.asctime(time.localtime(time.time())))
    actual_issame = []
    embedding_list = []
    for qkey in query_paths:
        qqkey = os.path.basename(qkey)
        for dkey in dataset_paths:
            ddkey = os.path.basename(dkey)
            embedding_list.append(embedding_dict[qqkey])
            embedding_list.append(embedding_dict[ddkey])
            if qqkey[1:] == ddkey[1:]:
                actual_issame = True
            else:
                actual_issame = False




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
