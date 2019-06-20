#!/usr/bin/env python3
""" load images from a subreddit.
    usage: ril.py [-l nn] [-n|-h|-t|-r] [-d] [--logfile LOGFILE] SUBREDDIT TARGETFOLDER
    parameters:
      required:
        SUBREDDIT:    an existing subreddit name (i.e.: earthporn).
        TARGETFOLDER: folder where the images and our trackingfile should be stored.
      optional:
        -l, --limit nn: limit number of images
        -d, --daemonize: run in background
        --logfile: override default logfile location (/var/log/ril.log)
        one of:
          -n, --new
          -h, --hot
          -t, --top
          -r, --random
"""
import os
from os import listdir
from os.path import isfile, join
import errno
import time
import json
import logging
import re
import argparse
import html
import requests
import PIL
from PIL import Image
import pprint


# pylint: disable=invalid-name
# pylint: disable=line-too-long




# if an environmentvariable "DEBUG" exists, set loglevel to DEBUG
ENV_LOGLEVEL_DEBUG = os.environ.get('DEBUG', False)
if ENV_LOGLEVEL_DEBUG:
    LOGLEVEL = logging.DEBUG
    print("loglevel set to DEBUG")
else:
    LOGLEVEL = logging.INFO

# set up logging
log = logging.getLogger(__name__)
lh = logging.StreamHandler()
format_str = '%(asctime)s - %(levelname)-8s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
lf = logging.Formatter(format_str, date_format)
lh.setFormatter(lf)
log.addHandler(lh)
log.setLevel(LOGLEVEL)


