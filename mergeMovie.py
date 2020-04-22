#!/usr/bin/env python
import os
import os.path, time
import shutil
from os import path

count = 0

def checkMediaFile(val,path):
    boolean = False
    for mediaFolder in os.listdir(path):
        if mediaFolder == val:
            boolean = True
    return boolean

#This program has been designed to merge media files from one directory to a directory containing multiple folders that contain media.
#The program will check if the source media file already exists in any folder at the destination path. 
#If not, the source media file's folder will be created at the destination path and the media located at the source file path will be copied over to that newly created folder. 
#Note: It is assumed the files located in the source path follow the naming convention of, media file name (year).extension,
#and that the folders located at the destination path follow the naming convention of, media folder name (year).  

def mergeFiles():
    source = input("Enter the source path of media to be copied: ")
    dest = input("Enter the destination path: ")  
    try:
        for mediaFile in os.listdir(source):
            mediaFilehead, mediaFileSep, mediaFileTail = mediaFile.rpartition(')')
            mediaFolderName = mediaFilehead + mediaFileSep
            if not checkMediaFile(mediaFolderName,dest):
                os.mkdir(dest+mediaFolderName)
                source= source + mediaFile
                dest = dest + mediaFolderName
                print("Copying...\n File: "+source+ " to Folder: " +dest)
                shutil.copy(source, dest)
                count = count + 1
    except (IOError,EOFError,ValueError,FileNotFoundError,ConnectionError,NotADirectoryError,TimeoutError,KeyboardInterrupt) as err:
        print("Error, " +err+ " has occured could not complete Merge")

def main():
    mergeFiles()
    if count != 0:
        print("Merge has completed! "+count+" files have been copied")
    else:
        print("No new files to merge :(")

if __name__ == "__main__":
    main()