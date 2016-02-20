import argparse
from get_episodes import Podcast

parser = argparse.ArgumentParser()
parser.add_argument("homepage", default='')
args = parser.parse_args()

Podcast(args.homepage)
