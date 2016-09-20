#!/usr/bin/env python

import urllib2
import sys
from bs4 import BeautifulSoup
import imghdr
import os

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
try:
    os.mkdir("data")
except Exception as e:
    os.chdir("data")

def adjustFileNameToWinOS(filename):
    deletechars = u'\/:*?"<>|*'
    for c in deletechars:
        filename = filename.replace(c,u'')
    return filename

def downloadImage(gameName, imageName, url, fType):
    isBg = False

    #imageName = imageName[:imageName.find("-")-1]

    #file_name = url.split('/')[-1]
    if fType == "card":
        imageName = imageName[:imageName.find("- Series")-1]
        file_name = u"{0} [Cards] - {1}{2}".format(gameName, imageName.lstrip(), url[url.rfind("."):])

    else: # fType == bg
        imageName = imageName[:imageName.find("- Type:")-1]
        file_name = u"{0} [Backgrounds] - {1}".format(gameName, imageName.lstrip())
        isBg = True

    #adjustFileNameToWinOS(file_name)
    deletechars = u'\/:*?"<>|*'
    for c in deletechars:
        file_name = file_name.replace(c,u'')

    u = opener.open(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading:   %-100s ||| Size: %7s bytes" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)

        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        #print status,

    f.close()

    #print "\n"

    if isBg:
        bgFileType = imghdr.what(file_name)
        os.rename(file_name, file_name + u".{0}".format(bgFileType))


def main():
    BASEURL = "http://www.steamcardexchange.net/index.php?showcase"

    categoryURLList = ["-filter-ac", "-filter-df", "-filter-gi", "-filter-jl", "-filter-mo", "-filter-pr", "-filter-su", "-filter-vx", "-filter-yz", "-filter-09"]
    gamesDict = {}

    for filterURL in categoryURLList:
        print "Grabbing {}".format(BASEURL + filterURL)
        page = opener.open(BASEURL + filterURL)
        soup = BeautifulSoup(page.read(),"html.parser")

        games = soup.findAll("div", attrs={"class":"showcase-game-item"})

        for game in games:
            gameLink = game.select("a")[0]

            name = gameLink.find("img").get("alt")

            # print gameLink.get("href")
            # print name

            gamesDict[name] = gameLink.get("href")

    temp = sorted(gamesDict.keys())
    start_index = temp.index('Blackwell Epiphany')
    cropped_list = temp[start_index:]
    for key in cropped_list:
        # print "{0}: {1}".format(key.encode("utf-8"), gamesDict[key].encode("utf-8"))
        page = opener.open("http://www.steamcardexchange.net/" + gamesDict[key])
        soup = BeautifulSoup(page.read(),"html.parser")

        # TODO: specify only "TRADING CARDS" section not to do the same work twice
        cards = soup.findAll("a", {"rel":"lightbox-normal"})

        hdBgrounds = soup.findAll("a", {"rel":"lightbox-background"})

        alreadyDoneCardLinks = []
        alreadyDoneBgLinks = []

        for card in cards:
            # This part is ugly...I'll clean it up later
            try:
                hdImageLink = card.get("href")
                #hdImageName = card.findAll("a")[1].get("title")# hdImageName = card.find("span", {"class":"card-name"}).text
                hdImageName = card.get("title")
                if not hdImageLink in alreadyDoneCardLinks:
                    downloadImage(key, hdImageName, hdImageLink, "card")
                    alreadyDoneCardLinks.append(hdImageLink)
                    # print "hdImageLink = {0}".format(hdImageLink)
                    # print "hdImageName = {0}".format(hdImageName)
            except Exception as e:
                print "Card ERROR {0}".format(str(e))
                print key + " - " + hdImageName
                #time.sleep(1)
                continue

        for hdBg in hdBgrounds:
            try:
                hdBgLink = hdBg.get("href")
                #hdBgName = hdBg.findAll("a")[2].get("title")# hdBgName = hdBg.find("span", {"class":"background-name"}).text
                hdBgName = hdBg.get("title")
                if not hdBgLink in alreadyDoneBgLinks:
                    downloadImage(key, hdBgName, hdBgLink, "bg")
                    alreadyDoneBgLinks.append(hdBgLink)
            except Exception as e:
                print "Background ERROR: {0}".format(str(e))
                print key + " - " + hdBgName
                #time.sleep(1)
                continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nStopping..."
        sys.exit(0)
