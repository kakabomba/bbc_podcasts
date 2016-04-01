import download
from bs4 import BeautifulSoup
import os
import re
import math
from datetime import datetime
from subprocess import call
import glob


# import logging
#
# logging.basicConfig(filename='podcast.log', level=logging.ERROR)


def getel(e, classname, elementname='div'):
    return e.find(elementname, {'class': classname} if classname else None)


def gettext(e, classname, elementname='div'):
    return getel(e, classname, elementname).get_text().strip()


class Eposide():
    file = None
    url_file = None
    title = None
    sortby = None
    description = None

    def __init__(self, url_file='', title='', sortby='', url_cover=None, description=''):
        self.url_file = url_file
        self.url_cover = url_cover
        self.title = title
        self.sortby = sortby
        self.description = description

    def download(self, dir, prefix=''):

        def convert_text(text):
            ret = re.sub(r"[^\(\)\w\-\s&\d,\.;:'—\?]", "_", text).strip()
            ret = re.sub(r"\n", ". ", ret)
            ret = re.sub(r"^[\s\._]+", "", ret)
            ret = re.sub(r"[\s\._]+$", "", ret)
            ret = re.sub(r"[:]", ".", ret)
            ret = re.sub(r"\s+", " ", ret)
            print("{} -> {}".format(text, ret))
            return ret

        title = convert_text(self.title)
        description = convert_text(self.description)
        if re.match(r"[^d]+_[^d]+_[^d]+", title):
            filename = description if description else title
        else:
            filename = title

        mp3filename = "{} {}.mp3".format(prefix, filename)
        coverfilename = 'covers/' + "{} {}.jpg".format(prefix, filename)

        fileswithsameprefix = glob.glob("{}*".format(prefix))
        if len(fileswithsameprefix):
            print("File `{}*` exists as `{}`".format(prefix, fileswithsameprefix[0]))
            if len(fileswithsameprefix)>1:
                print("Warning! exist more than one file with prefix `{}`".format(prefix))
                for filen in fileswithsameprefix:
                    print("`{}`".format(filen))
            if fileswithsameprefix[0] != mp3filename:
                print("renaming {} -> {}".format(fileswithsameprefix[0], mp3filename))
                os.rename(fileswithsameprefix[0], mp3filename)
            return False

        # if os.path.isfile(mp3filename):
        #     print("File {} exists".format(mp3filename))
        #     return True

        print("! #FILE #{} \n".format(prefix))

        # title = re.sub(r"[^\(\)\w\-\s&\d,\.;:']", "_", self.title).strip()
        # title = re.sub(r"\n", ".", title).strip()
        # description = re.sub(r"[^\(\)\w\-\s&\d,\.;:']", "_", self.description).strip()



        # filename = re.sub(r"^[^\w\d]", "", filename)
        # filename = re.sub(r"[^\w\d]$", "", filename)
        # filename = re.sub(r"[']", "`", filename)
        # filename = re.sub(r"[:]", ".", filename)



        file_content = download.get_page(self.url_file, bin=True)
        file = open(mp3filename, 'xb')
        file.write(file_content)
        file.close()
        logfile = open('files.log', 'a')
        logfile.write("{} - url_file=`{}`, title=`{}`, filename=`{}`, mp3_file=`{}`, url_cover=`{}`\n"
                   .format(prefix, self.url_file, title, filename, mp3filename, self.url_cover))
        if self.url_cover:
            if os.path.isfile(coverfilename):
                os.remove(coverfilename)
            file_content = download.get_page(self.url_cover, bin=True)
            file = open(coverfilename, 'xb')
            file.write(file_content)
            file.close()
            shcommand = ["eyeD3", "--quiet", "--force-update", "--remove-all-images", mp3filename]
            print(" ".join(shcommand))
            logfile.write(" ".join(shcommand))

            call(shcommand)
            shcommand = ["eyeD3", "--quiet", "--force-update", "--add-image",
                  '{}:FRONT_COVER:{}'.format(coverfilename, prefix), mp3filename]
            print(" ".join(shcommand))
            logfile.write(" ".join(shcommand))
            call(shcommand)


        logfile.close()


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
            print("Directory `{}` creation error".format(self.directory))

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
        pagesnum = 1
        url = self.downloadpage
        while pagetodownload <= pagesnum:

            trying = 1
            while trying < 10:
                try:
                    toadd = []
                    page = BeautifulSoup(download.get_page(url), 'html.parser')
                    if pagetodownload == 1:
                        pagelast = page.find('li', {'class': 'pagination__page--last'})
                        if pagelast:
                            pagesnum = int(pagelast.find('a')['title'].replace("Page ", ''))
                    episodes = getel(page, 'component--box--primary').findAll('div', {'class': 'programme--episode'})
                    for e in episodes:
                        toadd.append(
                                Eposide(title=gettext(e, 'programme__titles', 'h4'),
                                        description=gettext(e, 'text--subtle', 'p'),
                                        sortby=dt(gettext(e, 'programme__service', 'p')),
                                        url_cover=getel(e, None, 'meta')['content'],
                                        url_file=getel(e, 'buttons__download__link', 'a')['href']))

                    pagetodownload += 1
                    trying = 11

                except Exception as inst:
                    print(inst)
                    trying += 1

            for e in toadd:
                self.episodes.append(e)

            url = self.downloadpage + '?page={}'.format(pagetodownload)

            # nextpageelement = page.find('a', {'title': "Page {}".format(pagetodownload + 1)})
            # if nextpageelement:
            #     pagetodownload = pagetodownload + 1
            #     url = self.downloadpage + '?page={}'.format(pagetodownload)
            # else:
            #     pagetodownload = 0

        self.episodes = sorted(self.episodes, key=lambda e: e.sortby)

        for ind, e in enumerate(self.episodes):
            origWD = os.getcwd()
            os.chdir(self.directory)
            try:
                # e.download(self.directory, prefix=str(ind + 1).zfill(1 + int(math.floor(math.log10(0.1 + len(self.episodes))))) + '.')
                e.download(self.directory, prefix=str(ind + 1).zfill(3) + '.')
            except Exception as exp:
                print("downloading error {} episode: {}".format(exp, str(e)))
            os.chdir(origWD)
