# reddit-image-loader
A Python 3 class and script to download images from subreddits.

# Table of contents
1. [Usage as a script](#usage_script)
2. [Usage as a class](#usage_class)
3. [Installation](#installation)
    1. [Prerequesites](#prerequesites)
    2. [Setup](#setup)

## Usage as a script: ##
<a name="usage_script" />
Usage: `ril.py [-h] [-l LIMIT] [-d] [-N | -T | -H | -R] SUBREDDIT TARGETFOLDER`

Positional arguments:
* SUBREDDIT             An existing subreddid name. I.e.: earthporn
* TARGETFOLDER          Folder where the images and our trackingfile should be
                        stored.

Optional arguments:
* -h, --help: show this help message and exit
* -l LIMIT, --limit LIMIT: limit the number of images to download and keep in TARGETFOLDER
* -d, --daemonize: run in background
* -N, --new: Load newest posts.
* -T, --top: Load top posts.
* -H, --hot: Load hot posts.
* -R, --random: Load random posts.

Example:
`ril.py -l 5 -T earthporn ./images`
This will:
* Load a list of 5 images in landscape-orientation
* Remove all images, which are not in our list, from ./images/
* Download all images from our list, which are not already in ./images and
* Resize them to 1920xNNNN, preserving the ascpet-ration

## Usage as a class: ##
<a name="usage_class" />
```python
import ril
my_ril = RedditImageLoader(subreddit="earthporn", targetfolder="./images" limit=25 flair=new orientation=landscape"
my_ril.load_image_urls()
my_ril.download_images()
```
This will:
* Load a list of 25 (limit) images in landscape-orientation
* Download images from the list which are not already downloaded and resize them to 1920xNNNN (preserving the
aspect-ratio)

## Installation ##
<a name="installation" />
### Prerequesites ###
<a name="prerequesites" />
Python 3 has to be installed.
## Setup ##
<a name="setup" />
* Clone Repository: `git clone https://github.com/schbrongx/reddit-image-loader.git`
* Change into git repository: `cd reddit-image-loader`
* Create a virtual environment: `python3 -m venv env`
* Activate the virtual environment: `. ./env/bin/activate`
* Install requirements: `pip install -r requirements.txt`
* Test script: `src/ril.py --help`
