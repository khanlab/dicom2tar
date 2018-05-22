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

import DicomSorter

logging.basicConfig(filename = 'a.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s -%(message)s')
    

def sort_rule_CFMM(filename):
    '''
    CFMM's Dicom sort rule

    intput:
        filename: dicom filename
    output:
        a dictionary:
            key: filename
            value: pi/project/study_date/patient/studyID_and_hash_studyInstanceUID/series_number
                   /{patient}.{modality}.{study}.{series:04d}.{image:04d}.{date}.{unique}.dcm

    CFMM's DICOM data Hierarchical structure: (same with CFMM's dcmrcvr.https://gitlab.com/cfmm/dcmrcvr)
    root_dir/
        -PI->first part of StudyDescription: John^Project.
            -project ->second part of StudyDescription: John^3T_Project.
                -19700101 ->StudyDate
                    -1970_01_01_C001 ->patientName
                    -1.AC168B21 -> dataset.StudyID + '.' + hashcode(dataset.StudyInstanceUID)
                            -0001->series number
                            -0002
                            -0003
                            -0004
                            -0005
                            -0006
                            -0007
                            ...
                    -1970_01_01_C002
                        -1.AC168B24
                            ...
                    -1970_01_01_C003
                        -1.AC168B3C
    '''

    def clean_path(path):
        return re.sub(r'[^a-zA-Z0-9.-]', '_', '{0}'.format(path))

    def hashcode(value):
        code = 0
        for character in value:
            code = (code * 31 + ord(character)) & 0xffffffff
        return '{0:08X}'.format(code)

    try:
        dataset = pydicom.read_file(filename)

        # CFMM's newer data:'PI^project'->['PI','project']
        # CFMM's older GE data:'PI project'->['PI','project']
        pi_project = dataset.StudyDescription.replace('^', ' ').split()
        pi = clean_path(pi_project[0])
        project = clean_path(pi_project[1])
        study_date = clean_path(dataset.StudyDate)
        patient = clean_path(dataset.PatientName.partition('^')[0])
        studyID_and_hash_studyInstanceUID = clean_path('.'.join([dataset.StudyID or 'NA',
                                                                 hashcode(dataset.StudyInstanceUID)]))
        series_number = clean_path(
            '{series:04d}'.format(series=dataset.SeriesNumber))

        path = os.path.join(pi, project, study_date, patient,
                            studyID_and_hash_studyInstanceUID, series_number)
        sorted_filename = '{patient}.{modality}.{study}.{series:04d}.{image:04d}.{date}.{unique}.dcm'.format(
            patient=patient.upper(),
            modality=dataset.Modality,
            study=dataset.StudyDescription.upper(),
            series=dataset.SeriesNumber,
            image=dataset.InstanceNumber,
            date=dataset.StudyDate,
            unique=hashcode(dataset.SOPInstanceUID),
        )
    except Exception as e:
        logging.exception('something wrong with {}'.format(filename))
        return None

    sorted_full_filename = os.path.join(path, sorted_filename)

    return sorted_full_filename


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

    with DicomSorter.DicomSorter(dicom_dir, sort_rule_CFMM, output_dir) as d:
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
