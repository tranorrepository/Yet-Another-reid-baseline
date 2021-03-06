# encoding: utf-8

import glob
import re
import os
import os.path as osp

from .base import BaseImageDataset


class Rydata(BaseImageDataset):
    """
    data licensed to Ruiyan AI Inc

    """
    dataset_dir = 'rydata/'
    def __init__(self, root='', verbose=True, **kwargs):
        super(Rydata, self).__init__()
        self.dataset_dir = osp.join(root, self.dataset_dir)
        self.train_dir = self.dataset_dir

        self._check_before_run()

        train = self._process_dir(self.train_dir, relabel=False)
        if verbose:
            print("=> rydata data loaded")
        train = self.relabel(train)
        self.train = train
        self.query = []
        self.gallery = []

        # for test
        # dataset = self._process_dir(self.train_dir, relabel=True)
        # query, gallery = self._split_query_gallery(dataset)
        # if verbose:
        #     print("=> rydata data loaded")
        #
        # self.train = []
        # self.query = query
        # self.gallery = gallery

        self.num_train_pids, self.num_train_imgs, self.num_train_cams = self.get_imagedata_info(self.train)
        self.num_query_pids, self.num_query_imgs, self.num_query_cams = self.get_imagedata_info(self.query)
        self.num_gallery_pids, self.num_gallery_imgs, self.num_gallery_cams = self.get_imagedata_info(self.gallery)

    def _split_query_gallery(self, dataset):
        query, gallery = [], []
        label = set()
        for ele in dataset:
            img_path, pid, camid = ele
            if pid not in label:
                query.append(ele)
                label.add(pid)
            else:
                gallery.append(ele)
        return query, gallery

    def _check_before_run(self):
        """Check if all files are available before going deeper"""
        if not osp.exists(self.dataset_dir):
            raise RuntimeError("'{}' is not available".format(self.dataset_dir))
        if not osp.exists(self.train_dir):
            raise RuntimeError("'{}' is not available".format(self.train_dir))

    def _find_files(self, dir_path, img_paths, suffix=['.jpg', '.png', '.bmp']):
        files = os.listdir(dir_path)
        for f in files:
            path = osp.join(dir_path, f)
            if os.path.isdir(path):
                self._find_files(path, img_paths, suffix)
            elif f[-4:] in suffix:
                img_paths.append(path)

    # element: (img_path, pid, camid)
    def _process_dir(self, dir_path, relabel=True):
        dataset_names = os.listdir(dir_path)
        bias = 10000
        label_dict = {}
        for i, dataset_name in enumerate(dataset_names):
            img_paths = []
            self._find_files(os.path.join(dir_path, dataset_name), img_paths)
            for img_path in img_paths:
                splits = img_path.split('/')
                pid, _ = splits[-2:]
                pid = int(pid)
                pid += i * bias
                camid = 1
                if pid in label_dict:
                    label_dict[pid].append([camid, img_path])
                else:
                    label_dict[pid] = [[camid, img_path]]

        pid2label = {pid: label for label, pid in enumerate(label_dict.keys())}
        dataset = []
        for pid in label_dict:
            for camid, img_path in label_dict[pid]:
                if relabel:
                    new_pid = pid2label[pid]
                else:
                    new_pid = pid
                dataset.append((img_path, new_pid, camid))
        return dataset


if __name__ == '__main__':
    dataset = Rydata(root='/home/xiangyuzhu/data/ReID/')
