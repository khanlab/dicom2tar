#!/usr/bin/env python
'''
Define a DicomSorter class, which can sort dicom/compressed files, or tar the sorted files, to a destination directory.

Author: YingLi Lu
Email:  yinglilu@gmail.com
Date:   2018-05-15

Note:
    Tested on python 2.7.15
'''

import os
import tarfile
import zipfile
import shutil
import tempfile
import glob
import uuid
import logging

class DicomSorter():
    '''
    Extract compressed files(if any), sort dicom files, or tar the sorted, to a destination directory.

    Given a dicom directory:
        1. Find compressed files(if any) recursively, extract them temporally. Support formats:.  zip, .tgz, .tar.gz, tar.bz2
        2. Find dicom files recursively, sort(organizing and renaming) them, according to a given 'sort_rule_function', to a destination directory
        3. Tar the sorted dicom files to a destination directory.

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
        sort()
        tar()
    
    Note: 
        When extract larger compressed files on a platform with limit storage capacity temp folder, you might want to change the default 'extract_to_dir'

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

        self._extract_to_dir_uniq = None
        # extract_to_dir, default is platform's tmp dir
        if not extract_to_dir:
            temp_dir = tempfile.gettempdir()
            self.extract_to_dir = temp_dir
        else:
            self.extract_to_dir = extract_to_dir

        # _extract_to_dir_uniq = extract_to_dir/uniq-string
        # `rmtree _extract_to_dir_uniq` after the sorting
        uniq_string = self._generate_uniq_string()
        self._extract_to_dir_uniq = os.path.join(
            self.extract_to_dir, "DicomSorter_extract_" + uniq_string)

        if not os.path.exists(self._extract_to_dir_uniq):
            os.makedirs(self._extract_to_dir_uniq)

        self._sort_to_dir_uniq = None

    def sort(self):
        '''
        extract, sort, copy(organizing and renaming) dicom files into hierarchical directories
        '''
        # walk and extract compressed files
        self._walk_and_extract(
            self.dicom_dir, self._compressed_exts, self._extract_to_dir_uniq)

        # add _extract_to_dir_uniq directory to the search directory
        dicom_dirs = [self.dicom_dir, self._extract_to_dir_uniq]

        # walk and apply sort rule
        before_after_sort_rule_dict = self._walk_and_apply_sort_rule(
            dicom_dirs, self.sort_rule_function)

        sorted_dirs=[]

        # copy: organizing and renaming original dicom files
        for source, relative_dest in before_after_sort_rule_dict.items():

            #for logging
            sorted_dir = os.path.join(self.output_dir,relative_dest.split(os.sep)[0])

            if sorted_dir not in sorted_dirs:
                sorted_dirs.append(sorted_dir)

            dest = os.path.join(self.output_dir,relative_dest)
            dest_dir = os.path.dirname(dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy(source, dest)

        return  sorted_dirs

    def tar(self, depth):
        '''
        extract, sort, copy(organizing and renaming), and tar 

        input:
            depth:
                1. tar filename is named according to 'depth'.
                    example:
                        given tree: /home/user/output_dir/project/study_date/patient_name/study_id
                        given depth = 4, 
                        tar filename is: project_study_date_patient_name_study_id.tar

                2. tar's arcname is named according to 'depth'
                    with the above example,
                    tar file will store relative path: project/study_date/patient_name/study_id
                    instead of absolute path /home/user/output_dir/project/study_date/patient_name/study_id

        output:
            tar_full_filename_list:
                list of resulted tar filenames

        '''
        # extract
        self._walk_and_extract(
            self.dicom_dir, self._compressed_exts, self._extract_to_dir_uniq)

        # add _extract_to_dir_uniq directory to the search directory
        dicom_dirs = [self.dicom_dir, self._extract_to_dir_uniq]

        # create temp _sort_to_dir_uniq
        uniq_string = self._generate_uniq_string()
        self._sort_to_dir_uniq = os.path.join(
            self.extract_to_dir, "DicomSorter_sort_"+uniq_string)

        # walk and apply sort rule
        before_after_sort_rule_dict = self._walk_and_apply_sort_rule(
            dicom_dirs, self.sort_rule_function)

        # copy: organizing and renaming original dicom files
        for source, relative_dest in before_after_sort_rule_dict.items():
            dest = os.path.join(self._sort_to_dir_uniq,relative_dest)
            
            dest_dir = os.path.dirname(dest)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy(source, dest)

        dirs = self._list_paths_with_depth_under_dir(
            self._sort_to_dir_uniq, depth)

        # tar
        tar_full_filenames = []
        for dir in dirs:

            # get tar file name
            dir_split = dir.split(os.sep)
            tar_filename = "_".join(dir_split[-depth:])+".tar"
            tar_full_filename = os.path.join(self.output_dir, tar_filename)

            # arcname: use relative path instead of absolute path in tar file
            # exmple:
            # dir:
            #   c:\users\user\appdata\local\temp\DicomSorter_sort_3e6940f2-1241-421d-b9fb-122230b33c39\pi\project\20170101
            # arcname:
            #   pi\project\20170101
            # tar.add(dir, arcname = arcname) will tar 'dir' with an alternative name arcname
            with tarfile.open(tar_full_filename, "w") as tar:
                arcname = os.path.join(*dir_split[-depth:])
                tar.add(dir, arcname=arcname)

            tar_full_filenames.append(tar_full_filename)

        # for logging
        return tar_full_filenames

    def _walk_and_apply_sort_rule(self, dicom_dirs, sort_rule_function):
        '''
        find each dicom files, apply sort rule

        input:
            dicom_dirs
            sort_rule_function:
          
        output:
            sorted_dict: a dictionary
                key: original dicom file's full path filename
                value: sorted dicom file's relative path filename: e.g. /pi/study_date/new-filename.dcm
        '''
        before_after_sort_rule_dict = {}
        for dicom_dir in dicom_dirs:
            for root, directories, filenames in os.walk(dicom_dir):
                for filename in filenames:
                    full_filename = os.path.join(root, filename)
                    if not full_filename.endswith(self._compressed_exts):
                        try:
                            sorted_relative_path_filename = sort_rule_function(full_filename)
                            # apply sort_rule_function on non-dicom or bad dicom return None
                            if sorted_relative_path_filename is not None:
                                before_after_sort_rule_dict[full_filename] = sorted_relative_path_filename
                        except Exception as e:
                            self.logger.exception(e)

        return before_after_sort_rule_dict

    def _generate_uniq_string(self):
        return str(uuid.uuid4())

    def _list_paths_with_depth_under_dir(self, root_dir, depth):
        '''
        list all paths with a 'depth' under 'root_dir'

        Example: given tree
            home
              |-user
                |-root_dir
                  |-dir1
                  |-dir2-1
                    |-dir3
                    ...
                  |-dir2-2    

            depth = 2 will list ['/home/user/root_dir/dir1/dir2-1','/home/user/root_dir/dir1/dir2-2']
        '''

        if depth <= 0:
            return []

        glob_rule = os.sep.join(depth*['*'])

        files_dirs = glob.glob(os.path.join(root_dir, glob_rule))
        dirs = [e for e in files_dirs if os.path.isdir(e)]
        
        return dirs

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
        if self._extract_to_dir_uniq is not None:
            if os.path.exists(self._extract_to_dir_uniq):
                shutil.rmtree(self._extract_to_dir_uniq)

        if self._sort_to_dir_uniq is not None:
            if os.path.exists(self._sort_to_dir_uniq):
                shutil.rmtree(self._sort_to_dir_uniq)

