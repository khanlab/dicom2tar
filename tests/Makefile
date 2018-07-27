SHELL := /bin/bash

SINGULARITY=~/apps/singularity/bin/singularity
SINGULARITY_IMAGE=~/singularities/dicom2tar.simg
SINGULARITY_FILE=Singularity.v0.0.5

all:

test_compress:
	dicom2tar ./tests/data/regular_cfmm ~/test/dicom2tar

test_cmrr:
	#siemens cmrr mb physio
	dicom2tar ./tests/data/MRS_Physio_data ~/test/dicom2tar
	
test_cfmm:
	#cfmm mrs physio
	dicom2tar ./tests/data/regular_cfmm ~/test/dicom2tar

test_pypi:
	sudo pip install --upgrade setuptools wheel twine
	pushd ..;ls -l; python setup.py sdist bdist_wheel;twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*;popd

build: 
	pushd ../dicom2tar;sudo ${SINGULARITY} build --force ${SINGULARITY_IMAGE} ${SINGULARITY_FILE};popd

singularity_test_small:
	${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/small_data ~/test/dicom2tar
	
singularity_test_cmrr:
	${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/2017_11_30_MS12 ~/test/dicom2tar

singularity_test_cfmm:
	${SINGULARITY} run -B /mnt:/mnt -B /home:/home ${SINGULARITY_IMAGE} /mnt/hgfs/projects/dicom2tar/data/MRS_Physio_data/three_dicoms_from_Igor ~/test/dicom2tar
