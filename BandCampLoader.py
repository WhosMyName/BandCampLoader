""" Track/Album Downloader for https://bandcamp.com """

import os
import json
import time
from html import unescape
from concurrent import futures

import requests


if os.name == "nt":
    SLASH = "\\"
else:
    SLASH = "/"

CWD = os.path.dirname(os.path.realpath(__file__)) + SLASH

def get_file(srcfile, srcurl, counter=0, ftype=0) -> bool:
    """Function to Downloadad and verify downloaded Files"""
    if counter == 5:
        print(f"Could not download File: {srcfile} in 5 attempts")
        return False
    counter = counter + 1
    if not os.path.isfile(srcfile):
        time.sleep(1)
        print(f"Downloading {srcurl} as {srcfile}")
        with open(srcfile, "wb") as fifo:  # open in binary write mode
            response = requests.get(srcurl)  # get request
            fifo.write(response.content)  # write to file
        if (
            int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype
        ):  # Assumes Error in Download and redownlads File
            print(f"Redownloading {srcurl} as {srcfile}")
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, counter)
        else:  # Assume correct Filedownload
            return True
    else:
        if (
            int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype
        ):  # Assumes Error in Download and redownlads File
            print(
                f"{srcfile} was already downloaded but the filesize does not seem to fit -> Redownl0ading"
            )
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, 0)
        else:  # Assume correct Filedownload
            print(f"{srcfile} was downloaded correctly on a previous run")
            return True


def autocleanse(cleansefile) -> None:
    """Function for safautocleanseer deleting of files"""
    if os.path.exists(cleansefile):
        os.remove(cleansefile)
        print(f"Removed: {cleansefile}")


def __main__():
    """parses and loads files"""
    # inputurl = input("Please enter the URL of the Album to download:\n")
    inputurl = "https://riotjazz.bandcamp.com/album/on-tour"

    artist = inputurl.split(".bandcamp")[0].split("//")[1].title()
    album = None
    if "track" in inputurl:
        album = inputurl.split("track/")[1].replace("-", " ").title()
    else:
        album = inputurl.split("album/")[1].replace("-", " ").title()
    location = f"{CWD}{artist} - {album}{SLASH}"

    if not os.path.exists(location):
        os.mkdir(location)


    content = requests.get(inputurl).text.split("\n")
    for line in content:
        if "data-tralbum=\"" in line:
            unescaped_line = unescape(line.split("data-tralbum=\"")[1].split("\"")[0])
            data = json.loads(unescaped_line)

    tracklist = [{f"{location}{track['title']}.mp3": track["file"]["mp3-128"]} for track in data["trackinfo"]]
    with futures.ThreadPoolExecutor() as executor:
        for track in tracklist:
            for name, track_url in track.items():
                if track_url:
                    thread_kwargs: dict = {
                    "srcfile": name,
                    "srcurl": track_url
                    }
                    executor.submit(get_file, **thread_kwargs)
                else:
                    print(f"Failed downloading {name}\nNo URL qwq")


if __name__ == "__main__":
    __main__()
