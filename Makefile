
SINGULARITY=~/apps/singularity/bin/singularity
SINGULARITY_IMAGE=~/singularities/dicom2tar.simg
SINGULARITY_FILE=Singularity.v0.0.3

all:test_small test_big  build singularity_test_small

test_small:
	python dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/small_data ~/test/dicom2tar

test_big:
	python dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/ ~/test/dicom2tar

test_converter:
	python dicom2tar.py /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor ~/test/dicom2tar

build: 
	sudo ${SINGULARITY} build --force ${SINGULARITY_IMAGE} ${SINGULARITY_FILE}

singularity_test_small:
	sudo ${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/small_data ~/test/dicom2tar
	
