#!/usr/bin/env python
import os
import os.path, time
from os import path
from datetime import datetime, timedelta
import datetime

class mediaFile:
  def __init__(self, name, date):
    self.name = name
    self.date = date
   # self.size = 0

files = list()

for mediaFolder in os.listdir("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed"):
    for listFile in os.listdir("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder):
        filedate= time.strftime('%Y/%m/%d/%H', time.localtime(os.path.getmtime("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + listFile)))
        #print(filedate)
        filedate=filedate.split("/")
        filedate= datetime.datetime(int(filedate[0]),int(filedate[1]), int(filedate[2]), int(filedate[3]))
        files.append( mediaFile(listFile,filedate) )
    if len(files) > 1 :
      for fileobj in range(len(files)):
          for nextfileobj in range(fileobj +1, len(files)): 
              #print(files[fileobj].date, files[nextfileobj].date )
              if files[fileobj].date != files[nextfileobj].date:
                 #print(files[fileobj].date, files[nextfileobj].date)
                 if files[fileobj].date < files[nextfileobj].date:
                    #print(files[fileobj].name)
                    if os.path.exists("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + files[fileobj].name):
                       print("Removing File... " + files[fileobj].name)
                       os.remove("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + files[fileobj].name)
                       print("File: " + files[fileobj].name + " has been removed")
                       break
                 else:   
                    if os.path.exists("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + files[nextfileobj].name):
                       print("Removing File... " + files[nextfileobj].name)
                       os.remove("/mnt/c/Users/Frank Mitarotonda/Desktop/Movies/completed/" + mediaFolder + "/" + files[nextfileobj].name)
                       print("File: " + files[nextfileobj].name + " has been removed")
                       break
    files *= 0
                      
 
