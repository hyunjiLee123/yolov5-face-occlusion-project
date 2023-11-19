import os
import cv2
import numpy as np
import shutil
from tqdm import tqdm

root = '/home/lee2/Documents/hj_occlusion_project/dataset/WIDER_1person' # original folder loc


def xywh2xxyy(box):
    x1 = box[0]
    y1 = box[1]
    x2 = box[0] + box[2]
    y2 = box[1] + box[3]
    return (x1, x2, y1, y2)


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def wider2face(phase='val', ignore_small=0):
    data = {}
    with open('{}/{}/label.txt'.format(root, phase), 'r') as f:
        lines = f.readlines()
        for line in tqdm(lines):
            line = line.strip()
            if '.jpg' in line:
                path = '{}/{}/images/{}'.format(root, phase, os.path.basename(line))
                img = cv2.imread(path)
                label_path = '{}/{}/images/{}'.format(root, phase, line)
                height, width, _ = img.shape
                data[label_path] = list()
            else:
                box = np.array(line.split()[0:4], dtype=np.float32)  # (x1,y1,w,h)
                if box[2] < ignore_small or box[3] < ignore_small:
                    continue
                box = convert((width, height), xywh2xxyy(box))
                label = '0 {} {} {} {} -1 -1 -1 -1 -1 -1 -1 -1 -1 -1'.format(round(box[0], 4), round(box[1], 4),
                                                                             round(box[2], 4), round(box[3], 4))
                data[label_path].append(label)
    return data


if __name__ == '__main__':
    datas = wider2face('val')
    for idx, data in enumerate(datas.keys()):
        pict_name = os.path.basename(data)
        # output
        dir = os.path.basename(os.path.dirname(data))
        out_img_dir = './widerface/val_test/images/{}'.format(dir)
        if not os.path.isdir(out_img_dir):
            os.makedirs(out_img_dir)
        out_lab_dir = './widerface/val_test/labels/{}'.format(dir)
        if not os.path.isdir(out_lab_dir):
            os.makedirs(out_lab_dir)
        out_img = out_img_dir + '/' + pict_name
        out_txt = out_lab_dir + '/' + os.path.splitext(pict_name)[0] + '.txt'
        origin_path = os.path.dirname(os.path.dirname(data)) + '/' + os.path.basename(data)
        shutil.copyfile(origin_path, out_img)
        labels = datas[data]
        f = open(out_txt, 'w')
        for label in labels:
            f.write(label + '\n')
        f.close()