SHELL := /bin/bash

SINGULARITY=~/apps/singularity/bin/singularity
SINGULARITY_IMAGE=~/singularities/dicom2tar.simg
SINGULARITY_FILE=Singularity.v0.0.3

all:



test_empty:
	python ../dicom2tar.py ~/test/empty_dir ~/test/dicom2tar

test_small:
	python ../dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/small_data ~/test/dicom2tar

test_big:
	python ../dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/ ~/test/dicom2tar

test_cmrr:
	#siemens cmrr mb physio
	python ../dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/2017_11_30_MS12 ~/test/dicom2tar
	
test_cfmm:
	#cfmm mrs physio
	python ../dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor ~/test/dicom2tar

build: 
	pushd ../;sudo ${SINGULARITY} build --force ${SINGULARITY_IMAGE} ${SINGULARITY_FILE};popd

singularity_test_small:
	sudo ${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/small_data ~/test/dicom2tar
	
singularity_test_cmrr:
	sudo ${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/2017_11_30_MS12 ~/test/dicom2tar

singularity_test_cfmm:
	sudo ${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor ~/test/dicom2tar
