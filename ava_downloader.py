# python3 ava_downloader.py beginIndex endIndex

from urllib.request import urlopen, urlretrieve
import re
import sys
import os
import json

URLprefix = r'http://www.dpchallenge.com/image.php?IMAGE_ID='
AVADataPath = r'AVA.txt'
savePath = r'image'
tagsPath = r'tags.txt'
jsonFilePath = r'image_data.json'


def getHtml(url):
    page = urlopen(url)
    html = page.read()
    return html


def schedule(a, b, c):
    percent = 100.0 * a * b / c
    if percent > 100:
        percent = 100
    print('%.2f%%' % percent)


# fetch image, save to file
def getImg(html, imageID, imageIndex):
    reg = r'//.*?' + imageID + r'\.jpg'
    imgre = re.compile(reg)
    imglist = re.findall(imgre, html)
    for imgurl in imglist:
        imgurl = "https:" + imgurl
        print(imgurl)
        urlretrieve(imgurl, os.path.join(savePath, imageIndex + '.jpg'), schedule)

def saveJSON(imageID, imageIndex, ratingsCounts, tagIds, challengeId):
    if os.path.isfile(jsonFilePath) == True:
        with open(jsonFilePath, 'r') as f:
            jsonData = json.load(f)
    else:
        print(f"No file found for {jsonFilePath}. Creating one...")
        jsonData = {}
    
    ratings = []
    for i in range(0, len(ratingsCounts)):
        for _ in range(0, int(ratingsCounts[i])):
            ratings.append(i + 1)
    
    if len(ratings) == 0:
        median_rating = 0
        mean_rating = 0
    else:
        if len(ratings) % 2 == 1:
            median_rating = ratings[len(ratings) // 2]
        else:
            median_rating = (ratings[len(ratings) // 2] + ratings[len(ratings) // 2 + 1]) / 2

        mean_rating = sum(ratings) / len(ratings)

    image_tags = []
    for tag_id in tagIds:
        if tag_id != "0":
            image_tags.append(tags[tag_id])

    jsonData[imageID] = {
        "file_path": os.path.join(savePath, imageIndex + '.jpg'),
        "median_rating": median_rating,
        "mean_rating": mean_rating,
        "tags": image_tags
    }

    with open(jsonFilePath, "w") as f:
        json.dump(jsonData, f, indent=4)







if len(sys.argv) < 3:
    print('Usage: python3 ava_downloader.py beginIndex endIndex')
    exit()

with open(tagsPath, "r") as f:
    tags = {}
    for line in f:
        tag_id, description = line.rstrip().split(" ", maxsplit=1)
        tags[tag_id] = description

beginIndex = int(sys.argv[1])
endIndex = int(sys.argv[2])

with open(AVADataPath, "r") as f:
    for line in f:
        line = line.strip().split(' ')
        imageIndex = line[0]
        imageID = line[1]
        ratingsCounts = line[2:12]
        tagIds = line[12:14]
        challengeId = line[14]

        if int(imageIndex) < beginIndex:
            continue
        elif int(imageIndex) > endIndex:
            break

        if os.path.isfile(os.path.join(savePath, imageIndex + '.jpg')) == True:
            continue

        URL = URLprefix + imageID
        html = getHtml(URL)
        try:
            html = html.decode("utf-8")
        except UnicodeDecodeError as e:
            print("Error decoding HTML for image ID ", imageID, e)
            continue
        if "Page cannot be served due to suspicious activity detected from your address." in html:
            print("Cannot fetch - website has detected webscraping :/. Quitting.")
            break

        getImg(html, imageID, imageIndex)
        saveJSON(imageID, imageIndex, ratingsCounts, tagIds, challengeId)
        print(f'image{imageIndex} success')
