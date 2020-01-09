[![CircleCI](https://circleci.com/gh/khanlab/dicom2tar/tree/master.svg?style=svg)](https://circleci.com/gh/khanlab/dicom2tar/tree/master)
# dicom2tar
Tool for extract compressed files(if any), sort dicom files according to given rule, or tar the sorted, to a destination directory. 

Check dicom2tar.py for example.

### To install on graham:

```
module unload python
module load python/2
virtualenv ~/python_dicom2tar
source ~/python_dicom2tar/bin/activate
pip install dicom2tar
deactivate
```

You can then run it with:
```
source ~/python_dicom2tar/bin/activate
dicom2tar <input> <output>
```

