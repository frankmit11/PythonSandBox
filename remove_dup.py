#!/usr/bin/env python
import os
import os.path, time
from os import path

class file:
  def __init__(prop):
    prop.name = 0
    prop.date = 0
    prop.size = 0

files = list()
mediaFile = file()

for mediaFolder in os.listdir("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed"):
    for mediaFile.name in os.listdir("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder):
        print (mediaFile.name)
        mediaFile.date = time.ctime(os.path.getmtime("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + mediaFile.name))
        print(mediaFile.date)
        #files.append(mediaFile.rstrip())
