asf_cherry_pick
===============

The Alaska Sar Fundation mirrors the sentinel1 data from the ESA. For a given acquisition, 
data are provided as a zip file. 

We provide here a script (and an API) that can fetch data into the zip file, allowing to
download only the product of interest. This is useflull either for downloading meta data 
or only the tiff file of interest (e.g. only one polarization and one sub swath). 

Elements to fetch are describe as a pattern (in the sens of regular expression). 

The set of product are given either 

- a file in kml format (that contains a polygon which represent the region of interest)
- a file containing the list of zip files to fetch 
- a file containing the list of urls

Installation
------------

- Unzip the file.
- create a virtual env environment (e.g. python3 -m venv asf_cherry_pick)
- go to the directory in asf_cherry_pick where the setup.py lies
- run the command **pip install .**

Upon installation, you will have access to the script asf_cherry_pick. 

Run **asf_cherry_pick -h** and **asf_cherry_pick -H** for a more detail help. 

Enjoy. 

