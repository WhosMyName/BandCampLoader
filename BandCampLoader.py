""" album trial loader for bandcamp """

import os
import json
import time

import requests

if os.name == "nt":
    SLASH = "\\"
else:
    SLASH = "/"

CWD = os.path.dirname(os.path.realpath(__file__)) + SLASH

def get_file(srcfile, srcurl, counter=0, ftype=0):
    """Function to Downloadad and verify downloaded Files"""
    if counter == 5:
        print("Could not download File:", srcfile, "in 5 attempts")
        return 1
    counter = counter + 1
    if not os.path.isfile(srcfile):
        time.sleep(1)
        print("Downloading", srcurl, "as", srcfile)
        with open(srcfile, "wb") as fifo:#open in binary write mode
            response = requests.get(srcurl)#get request
            fifo.write(response.content)#write to file
        if int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype: #Assumes Error in Download and redownlads File
            print("Redownloading", srcurl, "as", srcfile)
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, counter)
        else: #Assume correct Filedownload
            return 0
    else:
        if int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype: #Assumes Error in Download and redownlads File
            print(srcfile, "was already downloaded but the filesize does not seem to fit -> Redownl0ading")
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, 0)
        else: #Assume correct Filedownload
            print(srcfile, "was downloaded correctly on a previous run")
            return 0

def autocleanse(cleansefile):
    """ Function for safautocleanseer deleting of files """
    if os.path.exists(cleansefile):
        os.remove(cleansefile)
        print("Removed:", cleansefile)
        return
    else:
        print("File", cleansefile, "not deleted, due to File not existing")
        return

def init():
    """ parses and loads files """
    inputurl = input("Please enter the URL of the Album to download:\n")

    artist = inputurl.split(".bandcamp")[0].split("//")[1].title()
    album = inputurl.split("album/")[1].replace("-", " ").title()
    location = artist + " - " + album

    if not os.path.exists(CWD + location):
        os.mkdir(location)

    resp = requests.get(inputurl)
    content = resp.text.split("\n")

    tracklist = []
    inline = False
    for line in content:
        if "var TralbumData" in line:
            inline = True
        elif "trackinfo" in line and inline:
            data = line.split("[")[1].split("]")[0].replace("},{", "}, {").split(", ")
            for track in data:
                tracklist.append(json.loads(track))
            inline = False

    for track in tracklist:
        name = location + SLASH + track["title"] + ".mp3"
        url = track["file"]["mp3-128"]
        get_file(name, url)


def __main__():
    """ MAIN """
    init()

if __name__ == "__main__":
    __main__()
