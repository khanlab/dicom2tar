#!/usr/bin/env python
'''
decompress(.zip/.tgz/.tar.gz/tar.bz2),sort, and tar dicom files

#tested on python 2.7
'''

import os
import sys
import re
import pydicom
import tarfile
import zipfile
import shutil
import tempfile
import glob
import uuid

def clean_path(path):
    return re.sub(r'[^a-zA-Z0-9.-]', '_', '{0}'.format(path))

def hashcode(value):
    code = 0
    for character in value:
        code = (code * 31 + ord(character)) & 0xffffffff
    return '{0:08X}'.format(code)
           
def sort_dicom_file(filename,outupt_dir):
    '''
    sort dicom file into hierarchical dirs

    intput:
        filename: dicom filename
        output_dir:save sorted hierarchical dirs to 
    output:
        StudyID_hashed_StudyInstanceUID_dir:full path of StudyID + '.' + hashcode(dataset.StudyInstanceUID), for instance, 1.AC168B21

    Algorithm:
        for each dicom file:
            parse
            mv(new name)
    Structure: same with CFMM's dcmrcvr.https://gitlab.com/cfmm/dcmrcvr
      bidsdump-dicom/					
        -Khan/ ->first part of StudyDescription: Palaniyappan^TOPSY. this is principal!
            -NeuroAnalytics ->second part of StudyDescription: Palaniyappan^TOPSY. this is project 
                -20171108 ->StudyDate
                    -2017_11_08_SNSX_C023 ->patientName
                       -1.AC168B21 -> dataset.StudyID + '.' + hashcode(dataset.StudyInstanceUID)
                            -0001->series number
                            -0002
                            -0003
                            -0004
                            -0005
                            -0006
                            -0007
                            ...
                    -2017_11_08_snSx_C024
                        -1.AC168B24
                            ...
                    -2017_11_08_snSx_C025
                        -1.AC168B3C
    '''
    try:
        dataset = pydicom.read_file(filename)
    
        #CFMM's newer data:'khan^NeuroAnalytics'->['khan','NeuroAnalytics']
        #CFMM's older GE data:'peter DTI'->['peter','DTI']
        pp = dataset.StudyDescription.replace('^',' ').split() 
        patient = dataset.PatientName.partition('^')[0]

        path = os.path.join(outupt_dir, clean_path(pp[0]))
        if not os.path.exists(path):
            # Everyone can read the principal directory
            # This is required so individuals with access to a project,
            # but not principal can get to their projects
            #self._mkdir(path, permissions=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO, gid=self.principal_gid)

            #print path 
            os.makedirs(path)

        for nextpath in [pp[1],
                        dataset.StudyDate,
                        patient,
                        '.'.join([dataset.StudyID or 'NA', hashcode(dataset.StudyInstanceUID)]),
                        '{series:04d}'.format(series=dataset.SeriesNumber)]:
            #print nextpath
            path = os.path.join(path, clean_path(nextpath))
            if os.path.exists(path):
                continue
            else:
                #self._mkdir(path, permissions=stat.S_IRWXU | stat.S_IRWXG | stat.S_IWOTH | stat.S_IXOTH)
                #print path 
                os.makedirs(path)

        sorted_filename = '{patient}.{modality}.{study}.{series:04d}.{image:04d}.{date}.{unique}.dcm'.format(
            patient=patient.upper(),
            modality=dataset.Modality,
            study=dataset.StudyDescription.upper(),
            series=dataset.SeriesNumber,
            image=dataset.InstanceNumber,
            date=dataset.StudyDate,
            unique=hashcode(dataset.SOPInstanceUID),
            )
    except:
        print "something wrong with", filename
        return 

    sorted_full_filename = os.path.join(path, clean_path(sorted_filename))
    shutil.copy(filename,sorted_full_filename)
    

