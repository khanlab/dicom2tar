#!/usr/bin/env python
'''
Define a DicomSorter class, which can sort dicom/compressed files, and tar the sorted files, to a destination directory.

Author: YingLi Lu
Email:  yinglilu@gmail.com
Date:   2018-05-22

Note:
    Tested on windows 10/ubuntu 16.04, python 2.7.14
'''

import os
import tarfile
import zipfile
import shutil
import tempfile
import uuid
import logging
from collections import defaultdict


class DicomSorter():
    '''
    Extract compressed files(if any), sort dicom files, or tar the sorted, to a destination directory.

    Given a dicom directory:
        1. Find compressed files(if any) recursively, extract them temporally. Support formats:.  zip, .tgz, .tar.gz, tar.bz2
        2. Find dicom files recursively, sort(organizing and renaming) them, according to a given 'sort_rule_function',
        3. Sort or Tar the sorted dicom files to a destination directory.

    attributes:
        dicom_dir: 
            dicom files directory, can have compressed files(.zip/.tgz/.tar.gz/.tar.bz2) under it.
        sort_rule_function:
            a function define how to sort(organizing and renaming) dicom files 
        output_dir:
            save sorted dicom files or tar files
        extract_to_dir:
            extract compressed files to this directory temporally, default is platform's temp dir.

    methods:
        tar()
        sort()

    Note: 
        When extract larger compressed files on a platform, like sharcnet, with limit storage capacity temp folder, 
        you might want to change the default 'extract_to_dir'

    '''

    def __init__(self, dicom_dir, sort_rule_function, output_dir, extract_to_dir=''):
        '''
        init DicomSorter
        '''
        self.logger = logging.getLogger(__name__)
        self._compressed_exts = ('.tar', '.tgz', '.tar.gz', '.tar.bz2', '.zip')
        self.dicom_dir = dicom_dir
        self.sort_rule_function = sort_rule_function
        self.output_dir = output_dir

        # extract_to_dir, default is platform's tmp dir
        if not extract_to_dir:
            temp_dir = tempfile.gettempdir()
            self.extract_to_dir = temp_dir
        else:
            self.extract_to_dir = extract_to_dir

        # _extract_to_dir_uniq = extract_to_dir/uniq-string
        # `rmtree _extract_to_dir_uniq` after the sorting
        self._extract_to_dir_uniq = os.path.join(
            self.extract_to_dir, "DicomSorter" + self._generate_uniq_string())
        if not os.path.exists(self._extract_to_dir_uniq):
            os.makedirs(self._extract_to_dir_uniq)

    def sort(self):
        '''
        extract, apply sort rule, copy(organizing and renaming) dicom files into hierarchical directories

        output:
            tar_full_filename_list: list of resulted tar filenames

        note: 
            write hierarchical direcotires and files on disk

        '''
        ######
        # extract compressed files if any
        ######
        self._walk_and_extract(
            self.dicom_dir, self._compressed_exts, self._extract_to_dir_uniq)

        # add _extract_to_dir_uniq directory in the search directories
        dicom_dirs = [self.dicom_dir, self._extract_to_dir_uniq]

        ######
        # walk and apply sort rule
        ######
        # return value is a list of list:
        #   [ [original_full_filename1, path/to/new-filename1],# [original_full_filename1, path/to/new-filename1],... ]
        before_after_sort_rule_list = self._walk_and_apply_sort_rule(
            dicom_dirs, self.sort_rule_function)

        # for logging
        sorted_dirs = []

        # copy: organizing and renaming original dicom files
        for item in before_after_sort_rule_list:

            # example: c:\\users\\user\\appdata\\local\\temp\\DicomSorter_8a46b089-fe90-4ee7-90fe-3cd9fc443d09\\0003.tar.gz816c904c-8e3e-4cff-8624-9fe4efd66815\\0003\\00001.dcm'
            original_full_filename = item[0]
            # example: PI\\Project\\19700101\\1970_01_01_T2\\1.9AC66A0D\\0003\\1970_01_01_T2.MR.PI_project.0003.0194.19700101.D6C44EC8.dcm
            relative_path_new_filename = item[1]

            source = item[0]
            relative_dest = item[1]

            # only the first element, example: PI
            sorted_dir = os.path.join(
                self.output_dir, relative_path_new_filename.split(os.sep)[0])
            if sorted_dir not in sorted_dirs:
                sorted_dirs.append(sorted_dir)

            full_path_new_full_filename = os.path.join(self.output_dir, relative_path_new_filename)
            dest_dir = os.path.dirname(full_path_new_full_filename)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            shutil.copy(original_full_filename, full_path_new_full_filename)

        return sorted_dirs

    def tar(self, depth, tar_filename_sep='_'):
        '''
        extract, apply sort rule, and create tar files

        input:
            depth: tar filename is named according to 'depth'.
                example:
                    given tree: /home/user/output_dir/project/study_date/patient_name/study_id
                    given depth = 4, 
                    tar filename is: project_study_date_patient_name_study_id.tar
            tar_filename_sep: seprator of the tar file name elements        

        output:
            tar_full_filename_list: list of resulted tar filenames

        note: 
            write tar files on disk

        '''
        ######
        # extract compressed files if any
        ######
        self._walk_and_extract(
            self.dicom_dir, self._compressed_exts, self._extract_to_dir_uniq)

        # add _extract_to_dir_uniq directory in the search directories
        dicom_dirs = [self.dicom_dir, self._extract_to_dir_uniq]

        ######
        # walk and apply sort rule
        ######
        # return value is a list of list:
        #   [[original_full_filename1, path/to/new-filename1],# [original_full_filename1, path/to/new-filename1],...]
        before_after_sort_rule_list = self._walk_and_apply_sort_rule(
            dicom_dirs, self.sort_rule_function)

        ######
        # tar
        ######

        # get a dict, key is tar_full_filename, key is a list of list:
        #   {tar_full_filename1:[[original_full_filename1,/path/to/new_filename1],[original_full_filename2,/path/to/new_filename2],...],
        #   tar_full_filename2:[[original_full_filename1,/path/to/new_filename2],[original_full_filename2,/path/to/new_filename2],...],...}
        tar_full_filename_dict = defaultdict(list)

        for item in before_after_sort_rule_list:
            # c:\\users\\user\\appdata\\local\\temp\\DicomSorter_8a46b089-fe90-4ee7-90fe-3cd9fc443d09\\0003.tar.gz816c904c-8e3e-4cff-8624-9fe4efd66815\\0003\\00001.dcm'
            origianl_full_filename = item[0]
            #'PI\\Project\\19700101\\1970_01_01_T2\\1.9AC66A0D\\0003\\1970_01_01_T2.MR.PI_project.0003.0194.19700101.D6C44EC8.dcm'
            relative_path_new_filename = item[1]

            # get tar file name
            #['PI','Project','19700101','1970_01_01_T2','1.9AC66A0D','0003','1970_01_01_T2.MR.PI_project.0003.0194.19700101.D6C44EC8.dcm']
            dir_split = relative_path_new_filename.split(os.sep)

            tar_filename = tar_filename_sep.join(dir_split[:depth])+".tar"
            tar_full_filename = os.path.join(self.output_dir, tar_filename)
            tar_full_filename_dict[tar_full_filename].append(item)

        for tar_full_filename, items in tar_full_filename_dict.items():

            with tarfile.open(tar_full_filename, "w") as tar:
                for item in items:
                    arcname = item[1]
                    tar.add(item[0], arcname=arcname)

        # for logging
        tar_full_filenames = tar_full_filename_dict.keys()
        return tar_full_filenames

    def _walk_and_apply_sort_rule(self, dicom_dirs, sort_rule_function):
        '''
        find each dicom files, apply sort rule

        input:
            dicom_dirs
            sort_rule_function:

        output:
            before_after_sort_rule_list: a list of list.
                sub_list[0]: original dicom-file's full path filename
                sub_list[1]: sorted-dicom-file's relative path filename: e.g. /pi/study_date/new-filename.dcm
        '''
        before_after_sort_rule_list = []
        for dicom_dir in dicom_dirs:
            for root, directories, filenames in os.walk(dicom_dir):
                for filename in filenames:
                    full_filename = os.path.join(root, filename)
                    if not full_filename.endswith(self._compressed_exts):
                        try:
                            sorted_relative_path_filename = sort_rule_function(
                                full_filename)
                            # apply sort_rule_function on non-dicom or bad dicom return None
                            if sorted_relative_path_filename is not None:
                                before_after_sort_rule_list.append(
                                    [full_filename, sorted_relative_path_filename])
                        except Exception as e:
                            self.logger.exception(e)

        return before_after_sort_rule_list

    def _generate_uniq_string(self):
        return str(uuid.uuid4())

    def _walk_and_extract(self, input_dir, compressed_exts, to_dir):
        #self.input_dir, self._extract_to_dir_uniq

        def extract(filename, to_dir):
            if (filename.endswith(".tar")):
                c_file = tarfile.open(filename, "r:")
            elif (filename.endswith(".tar.gz")) or (filename.endswith(".tgz")):
                c_file = tarfile.open(filename, "r:gz")
            elif (filename.endswith(".tar.bz2")):
                c_file = tarfile.open(filename, "r:bz2")
            elif (filename.endswith(".zip")):
                c_file = zipfile.ZipFile(filename)

            c_file.extractall(to_dir)
            c_file.close()

        #walk and extract
        for root, directories, filenames in os.walk(input_dir):
            for filename in filenames:
                full_filename = os.path.join(root, filename)
                if full_filename.endswith(compressed_exts):
                    #print 'decompressing ', full_filename
                    uniq_string = self._generate_uniq_string()
                    # filename+uniq_string: avoid same file names overwrite
                    output_dir = os.path.join(
                        to_dir, filename + uniq_string)

                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    try:
                        extract(full_filename, output_dir)
                    except Exception as e:
                        self.logger.exception(e)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        '''
        remove temp directories
        '''
        if os.path.exists(self._extract_to_dir_uniq):
            shutil.rmtree(self._extract_to_dir_uniq)
