import argparse
import os
import sys
import numpy as np
import dlib
from skimage import io
import time

import lfw

onegraph_zuobi_nodetected_dict = {
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
# left, top, right, bottom
test1_20170525_nodetected_dict = {
    "a001.jpg": dlib.rectangle(200, 87, 200 + 338, 87 + 338),
    "a006.jpg": dlib.rectangle(146, 214, 146 + 372, 214 + 410),
    "a027.jpg": dlib.rectangle(163 , 398, 163 + 324, 398 + 287),
    "a034.jpg": dlib.rectangle(154 , 151, 154+276 ,151 + 238),
    "a037.jpg": dlib.rectangle(10, 380, 10 + 401, 380 + 428),
    "a053.jpg": dlib.rectangle(200 , 280, 200 + 392 , 280 + 389),
    "a075.jpg": dlib.rectangle(155, 396, 155 + 410, 396 + 311),
    "a100.jpg": dlib.rectangle(47, 321, 47 + 381, 321 + 307),
    "a117.jpg": dlib.rectangle(70, 239, 70 + 350 , 239 +317),
    "a125.jpg": dlib.rectangle(226 ,229 , 226 + 261, 229 + 220),
    "a134.jpg": dlib.rectangle(92 , 467, 92 + 368, 467 + 319),
    "a138.jpg": dlib.rectangle(212, 92, 212 + 164, 92 + 156),
    "a142.jpg": dlib.rectangle(42, 272, 42 + 418, 272 + 328),
    "a144.jpg": dlib.rectangle(122, 126, 122 + 345, 126 + 342),
    "a149.jpg": dlib.rectangle(147, 95, 147 + 263, 95 +256),
    "a156.jpg": dlib.rectangle(114, 483, 114 + 367, 483 + 380),
    "a165.jpg": dlib.rectangle(74, 224, 74 + 459, 224 + 473),
    "a186.jpg": dlib.rectangle(21, 82, 21 + 440, 82 + 511),
    "a197.jpg": dlib.rectangle(74, 140, 74 + 356 , 140 + 330),
    "a199.jpg": dlib.rectangle(117, 42, 117 + 414, 42 + 387),
    "a201.jpg": dlib.rectangle(245, 274, 245 + 365, 274 + 370),
    "a218.jpg": dlib.rectangle(429, 99, 429 + 319 , 99 + 293),
    "a221.jpg": dlib.rectangle(82, 103, 82 + 339, 103 + 281),
    "a245.jpg": dlib.rectangle(210 , 228, 210 + 506, 210 + 471),
    "a254.jpg": dlib.rectangle(171, 384, 171 + 460, 384 + 505),
    "a265.jpg": dlib.rectangle(372 , 349, 372 + 234, 349 + 224),
    "a267.jpg": dlib.rectangle(131, 155, 131 + 227, 155 + 223),
    "a275.jpg": dlib.rectangle(115, 516, 115 + 298, 516 + 337),
    "a305.jpg": dlib.rectangle(478, 59, 478 + 417, 59 + 422),
    "a321.jpg": dlib.rectangle(40, 220, 40 + 640, 220 + 626),
    "a336.jpg": dlib.rectangle(274, 162,274 + 263, 162 + 229),
    "a350.jpg": dlib.rectangle(232, 286, 232 + 486, 286 + 479),
    "a377.jpg": dlib.rectangle(147, 389, 147 + 625, 389 + 570),
    "a391.jpg": dlib.rectangle(61, 210, 61 + 456, 210 + 469),
    "a429.jpg": dlib.rectangle(177, 248, 177 + 345, 248 + 307),
    "a466.jpg": dlib.rectangle(5, 319, 5 + 607, 319 + 720),
    "a472.jpg": dlib.rectangle(70 , 95, 70 + 298, 95 + 290),
    "a481.jpg": dlib.rectangle(170, 289, 170 + 381, 289 + 341),
    "a486.jpg": dlib.rectangle(18, 180, 18 + 358, 180 + 384),
    "c218.jpg": dlib.rectangle(35, 94, 35 + 137, 94 + 119),
    "c283.jpg": dlib.rectangle(35, 77, 35 + 137, 77 + 117)
}

def main(args):
    # queryset_path = r"D:\datasets\500500\testdata\query"
    # dataset_path = r"D:\datasets\500500\testdata\database"
    # queryset_path = r"D:\datasets\500500\test1_182\IDMixImg"
    # dataset_path = r"D:\datasets\500500\test1_182\IDImg"
    queryset_path = r"D:\datasets\500500\test1_182\IDMixImg"
    dataset_path = r"D:\datasets\500500\test1_182\IDImg"

    # embedding_list, real_same_list = dlib_generate_embedding(get_q_list(queryset_path), get_d_list(dataset_path))
    dlib_generate_500(get_q_list(queryset_path), get_d_list(dataset_path), test1_20170525_nodetected_dict)
    # tpr, fpr, accuracy = evaluate(embedding_list, real_same_list)
    # print('Accuracy: %1.3f+-%1.3f' % (np.mean(accuracy), np.std(accuracy)))
    #
    # auc = metrics.auc(fpr, tpr)
    # print('Area Under Curve (AUC): %1.3f' % auc)


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

def evaluate(embedding_list, actual_issame, nrof_folds=10):
    # Calculate evaluation metrics
    embeddings = np.asarray(embedding_list)
    thresholds = np.arange(0, 4, 0.001)
    embeddings1 = embeddings[0::2]
    embeddings2 = embeddings[1::2]
    tpr, fpr, accuracy = lfw.calculate_roc(thresholds, embeddings1, embeddings2,
                                           np.asarray(actual_issame), nrof_folds=nrof_folds)
    return tpr, fpr, accuracy


win1 = None
win2 = None


def show_pair(path1, path2):
    global win1, win2
    if win1 == None:
        win1 = dlib.image_window()
    if win2 == None:
        win2 = dlib.image_window()
    img1 = io.imread(path1)
    img2 = io.imread(path2)
    win1.clear_overlay()
    win2.clear_overlay()
    win1.set_image(img1)
    win2.set_image(img2)
    dlib.hit_enter_to_continue()

    win1.set_image(img1)
    win2.set_image(img2)


def dlib_generate_500(query_paths, dataset_paths, nodetected_dict):
    predictor_dat_path = r"./shape_predictor_68_face_landmarks.dat"
    # face_rec_dat_path = r"./orig_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./1000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./4000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./10000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./20000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./origplus20000_dlib_face_recognition_resnet_model_v1.dat"
    face_rec_dat_path = r"./10x10origplus20000_dlib_face_recognition_resnet_model_v1.dat"


    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_dat_path)
    face_rec = dlib.face_recognition_model_v1(face_rec_dat_path)
    embedding_dict = {}
    nodetected_fail = False

    for i, img_path in enumerate(query_paths + dataset_paths):
        img = io.imread(img_path)
        key = os.path.basename(img_path)
        try:
            dets = detector(img, 1)
        except RuntimeError:
            print('%s failed on image format, please check it.' % img_path)
            continue

        if i % 1000 == 0:
            print(i, time.asctime(time.localtime(time.time())))
        det = None
        if len(dets) < 1:

            # If we can't detect only one face, we give the position of face.
            try:
                det = nodetected_dict[key]
            except KeyError:
                print('%s failed on face detection, please check it.' % img_path)
                det = dlib.rectangle(1, 1, 1 + 180, 1 + 180)

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

    if nodetected_fail:
        sys.exit(1)
    print("embedding geranating finished", time.asctime(time.localtime(time.time())))
    ground_truth_file = open("ground_truth.txt", "w")
    result_file = open("test_result.txt", "w")
    qkey_list = []
    dkey_list = []
    embeddingq = []
    embeddingd = []
    for qkey in query_paths:
        qqkey = os.path.basename(qkey)
        for dkey in dataset_paths:
            ddkey = os.path.basename(dkey)
            qkey_list.append(qqkey)
            dkey_list.append(ddkey)
            embeddingq.append(embedding_dict[qqkey])
            embeddingd.append(embedding_dict[ddkey])
            if qqkey[1:] == ddkey[1:]:
                ground_truth_file.write(qqkey + "," + ddkey + "\n")

    diff = np.subtract(embeddingq, embeddingd)
    dist = np.sum(np.square(diff), 1)

    for i, _ in enumerate(qkey_list):
        result_file.write(qkey_list[i] + "," + dkey_list[i] + "," + str(1.0 / dist[i]) + "\n")

    ground_truth_file.close()
    result_file.close()


