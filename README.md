# <img src="https://github.com/justmwest/easyquant/blob/main/Images/EasyQuant.png" width="40"> EasyQuant 

EasyQuant is a GUI-based program for fitting multiple, overlapping gaussian
curves to 2D data. It is mainly used to extract integrated intensities (i.e.,
areas under the curve) from SDS-PAGE gel profiles extracted by imageJ's 'plot
profile' tool.


Originally written by Rickard Hedman ca. ~2012 for the von Heijne lab, it was
later refactored by, and is still maintained by, Justin Westerfield of the same
group. It is a new version of the same software mentioned in (among others):
* https://doi.org/10.7554/eLife.25642
* https://doi.org/10.1073/pnas.2205810119
* https://elifesciences.org/articles/36326
* https://doi.org/10.1038/nsmb.2376
* https://doi.org/10.1002/1873-3468.14562
* https://doi.org/10.7554/eLife.64302


# Installation
I recommend setting up a new conda environment:
```conda create -n easyquant python=3.12```
and then installing other dependencies:
```
conda activate easyquant
conda install scipy tk matplotlib=3.8.0
```
From this environment, you can now start EasyQuant by cloning this repository, cding into it, and then running:
```python3 EasyQuant.py```.

# Usage

## Exporting from ImageJ
First export a gel lane profile (it is easiest if it's limited to a narrow vertical region of the lane) from ImageJ using plot profile (cmd+k on mac) then "save data". 

## Opening files
EasyQuant opens with a file box. Click import and then select the file(s) that you exported from ImageJ. Then, in the list of files, double-click the file you want to start working on. This opens a new window with the data plotted.

## The interactive graph
Right click adds a new gaussian curve. You can move the curve around by clicking and dragging the handle at the peak of the curve. Clicking and dragging while holding down shift changes the width of the curve. You can delete the curve by pressing backspace while the handle is selected.
To automatically fit the displayed curves, you can click the F or type ```f``` on the keyboard. Similarly, to estimate fits from scratch you can click the E or type ```e```.

## Exporting data
Gaussian curve parameters are listed in the box below, which can be exported for further analysis by pressing the floppy disk icon, or ```s```. Exporting creates 3 files in the directory where the ImageJ-created file is located, 1) the graph image with the same name as the file, 2) export.csv, which contains all the parameters shown in the info box, and 3) areas.csv, which only shows the areas. If export is pressed multiple times, new information is appended to the end of the csv files, whereas the image file is overwritten (if [file].png is already saved in the directory). 
