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

