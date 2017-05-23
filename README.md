# ICDAR 2017 Competition SmartDoc-reconstruction
## Example Method -- in Python
This repository contains an example method for participants to check how to read inputs 
and write outputs, and also to illustrate how the global processing pipeline could look like.

Thank you for your interest in our competition, and good luck to all participants!

### Language and dependencies
This example method is wrote using Python 2.7+ for maximal compatibility with existing image processing libraries.

It depends on two libraries:
* **Numpy** (any recent version should work): the famous package for scientific computing -- http://www.numpy.org/
* **OpenCV** (version 2.10+ but not 3.x): the famous computer vision library -- http://opencv.org/

As this methods makes use of SIFT for object tracking, we believe the 2.X series are easier to use.
If you need OpenCV 3.X support, it may be easy to fix the incompatible few lines.

If you use a virtual environment to develop in Python, we recommend to use VirtualEnv Wrapper (http://virtualenvwrapper.readthedocs.io/) and to give the virtual environment access to the global site-packages using a command like:
~~~
$ mkvirtualenv --system-site-packages smartdoc17
~~~

This example method was successfully run within a Docker container. Any decent container with OpenCV 2.10+ and Python should work.


### Installation
Simply copy the files of this repository.

### Update
Reinstall from https://github.com/smartdoc2017-competition/sample_method_python

### Usage
Run the following command to print out the help:
~~~
$ python main.py -h
~~~

To run the method, you can use:
~~~
$ python main.py  --debug --gui \
    /path/to/sampleNN/task_data.json \
    /path/to/sampleNN/input.mp4 \
    /path/to/sampleNN/reference_frame_??_dewarped.png \
    /path/to/output/sampleNN.png
~~~

`--debug` and `--gui` activate debug output and graphical interface, respectively. The GUI slows the method down.


### Improving this method
The file `processing/VideoCapture.py` contains the core of the method.
It contains several comments about the critical points of the pipeline.
We tried to keep the whole project readable, even for the non-experts in Python.


### Questions
Ask us any question about the competition at: icdar (dot) smartdoc (at) gmail (dot) com


### License
The LICENCE file contains the details about the MIT license used.

In a nutshell, it says that you can do whatever you want with the code of this repository as long as:
* you don't hold us liable for anything
* you credit our work properly