def dlib_generate_500_without_detect(query_paths, dataset_paths, nodetected_dict):
    predictor_dat_path = r"./shape_predictor_68_face_landmarks.dat"
    # face_rec_dat_path = r"./orig_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./1000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./4000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./10000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./20000_dlib_face_recognition_resnet_model_v1.dat"
    face_rec_dat_path = r"./origplus20000_dlib_face_recognition_resnet_model_v1.dat"
    # face_rec_dat_path = r"./10x10origplus20000_dlib_face_recognition_resnet_model_v1.dat"


    shape_predictor = dlib.shape_predictor(predictor_dat_path)
    face_rec = dlib.face_recognition_model_v1(face_rec_dat_path)
    embedding_dict = {}

    for i, img_path in enumerate(query_paths + dataset_paths):
        img = io.imread(img_path)
        key = os.path.basename(img_path)

        if i % 1000 == 0:
            print(i, time.asctime(time.localtime(time.time())))
        det = dlib.rectangle(1, 1, 1 + 180, 1 + 180)

        shape = shape_predictor(img, det)
        face_embedding = face_rec.compute_face_descriptor(img, shape)
        embedding_dict[key] = np.array(face_embedding)

    print("embedding geranating finished", time.asctime(time.localtime(time.time())))
    ground_truth_file = open("ground_truth.txt", "w")
    result_file = open("test_result.txt", "w")
    qkey_list = []
    dkey_list = []
    embeddingq = []
    embeddingd = []
    for qkey in query_paths:
        qqkey = os.path.basename(qkey)
        for dkey in dataset_paths:
            ddkey = os.path.basename(dkey)
            qkey_list.append(qqkey)
            dkey_list.append(ddkey)
            embeddingq.append(embedding_dict[qqkey])
            embeddingd.append(embedding_dict[ddkey])
            if qqkey[1:] == ddkey[1:]:
                ground_truth_file.write(qqkey + "," + ddkey + "\n")

    diff = np.subtract(embeddingq, embeddingd)
    dist = np.sum(np.square(diff), 1)

    for i, _ in enumerate(qkey_list):
        result_file.write(qkey_list[i] + "," + dkey_list[i] + "," + str(1.0 / dist[i]) + "\n")

    ground_truth_file.close()
    result_file.close()

if __name__ == "__main__":
    main(parse_args())
