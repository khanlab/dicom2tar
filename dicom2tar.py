#!/usr/bin/env python
'''
sort or tar CFMM' data with DicomSorter

Author: YingLi Lu
Email:  yinglilu@gmail.com
Date:   2018-05-22

Note:
    Tested on windows 10/ubuntu 16.04, python 2.7.14

'''
import sys
import os
import re
import logging

import sort_rules
import DicomSorter

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s -%(message)s')
    
def main(dicom_dir, output_dir):
    '''
    example showing how to use DicomSorter for CFMM's dicom data

    input:
        dicom_dir: folder contains dicom files(and/or compressed files:.zip/.tgz/.tar.gz/.tar.bz2)
        output_dir: output sorted or tar files to this folder
    '''

    logger = logging.getLogger(__name__)

    if not os.path.exists(dicom_dir):
        print("Error: {} not exist!".format(dicom_dir))
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ######
    # CFMM
    ######
    with DicomSorter.DicomSorter(dicom_dir, sort_rules.sort_rule_CFMM, output_dir) as d:
        # #######
        # # sort
        # #######
        # sorted_dirs = d.sort()
        # #logging
        # for item in sorted_dirs:
        #     logger.info("sorted directory created: {}".format(item))


        #######
        # tar
        #######
        # pi/project/study_date/patient/studyID_and_hash_studyInstanceUID
        tar_full_filenames = d.tar(5)
        # logging
        for item in tar_full_filenames:
            logger.info("tar file created: {}".format(item))

    # ######
    # # demo
    # ######
    # with DicomSorter.DicomSorter(dicom_dir, sort_rules.sort_rule_demo, output_dir) as d:
    #     # sort
    #     sorted_dirs = d.sort()
    #     #logging
    #     for item in sorted_dirs:
    #         logger.info("sorted directory created: {}".format(item))

    #     # tar
    #     # patient_name/study_date/series_number/new_filename.dcm
    #     tar_full_filenames = d.tar(2)
    #     # logging
    #     for item in tar_full_filenames:
    #         logger.info("tar file created: {}".format(item))

if __name__ == "__main__":

    if len(sys.argv)-1 < 2:
        print ("Usage: python " + os.path.basename(__file__) +
               " dicom_dir output_dir")
        sys.exit()
    else:
        dicom_dir = sys.argv[1]
        output_dir = sys.argv[2]

    main(dicom_dir, output_dir)

# test command line
# linux: python dicom2tar.py  /mnt/hgfs/test/dicom2tar/ ~/test/dicom2tar
# sudo /home/ylu/apps/singularity/bin/singularity build ~/singularities/dicom2tar.simg Singularity.v0.0.2
# windows: python dicom2tar.py  "D:\OneDrive - The University of Western Ontario\projects\dicom2tar\data\small_data" d:/test
# sudo /home/ylu/apps/singularity/bin/singularity run -B /mnt:/mnt -B /home:/home  /home/ylu/singularities/dicom2tar.simg  /mnt/hgfs/projects/dicom2tar/data/small_data /home/ylu/test/dicom2tar
