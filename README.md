# reddit-image-loader
A Python 3 class and script todownload images from subreddits.

## As a script: ##
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

## As a class: ##
```python
import ril
my_ril = RedditImageLoader(subreddit="earthporn", targetfolder="./images" limit=25 flair=new orientation=landscape"
my_ril.load_image_urls()
my_ril.download_images()
```
This will:
* Load a list of 25 (limit) images in landscape-orientation
* Remove all images that are NOT in this list from ./images/
* Download images from the list which are not already downloaded and resize them to 1920xNNNN (preserving the
aspect-ratio)

## Installation ##
### Prerequesites ###
Python 3 has to be installed.
## Setup ##
* Clone Repository: `git clone https://github.com/schbrongx/reddit-image-loader.git`
* Change into git repository: `cd reddit-image-loader`
* Create a virtual environment: `python3 -m venv env`
* Activate the virtual environment: `. ./env/bin/activate`
* Install requirements: `pip install -r requirements.txt`
* Test script: `src/ril.py --help`