def tar_by_sorted_dir(dicom_dir,tar_dest_dir):
    '''
    search dir and tar sub-dir to PI_Project_studyDate_PatientName_StudyID+hashCode.tar

    '''
    #search depth 6: /dicom_dir/Palaniyappan/TOPSY/20170210/patientName/"StudyID+hashcode(StudyInstanceUID)"
    files_depth = glob.glob(os.path.join(dicom_dir,'*/*/*/*/*'))
    dirs = filter(lambda f: os.path.isdir(f), files_depth) 

    tar_full_filename_list=[]
    for dir in dirs:
        dir_split=dir.split(os.sep) #example result:['', 'bidsdump-dcom', 'Palaniyappan', 'TOPSY', '20170210', 'patientName','1.2E853E5E']
        
        #tar
        tar_filename="_".join(dir_split[-5:])+".tar"
        tar_full_filename=os.path.join(tar_dest_dir,tar_filename)
        tar_full_filename_list.append(tar_full_filename)
        
        #tar_cmd = 'tar cf {} {}'.format(tgz_full_filename,dir)
        #os.system(tar_cmd)

        with tarfile.open(tar_full_filename, "w") as tar:
            tar.add(dir)

    return  tar_full_filename_list

def decompress(filename,output_dir):
    if (filename.endswith(".tar")):
        c_file = tarfile.open(filename, "r:")
    elif (filename.endswith(".tar.gz")) or (filename.endswith(".tgz")):
        c_file = tarfile.open(filename, "r:gz")
    elif (filename.endswith(".tar.bz2")):    
        c_file = tarfile.open(filename, "r:bz2")
    elif (filename.endswith(".zip")):    
        c_file = zipfile.ZipFile(filename)
    
    c_file.extractall(output_dir)
    c_file.close()


def main(input_dir,tar_dest_dir):
    '''
    decompress(if folder contains compressed files), sort, and tar

    input:
        input_dir: folder contains dicom files(and/or .zip/.tgz/.tar.gz/.tar.bz2, can contain multi-sessions)
        tar_dest_dir: write tar files to this folder
    '''
        
    assert os.path.exists(input_dir)
    assert os.path.exists(tar_dest_dir)

    tmp_dir = tempfile.gettempdir() #cross-platform temp folder
    
    #decompress compressed file 'decompress_to_dir':$input_dir/.tmp/decompressed
    decompress_to_dir = os.path.join(input_dir,'.tmp')
    if not os.path.exists(decompress_to_dir):
        os.makedirs(decompress_to_dir)

    #sort dicom files to 'sort_to_dir':$tmp_dir/sorted
    sort_to_dir=os.path.join(tmp_dir,'sorted')
    if not os.path.exists(sort_to_dir):
        os.makedirs(sort_to_dir)

    #decompress
    for root, directories, filenames in os.walk(input_dir):
        for filename in filenames: 
            full_filename = os.path.join(root,filename)
            if full_filename.endswith(('.tar', '.tgz','.tar.gz','.tar.bz2','.zip')):
                print 'decompressing ', full_filename
                decompress_to_dir_= os.path.join(decompress_to_dir,clean_path(filename),str(uuid.uuid4())) #random uid: in case of same filename cross different sessions
                decompress(full_filename,decompress_to_dir_)

    #sort dicoms
    for root, directories, filenames in os.walk(input_dir):
        for filename in filenames: 
            full_filename = os.path.join(root,filename)
            if not full_filename.endswith(('.tar', '.tgz','.tar.gz','.tar.bz2','.zip')):
                sort_dicom_file(full_filename,sort_to_dir)

    #tar
    tar_full_filename_list = tar_by_sorted_dir(sort_to_dir,tar_dest_dir)

    print 'tar files:'
    for e in tar_full_filename_list:
        print e

    #rm decompress_to_dir sort_to_dir tar_to_dir
    shutil.rmtree(decompress_to_dir)
    shutil.rmtree(sort_to_dir)
    
if __name__=="__main__":
    
    if len(sys.argv)-1 < 2:
        print ("Usage: python " + os.path.basename(__file__)+  " dicom_dir tar_dest_dir")
        sys.exit()
    else:
        dicom_dir = sys.argv[1]
        tar_dest_dir = sys.argv[2]

    if not os.path.exists(tar_dest_dir):
        os.makedirs(tar_dest_dir)

    main(dicom_dir,tar_dest_dir)
    
#test
#python dicom2tar.py  /mnt/hgfs/test/dicom2bids/ ~/test/dicom2tar

