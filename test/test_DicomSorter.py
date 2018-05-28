#!/usr/bin/env python
'''
test DicomSorter.py functions
'''


import logging
import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import DicomSorter
import sort_rules

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s -%(message)s')

# small data without mrs physio
# dicom_dir = '/mnt/hgfs/projects/dicom2tar/data/small_data'

# Igor's script wraped mrs and physio
#dicom_dir = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor'

# siemens cmrr mb physio
dicom_dir = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/2017_11_30_MS12'

output_dir = '/home/ylu/test/dicom2tar'
#dicomunwrap_path = '/home/ylu/apps/DicomRaw/bin/dicomunwrap'
dicomunwrap_path = '/home/ylu/apps/DicomRaw/bin/dicomunwrap'
simens_cmrr_mb_unwrap_path = '/mnt/hgfs/projects/dicom2tar/src/extract_cmrr_physio.py'


with DicomSorter.DicomSorter(dicom_dir, sort_rules.sort_rule_CFMM, output_dir, simens_cmrr_mb_unwrap_path=simens_cmrr_mb_unwrap_path) as d:

    # # filename = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor/mrs1.dcm'
    # # filename = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor/physio1.dcm'
    # filename = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor/physio2.dcm'
    filename = '/mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/2017_11_30_MS12/1.3.12.2.1107.5.2.43.67007.2017113012213822613175070'

    r = d._check_non_imaging_and_unwrap(filename)
    print(r)

    #r = d._walk_and_apply_sort_rule([dicom_dir], sort_rules.sort_rule_CFMM)
    # print(r)

    # unwrap
    # d._walk_and_check_non_imaging_and_unwrap(dicomunwrap_path)

    # #######
    # # sort
    # #######
    #sorted_dirs = d.sort()
    # #logging
    # for item in sorted_dirs:
    #     logger.info("sorted directory created: {}".format(item))

    # # #######
    # # # tar
    # # #######
    # # # pi/project/study_date/patient/studyID_and_hash_studyInstanceUID
    # tar_full_filenames = d.tar(5)
    # # logging
    # for item in tar_full_filenames:
    #     logging.info("tar file created: {}".format(item))
