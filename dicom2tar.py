#!/usr/bin/env python
'''
CFMM's dicom files sort rule function, and sort CFMM' data use DicomSorter

Author: YingLi Lu
Email:  yinglilu@gmail.com
Date:   2018-05-15

Note:
    Tested on python 2.7.15

'''
import sys
import os
import re
import pydicom
import logging

import sort_rules
import DicomSorter

logging.basicConfig(filename = 'a.log', level=logging.DEBUG,
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

    with DicomSorter.DicomSorter(dicom_dir, sort_rules.sort_rule_CFMM, output_dir) as d:
        #######
        # sort
        #######
        sorted_dirs = d.sort()
        #logging
        for item in sorted_dirs:
            logger.info("sorted directory created: {}".format(item))


        # #######
        # # tar
        # #######
        # # according to CFMM's rule, folder depth is 5:
        # # pi/project/study_date/patient/studyID_and_hash_studyInstanceUID
        # tar_full_filenames = d.tar(5)
        
        # # logging
        # for item in tar_full_filenames:
        #     logger.info("tar file created: {}".format(item))

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
# linux: python dicom2tar.py  /mnt/hgfs/test/dicom2bids/ ~/test/dicom2tar
# windows: python dicom2tar.py  "D:\OneDrive - The University of Western Ontario\projects\dicom2tar\data\small_data" d:/test
