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
        print(f"Could not download File: {srcfile} in 5 attempts")
        return 1
    counter = counter + 1
    if not os.path.isfile(srcfile):
        time.sleep(1)
        print(f"Downloading {srcurl} as {srcfile}")
        with open(srcfile, "wb") as fifo:#open in binary write mode
            response = requests.get(srcurl)#get request
            fifo.write(response.content)#write to file
        if int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype: #Assumes Error in Download and redownlads File
            print(f"Redownloading {srcurl} as {srcfile}")
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, counter)
        else: #Assume correct Filedownload
            return 0
    else:
        if int(str(os.path.getsize(srcfile)).strip("L")) < 25000 and ftype: #Assumes Error in Download and redownlads File
            print(f"{srcfile} was already downloaded but the filesize does not seem to fit -> Redownl0ading")
            autocleanse(srcfile)
            return get_file(srcfile, srcurl, 0)
        else: #Assume correct Filedownload
            print(f"{srcfile} was downloaded correctly on a previous run")
            return 0

def autocleanse(cleansefile):
    """ Function for safautocleanseer deleting of files """
    if os.path.exists(cleansefile):
        os.remove(cleansefile)
        print(f"Removed: {cleansefile}")
        return
    else:
        print(f"File {cleansefile} not deleted, due to File not existing")
        return

def __main__():
    """ parses and loads files """
    inputurl = input("Please enter the URL of the Album to download:\n")

    artist = inputurl.split(".bandcamp")[0].split("//")[1].title()
    album = None
    if "track" in inputurl:
        album = inputurl.split("track/")[1].replace("-", " ").title()
    else:
        album = inputurl.split("album/")[1].replace("-", " ").title()
    location = artist + " - " + album

    if not os.path.exists(CWD + location):
        os.mkdir(location)

    resp = requests.get(inputurl)
    content = resp.text.split("\n")

    inline = False
    data = None
    for line in content:
        if "application/ld+json" in line:
            inline = True
        elif "mp3-128" in line and inline:
            data = json.loads(line)
            inline = False
        elif "</head>" in line:
            inline = False

    for item in data["track"]["itemListElement"]:
        name = f"{location}{SLASH}{item['item']['name']}.mp3"
        url = None
        for track_property in item["item"]["additionalProperty"]:
            if "value" in track_property and isinstance(track_property["value"], str) and "mp3-128" in track_property["value"]:
                url = track_property['value']
        get_file(name, url)

if __name__ == "__main__":
    __main__()