class RedditImageLoader:
    """
    A class which provides methods to retreive images from subreddits.

    Arguments:
        subreddit=str (required)
            a subreddit name (i.e. "earthporn"
        targetfolder=str (requred)
            a path to a folder where the images and our tracking file should
            be stored (i.e. "/tmp/"
        limit=int (optional) default: 10
            limit the number of loaded images
        flair=("new"|"top"|"hot"|"random") (optional)
            a flair to add to the request
        orientation=("landscape"|"portrait") (optional)
            limit downloaded images to a specific orientation
    """
    FLAIRS = [
        "new",
        "top",
        "hot",
        "random",
    ]
    ORIENTATIONS = [
        "landscape",
        "portrait",
    ]
    URL_REDDIT = "https://www.reddit.com"
    HEADERS = {
        'User-agent': 'Reddit Image Loader 1.0',
    }
    IMAGE_WIDTH = 1920

    def __init__(self, **kwargs):
        log.debug("Initializing RIL")
        self.subreddit = kwargs.get("subreddit")
        self.targetfolder = kwargs.get("targetfolder")
        if not os.path.exists(self.targetfolder):
            log.info("TARGETFOLDER does not exists. Creating %s", self.targetfolder)
            try:
                os.makedirs(self.targetfolder)
                log.info("success")
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
        self.limit = kwargs.get("limit", 10)
        self.flair = kwargs.get("flair", False)
        if self.flair and self.flair not in self.FLAIRS:
            raise ValueError("%s not in %s" % (self.flair, self.FLAIRS))
        self.orientation = kwargs.get("orientation", False)
        if self.orientation and self.orientation not in self.ORIENTATIONS:
            raise ValueError("%s not in %s" % (self.orientation, self.ORIENTATIONS))
        self.imagedict = {}
        # construct URL
        self.url = self.URL_REDDIT + "/r/" + self.subreddit
        if self.flair:
            self.url += "/" + self.flair
        self.url += ".json"

    def __repr__(self):
        """ Reutrn self.imagedict as string. """
        return "RedditImageLoader({}, {}, {}, {}, {}, {}".format(self.subreddit,
                                                                 self.targetfolder,
                                                                 self.limit,
                                                                 self.flair,
                                                                 self.orientation,
                                                                 self.imagedict)

    def __str__(self):
        """ Reutrn self.imagedict as a descriptive string. """
        _returnstr = ("RedditImageLoader(SUBREDDIT={}, "
                      "TARGETFOLDER={}, "
                      "limit={}, "
                      "flair={}, "
                      "orientation={}, "
                      "imagedict={})"
                     )
        return _returnstr.format(self.subreddit,
                                 self.targetfolder,
                                 self.limit,
                                 self.flair,
                                 self.orientation,
                                 self.imagedict)

    def load_image_urls(self, **kwargs):
        """ Load image URLs and thread-names (as unique ID) into dict self.imagedict. """
        # adapt url to recursion depth
        after = kwargs.get("after", False)
        if not after:
            _url = self.url
        else:
            _url = self.url + "?after=" + after
        log.info("Loading images from %s", _url)

        # load the json
        _data = json.loads(requests.get(url=_url, headers=self.HEADERS).text)
        if "error" in _data:
            raise RuntimeError("Server returned error: %s" % _data["error"])

        # extract id's and image URLs
        for thread in _data["data"]["children"]:
            # dont load any more images if we reached the limit
            if len(self.imagedict) >= self.limit:
                break
            # extract id, url, height and width from JSON
            _id = thread["data"]["preview"]["images"][0]["id"]
            _img = html.unescape(thread["data"]["preview"]["images"][0]["source"]["url"])
            _height = int(thread["data"]["preview"]["images"][0]["source"]["height"])
            _width = int(thread["data"]["preview"]["images"][0]["source"]["width"])
            # if param "orientation" has been given, skip images which dont comply
            if self.orientation and self.orientation == "landscape":
                if _height > _width:
                    continue
            if self.orientation and self.orientation == "portrait":
                if _height < _width:
                    continue
            # we are good -> append image to our dict
            self.imagedict[_id] = _img
        # if we haven't loaded enough images, recurse
        if len(self.imagedict) < self.limit:
            log.debug("Only loaded %s/%s images, starting recursion.", str(len(self.imagedict)), str(self.limit))
            # prevent spamming of the API
            time.sleep(1)
            # reddit's API gives us the parameter to continue loading after
            # our last request
            self.load_image_urls(after=_data["data"]["after"])

    def download_images(self):
        """ Download the images from self.imagedict. """
        for _id, _url in self.imagedict.items():
            _filename = re.search(r"(?<=/)[\w\-\_]+\.(jpg|png)", _url).group(0)
            _filename = self.targetfolder + "/" + _filename
            if os.path.exists(_filename):
                log.info("File %s already downloaded, skipping download", _filename)
                continue
            log.info("Downloading %s", _url)
            _response = requests.get(_url)
            log.debug(_filename)
            with open(_filename, "wb+") as _f:
                _f.write(_response.content)
                _f.close()
            _img = Image.open(_filename)
            _height = int((float(_img.size[1])*float((self.IMAGE_WIDTH /float(_img.size[0])))))
            log.debug("Resizing %sx%s -> %sx%s", _img.size[0], _img.size[1], self.IMAGE_WIDTH, _height)
            _img = _img.resize((self.IMAGE_WIDTH, _height), PIL.Image.ANTIALIAS)
            _img.save(_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load images from a subreddit.")
    # required arguments
    parser.add_argument("SUBREDDIT",
                        help="An existing subreddid name. I.e.: earthporn")
    parser.add_argument("TARGETFOLDER",
                        help="Folder where the images and our trackingfile should be stored.")
    # optional arguments
    parser.add_argument("-l", "--limit",
                        type=int,
                        default=10,
                        help="limit the number of images to download and keep in TARGETFOLDER")
    parser.add_argument("-d", "--daemonize",
                        action="store_true",
                        default=False,
                        help="run in background")
    # mutual exclusive, optional arguments
    flairgroup = parser.add_mutually_exclusive_group()
    flairgroup.add_argument("-N", "--new",
                            action="store_true",
                            help="Load newest posts.")
    flairgroup.add_argument("-T", "--top",
                            action="store_true",
                            help="Load top posts.")
    flairgroup.add_argument("-H", "--hot",
                            action="store_true",
                            help="Load hot posts.")
    flairgroup.add_argument("-R", "--random",
                            action="store_true",
                            help="Load random posts.")
    args = parser.parse_args()
    log.debug("Arguments: %s", args)

    if args.new:
        flair = "new"
    elif args.hot:
        flair = "hot"
    elif args.top:
        flair = "top"
    elif args.random:
        flair = "random"
    else:
        flair = False

    ril = RedditImageLoader(subreddit=args.SUBREDDIT,
                            targetfolder=args.TARGETFOLDER,
                            limit=args.limit,
                            flair=flair,
                            orientation="landscape")
    # load dict of images from reddit
    ril.load_image_urls()

    log.debug(ril)

    # remove all files which are not in ril.imagedict{}
    _ril_filenames = []
    # extract filenames from ril.imagedict{}
    for _url in ril.imagedict.values():
        _filename = re.search(r"(?<=/)[\w\-\_]+\.(jpg|png)", _url).group(0)
        _filename = args.TARGETFOLDER + "/" + _filename
        _ril_filenames.append(_filename)
    log.debug("Filenames from RIL:\n%s", pprint.PrettyPrinter(indent=2).pformat(_ril_filenames))
    # loop over all files in TARGETFOLDER
    for _localfile in listdir(args.TARGETFOLDER):
        _f = join(args.TARGETFOLDER, _localfile)
        if isfile(_f) and _f not in _ril_filenames:
            log.info("File found, which is not part of our list of images: %s", _f)
            log.info("Removing file")
            try:
                os.remove(_f)
                log.info("Done")
            except OSError as err:
                log.error("Unable to remove file %s", _f)
                log.error(str(err))

    # download images from reddit
    ril.download_images()
