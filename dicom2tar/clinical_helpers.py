# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:03:24 2019

@author: User
"""
import os
import numpy as np
import pandas as pd
from tempfile import mkdtemp
import  tarfile
import shutil
import csv

def tarSession(tar_dir, source_dir, modality_sep):
    
    tar_files = [f for f in os.listdir(tar_dir) if f.endswith('.tar')]
    subjects = np.unique([x.split('_')[0] for x in tar_files])
    isub = 0
    for isub in range(len(subjects)):
        tar_files_sub = [f for f in os.listdir(tar_dir) if f.startswith(subjects[isub])]
        tar_files_sub_check = tar_files_sub[0].split('_')
        if len(tar_files_sub_check) > 7:
            print('Incorrect .tar filname for subject ' + subjects[isub])
            continue
        else:
            tar_files_dates = [x.split('_')[4] for x in tar_files_sub]
            date_sort_idx = np.argsort(tar_files_dates)
            
            tar_files_sub = [tar_files_sub[i] for i in date_sort_idx]
            tar_files_dates = [tar_files_dates[i] for i in date_sort_idx]
            
            sessionDates = {'date':[],'session':[]}
            session = 1
            for idate in range(len(tar_files_dates)):
                if modality_sep:
                    sessionDates['date'].append(tar_files_dates[idate])
                    sessionDates['session'].append(str(session).zfill(3))
                    session += 1
                else:
                    sessionDates['date'].append(tar_files_dates[idate])
                    sessionDates['session'].append(str(session).zfill(3))
                    session += 1
                    
            sessionDates = pd.DataFrame.from_dict(sessionDates)
            
            for i in range(len(tar_files_sub)):
                
                session = sessionDates.loc[i,'session']
                tmpdir = mkdtemp(prefix='DCM')
                
                tf = tarfile.open(os.path.join(tar_dir,tar_files_sub[i]))
                tmembers = tf.getmembers()
                for tm in tmembers:
                    tm.mode = 0o700
                tf_content = [m.name for m in tmembers if m.isfile()]
                fullTarPath = [os.path.join(tmpdir, f) for f in tf_content]
                tf.extractall(path=tmpdir, members=tmembers)
                tf.close()
                
                newName = tar_files_sub[i].split('_')
                newName = os.path.join(tar_dir, '_'.join([newName[0], session] + newName[1:]))
                
                with tarfile.open(newName, "w") as tar:
                    for filename in fullTarPath:
                        original_full_filename = filename
                        newName = filename.split('\\')[-1].split('/')
                        firstPart = '_'.join([newName[0].split('_')[0], session, newName[0].split('_')[1], newName[0].split('_')[2], newName[0].split('_')[3]])
                        lastPart = '_'.join([newName[-1].split('_')[0], session, newName[-1][5:]])
                        newName[0] = firstPart
                        newName[-1] = lastPart
                        arcname = '/'.join(newName)
                        tar.add(original_full_filename, arcname=arcname)
        
                shutil.rmtree(tmpdir)
                os.remove(os.path.join(tar_dir, tar_files_sub[i]))    
                
                print('Finished subject ' + subjects[isub] + ' session ' + session)

def combine_or_dates(source_dir, tar_dir):
    subs = [f for f in os.listdir(source_dir) if f.startswith('sub')]
    masterList = []
    for isub in range(len(subs)):
        path_to_sub = os.path.join(source_dir, subs[isub])
        my_file = os.path.join(path_to_sub, 'OR_dates.tsv')
        if os.path.exists(my_file):
            with open(my_file, 'r') as readFile:
                reader = csv.reader(readFile, delimiter='\t')
                next(reader, None)
                lines = list(reader)
            if len(lines)>1:
                sortedDates = [x[1] for x in lines]
                dateSort = np.argsort(sortedDates)
                for isort in range(len(dateSort)):
                    masterList.append(lines[dateSort[isort]])
            else:
                masterList.append(lines[0])
            
            os.remove(my_file) 
            
    if not masterList: 
        if os.path.exists(os.path.join(source_dir, 'or_dates.tsv')):
            with open(os.path.join(source_dir, 'or_dates.tsv'), 'r') as readFile:
                reader = csv.reader(readFile, delimiter='\t')
                next(reader, None)
                masterList = list(reader)
         
    final_file = os.path.join("\\".join(tar_dir.split('\\')[:-1]), 'or_dates.tsv')
    if os.path.exists(final_file):
        with open(final_file, 'r') as readFile:
            reader = csv.reader(readFile, delimiter='\t')
            next(reader, None)
            lines = list(reader)
        masterList = lines + [x for x in masterList if x not in lines]
        finalList = sorted(masterList, key=lambda x: (x[0], x[1]))
    else:
        finalList = masterList
                                        
    with open(final_file, 'w') as writeFile:
        writeFile.write("\t".join(['subject','or_date']))
        writeFile.write( "\n" )
        for i in range(len(finalList)):
            writeFile.write("\t".join(finalList[i]))
            writeFile.write( "\n" )
            
def combine_error_info_tsv(source_dir, tar_dir):
    if os.path.exists(os.path.join(source_dir, 'errorInfo.tsv')):
        with open(os.path.join(source_dir, 'errorInfo.tsv'), 'r') as readFile:
            reader = csv.reader(readFile, delimiter='\t')
            next(reader, None)
            masterList = list(reader)
        final_file = os.path.join("\\".join(tar_dir.split('\\')[:-1]), 'errorInfo.tsv')
        if os.path.exists(final_file):
            with open(final_file, 'r') as readFile:
                reader = csv.reader(readFile, delimiter='\t')
                next(reader, None)
                lines = list(reader)
            masterList = lines + [x for x in masterList if x not in lines]
            finalList = sorted(masterList, key=lambda x: (x[0], x[1], x[2]))
        else:
            finalList = masterList
                                            
        with open(final_file, 'w') as writeFile:
            writeFile.write("\t".join(['subject','date', 'series']))
            writeFile.write( "\n" )
            for i in range(len(finalList)):
                writeFile.write("\t".join(finalList[i]))
                writeFile.write( "\n" )
        
        os.remove(os.path.join(source_dir, 'errorInfo.tsv')) 