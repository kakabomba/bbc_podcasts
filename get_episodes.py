import download
from bs4 import BeautifulSoup
import os
import re
import math
from datetime import datetime
from subprocess import call

import logging

logging.basicConfig(filename='podcast.log', level=logging.ERROR)


def getel(e, classname, elementname='div'):
    return e.find(elementname, {'class': classname} if classname else None)


def gettext(e, classname, elementname='div'):
    return getel(e, classname, elementname).get_text().strip()


class Eposide():
    file = None
    url_file = None
    title = None
    sortby = None

    def __init__(self, url_file='', title='', sortby='', url_cover=None):
        self.url_file = url_file
        self.url_cover = url_cover
        self.title = title
        self.sortby = sortby

    def download(self, dir, prefix=''):
        origWD = os.getcwd()
        os.chdir(dir)
        file_content = download.get_page(self.url_file, bin=True)
        mp3filename = "{}{}.mp3".format(prefix, self.title)
        file = open(mp3filename, 'xb')
        file.write(file_content)
        file.close()
        if self.url_cover:
            file_content = download.get_page(self.url_cover, bin=True)
            coverfilename = 'covers/' + "{}{}.jpg".format(prefix, self.title)
            file = open(coverfilename, 'xb')
            file.write(file_content)
            file.close()
            call(["eyeD3", "--quiet", "--force-update", "--remove-all-images", mp3filename])
            call(["eyeD3", "--quiet", "--force-update", "--add-image",
                  '{}:FRONT_COVER:{}'.format(coverfilename, prefix), mp3filename])
        os.chdir(origWD)
        print("{}{}.mp3".format(prefix, self.title))

    def __str__(self):
        return "{} {} {}".format(self.title, self.sortby, self.url_file)


class Podcast():
    homepage = None
    directory = None
    title = None
    artist = None
    episodes = []

    def __init__(self, homepage='', directory='./podcasts'):
        self.homepage = homepage
        self.directory = directory
        self.downloadpage = self.homepage + '/episodes/downloads'
        self.download_homepage()
        self.create_dir()
        self.download_episodes()

    def download_episodes(self):
        pass

    def create_dir(self):
        try:
            d = re.sub(r"[^\w\-\s]", "_", self.title).strip()
            self.directory = self.directory + '/' + d
            os.mkdir(self.directory)
            os.mkdir(self.directory + '/covers')
            print("Directory `{}` created".format(self.directory))
        except:
            logging.error("Directory `{}` creation error".format(self.directory))

    def download_homepage(self):
        page = BeautifulSoup(download.get_page(self.homepage), 'html.parser')
        self.title = page.find('div', {'class': 'br-masthead__title'}).get_text()
        self.artist = 'BBC'

    def download_episodes(self):
        def dt(text):
            try:
                return datetime.strptime(text, '%a %d %b %Y').timestamp()
            except:
                return 99999999999.0

        pagetodownload = 1
        url = self.downloadpage
        while pagetodownload > 0:
            page = BeautifulSoup(download.get_page(url), 'html.parser')
            episodes = getel(page, 'component--box--primary').findAll('div', {'class': 'programme--episode'})
            for e in episodes:
                self.episodes.append(
                        Eposide(title=gettext(e, 'programme__titles', 'h4'),
                                sortby=dt(gettext(e, 'programme__service', 'p')),
                                url_cover=getel(e, None, 'meta')['content'],
                                url_file=getel(e, 'buttons__download__link', 'a')['href']))

            nextpageelement = page.find('a', {'title': "Page {}".format(pagetodownload + 1)})
            if nextpageelement:
                pagetodownload = pagetodownload + 1
                url = self.downloadpage + '?page={}'.format(pagetodownload)
            else:
                pagetodownload = 0

        self.episodes = sorted(self.episodes, key=lambda e: e.sortby)

        for ind, e in enumerate(self.episodes):
            try:
                e.download(self.directory,
                           prefix=str(ind + 1).zfill(1 + int(math.floor(math.log10(0.1 + len(self.episodes))))) + '.')
            except:
                logging.error("downloading error episode: {}".format(str(e)))
