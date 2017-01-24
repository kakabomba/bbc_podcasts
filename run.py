import argparse
from get_episodes import Podcast

parser = argparse.ArgumentParser()
parser.add_argument("homepage", default='')
args = parser.parse_args()

Podcast(args.homepage)

# http://www.bbc.co.uk/programmes/b00srz5b - A Brief History of Mathematics
# http://www.bbc.co.uk/programmes/b006qh6g - Saturday Review
# http://www.bbc.co.uk/programmes/p02s8ykn - Natural Histories (36 + 4 can`t be downloaded - for UK only)


# http://www.bbc.co.uk/programmes/b006qtnz - Word of Mouth
# http://www.bbc.co.uk/programmes/b037x68c - Techno Odyssey

# http://www.bbc.co.uk/programmes/p02nrvk3 - arts and ideas
# The best of BBC Radio 3's flagship arts and ideas programme Free Thinking - featuring in-depth interviews and debates with artists, scientists and public figures.
# 241 files

# http://www.bbc.co.uk/programmes/b006x3hl - The essay
# Leading writers on arts, history, philosophy, science, religion and beyond, themed across a week - insight, opinion and intellectual surprise
#

# http://www.bbc.co.uk/programmes/b036f7w2 - BBC Inside Science
# Dr Adam Rutherford and guests illuminate the mysteries and challenge the controversies behind the science that's changing our world.
#

# http://www.bbc.co.uk/programmes/b00nrtd2 - A History of the World in 100 Objects
# The British Museum's Neil MacGregor presents. Catch up on a week's programmes and explore how five artefacts tell a story of civilisations and connections.
# 100 files

# http://www.bbc.co.uk/programmes/b04bwydw - A History of Ideas
# Melvyn Bragg and guests discuss the work of key philosophers and their theories.
# 60 files