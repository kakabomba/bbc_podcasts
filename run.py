import argparse
from get_episodes import Podcast

parser = argparse.ArgumentParser()
parser.add_argument("homepage", default='')
args = parser.parse_args()

Podcast(args.homepage)

# http://www.bbc.co.uk/programmes/b00srz5b - A Brief History of Mathematics
# http://www.bbc.co.uk/programmes/b006qh6g - Saturday Review
# http://www.bbc.co.uk/programmes/p02s8ykn - Natural Histories (36 + 4 can`t be downloaded - for UK only)
# http://www.bbc.co.uk/programmes/b036f7w2 - BBC Inside Science
# http://www.bbc.co.uk/programmes/b04bwydw - A History of Ideas
# http://www.bbc.co.uk/programmes/b00nrtd2 - A History of the World in 100 Objects (100)
# http://www.bbc.co.uk/programmes/b006qtnz - Word of Mouth
# http://www.bbc.co.uk/programmes/b037x68c - Techno Odyssey
# http://www.bbc.co.uk/programmes/p02nrvk3 - arts and ideas
# http://www.bbc.co.uk/programmes/b006x3hl - The essay (Leading writers on arts, history, philosophy, science, religion and beyond, themed across a week - insight, opinion and intellectual surprise)
