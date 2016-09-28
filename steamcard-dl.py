#!/usr/bin/env python

import urllib2
import sys
from bs4 import BeautifulSoup
import os
import logging
from PIL import Image
import time

RETRY_TIMES = 10

# Cookie handler
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())


def adjustFileNameToWinOS(filename):
    deletechars = u'\/:*?"<>|\t'
    for c in deletechars:
        filename = filename.replace(c,u'')
    return filename

def downloadImage(gameName, imageName, url, fType):
    if fType == "card":
        imageName = imageName[:imageName.find("- Series")-1]
        file_name = u"{0} [Cards] - {1}".format(gameName, imageName.lstrip())
    else:  # fType == bg
        imageName = imageName[:imageName.find("- Type:")-1]
        file_name = u"{0} [Backgrounds] - {1}".format(gameName, imageName.lstrip())

    file_name = adjustFileNameToWinOS(file_name)

    for i in range(RETRY_TIMES):
        try:
            u = opener.open(url)
            break
        except (urllib2.HTTPError,urllib2.URLError) as e:
            logging.debug(u"Address from %s was not available when tried to download. Error: %s", gameName, e)

    f = open(file_name, 'wb')

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)

        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)

    f.close()

    imgFileType = Image.open(file_name).format.lower()
    i = 0
    file_name_new = file_name
    while os.path.isfile(file_name_new + u".{0}".format(imgFileType)):
        i += 1
        file_name_new = file_name + u" [{0}]".format(i)
    file_name_new = file_name_new + u".{0}".format(imgFileType)
    os.rename(file_name, file_name_new)

    print u"Downloaded:   %-100s ||| Size: %7s bytes" % (file_name_new, os.stat(file_name_new).st_size)


def main():
    try:
        os.mkdir("data")
        os.chdir("data")
    except Exception as e:
        os.chdir("data")

    logging.basicConfig(filename='Errors.log',format='%(asctime)s | %(levelname)s | %(message)s',level=logging.DEBUG)

    BASEURL = "http://www.steamcardexchange.net/index.php?showcase"

    categoryURLList = ["-filter-ac", "-filter-df", "-filter-gi", "-filter-jl", "-filter-mo", "-filter-pr", "-filter-su", "-filter-vx", "-filter-yz", "-filter-09"]
    gamesDict = {}

    for filterURL in categoryURLList:
        print u"Grabbing {}".format(BASEURL + filterURL)
        try:
            page = opener.open(BASEURL + filterURL)
        except (urllib2.HTTPError,urllib2.URLError) as e:
            logging.debug(u'Grabbing %s failed. Error: %s', filterURL, e)
            continue

        soup = BeautifulSoup(page.read(),"html.parser")

        games = soup.findAll("div", attrs={"class":"showcase-game-item"})

        for game in games:
            gameLink = game.select("a")[0]
            name = gameLink.find("img").get("alt")
            gamesDict[name] = gameLink.get("href")

    temp = sorted(gamesDict.keys())
    start_index = 0             #temp.index('God Mode')
    finish_index = len(temp)    #temp.index('TurnOn')
    cropped_list = temp[start_index:finish_index]
    for key in cropped_list:
        for i in range(RETRY_TIMES):
            try:
                page = opener.open("http://www.steamcardexchange.net/" + gamesDict[key])
            except (urllib2.HTTPError,urllib2.URLError) as e:
                logging.debug(u'Game "%s" page is not available. Error: %s', key, e)
                time.sleep(1)

        soup = BeautifulSoup(page.read(),"html.parser")

        cards = soup.findAll("a", {"rel":"lightbox-normal"})

        hdBgrounds = soup.findAll("a", {"rel":"lightbox-background"})

        alreadyDoneCardLinks = []
        alreadyDoneBgLinks = []

        for card in cards:
            try:
                hdImageLink = card.get("href")
                hdImageName = card.get("title")
                if not hdImageLink in alreadyDoneCardLinks:
                    for i in range(RETRY_TIMES):
                        try:
                            downloadImage(key, hdImageName, hdImageLink, "card")
                            break
                        except (urllib2.HTTPError,urllib2.URLError) as e:
                            logging.debug(u'Address of "%s" is not available. Error: %s', hdImageName, e)
                            time.sleep(1)
                    alreadyDoneCardLinks.append(hdImageLink)
            except Exception as e:
                print u"Card ERROR: {0}".format(str(e))
                logging.debug(u'Another weird error occurred for "%s". Error: %s', key, e)
                if str(e) == u"[Errno 28] No space left on device":
                    sys.exit(1)

        for hdBg in hdBgrounds:
            try:
                hdBgLink = hdBg.get("href")
                hdBgName = hdBg.get("title")
                if not hdBgLink in alreadyDoneBgLinks:
                    for i in range(RETRY_TIMES):
                        try:
                            downloadImage(key, hdBgName, hdBgLink, "bg")
                            break
                        except (urllib2.HTTPError,urllib2.URLError) as e:
                            logging.debug(u'Address of "%s" is not available. Error: %s', hdBgName, e)
                            time.sleep(1)
                    alreadyDoneBgLinks.append(hdBgLink)
            except Exception as e:
                print u"Background ERROR: {0}".format(str(e))
                logging.debug(u'Another weird error occurred for "%s". Error: %s', key, e)
                if str(e) == u"[Errno 28] No space left on device":
                    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nStopping..."
        sys.exit(0)
