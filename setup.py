import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = "0.1"
setuptools.setup(name='dicom2tar',
                 version=VERSION,
                 description="sort or tar CFMM' data with DicomSorter",
                 author='YingLi Lu,Ali Khan',
                 author_email='alik.khanlab@gmail.com,yinglilu@gmail.com',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/khanlab/dicom2tar",
                 license='GNU General Public License v3.0',
                 entry_points={
                     'console_scripts': [
                         'dicom2tar = dicom2tar.main:run']},
                 packages=setuptools.find_packages(),
                 install_requires=['pydicom',
                                   'extractCMRRPhysio', 'DicomRaw'],
                 zip_safe=False)
