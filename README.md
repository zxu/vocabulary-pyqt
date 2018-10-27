# Vocabulary Flashcard
This small program is aiming to assist with memorising words. It just loops through a group of CSV files and presents each of the words in them in random order.

The GUI is initially designed using Qt Creator and exported as Python source file using the `pyuic5` commiand-line utility. (`pyuic5 ./mainwindow.ui -o ./mainwindow.py`). Then the main logic is implemented using Python and PyQt.

## Environment Preparation for PyQt Development on Mac
1. Install `miniconda`: `sh ./Miniconda3-latest-MacOSX-x86_64.sh`
1. Create a Conda environment: `conda create --name pyqt python=3.7`
1. Activate the newly created environment: `source activate pyqt`
1. Search PyQt for its latest version: `conda search -f pyqt`
1. Install the latest version of PyQt: `conda install pyqt=5.9.2`
1. Install `pandas`: `conda install pandas`