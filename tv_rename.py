#!/usr/bin/env python

import os
from sys import exc_info
from guessit import guess_file_info
from pytvdbapi import api


def getFileSeasonEpisode(filename):
    """
    The function takes the video filename as input
    and returns its title, season and episode number
    """
    # the guessit module returns a dictionary with all the information extracted from filename
    fileinfo = guess_file_info(filename)
    # with the correct dictionary keys we retrieve the filename series information
    print('Retrieve info from \033[1;34m %s\033[1;m' % filename)
    try:
        title = fileinfo[u'series']
    except KeyError:
        title = raw_input("Tvseries title could not be recognised,\nplease insert one:")
    try:
        season = fileinfo[u'season']
    except KeyError:
        season = int(raw_input("Episode season could not be recognised,\nplease insert one:"))
    try:
        episode = fileinfo[u'episodeNumber']
    except KeyError:
        episode = int(raw_input("episode number could not be recognised,\nplease insert one:"))

    return title, season, episode


def choiceMenu(listOfOptions, title):
    """
    The function is called when more than one options are available from TVdb.
    The function takes 2 arguements, the list of available options
    and the series title and returns a choice (from the user), which
    will be an integer from 1 to len(listOfOptions)
    """

    print("Search with keyword %s returned more than one results" % title)
    print("Please choose the appropriate from the choices below")
    count = 0
    for element in listOfOptions:
        count += 1
        print("#%d is %s" % (count, element))
    choice = raw_input("Select one of the choices: ")
    try:
        choice=int(choice)
    except ValueError:
        print("**************************************")
        print("* Your choice must be a valid number *")
        print("**************************************")
        choiceMenu(listOfOptions, title)
    return choice


def searchTVDB(title, season, episode, filename):
    """
    Takes in the tvshow title, season and episode number
    searches for it in tvdb and returns a new filename
    """
    tvshow = None
    l=[]
    #import your tvdb_api_key in order for the program to work
    db = api.TVDB('tvdb_api_key')
    result = db.search(title, 'en')

    if len(result)==0:
        print "a0"
        print("Search did not return any valid results")
        title, season, episode = refine_search_criteria(title, season, episode, filename)
        searchTVDB(title, season, episode, filename)
    elif len(result)==1:
        tvshow = result[0]
    else:
        tvseriesList = readTVseriesListFile()
        for tv_show in result:
            if tv_show in tvseriesList:
                tvshow = tv_show
        print tvshow
        if tvshow == None:
            choice = choiceMenu(result._result, title)
            try:assert choice < len(result)
            except AssertionError:
                print("**************************************")
                print("* Your choice must be a valid number *")
                print("**************************************")
                choiceMenu(result._result, title)
            tvshow = result[choice-1]
    season = tvshow[season]
    episode = season[episode]
    seasonNumber = season.season_number
    episodeNumber = episode.EpisodeNumber
    if episodeNumber<10:
        episodeNumber="0"+str(episodeNumber)
    episodeName=episode.EpisodeName
    l.append(tvshow.SeriesName)
    l.append("-")

    l.append(str(seasonNumber)+"x"+str(episodeNumber))
    l.append("-")
    l.append(episodeName)
    new_filename = " ".join(l)

    return new_filename


def renameFile(filename, new_filename):
    """a function which renames the file """
    new_filename=new_filename+filename[-4:]
    os.rename(filename, new_filename)


def ListOfchangedFiles(filename, new_filename):
    """ Because sometimes the original filenames may be needed this function makes
     a file in which the original names are stored"""
    f=open("ListOfChangedFiles.txt","a")
    line='"%s" changed to "%s%s"\n' %(filename, new_filename, filename[-4:])
    f.write(line)
    f.close()


def readTVseriesListFile():
    """If user choose a tvseries from the choice menu the choice is stored in a file
    so it will not ask again for the same choice"""
    try:
        data = open("tvseries List.txt","r")
        tvseriesList = []
        discardFirstLine=data.readline()
        for line in data:
            tvseriesList.append(line)
        data.close()
    except IOError:
        tvseriesList = []
    return tvseriesList


def addToTvSeriesList(tvseriesName):
    """ Function takes one arguement a tvseriesName and appends that to the
    'tvseries List.txt' file"""
    try:
        tvseriesListFile = open("tvseries List.txt","a")
        tvseriesListFile.writeline(tvseriesName)
        tvseriesListFile.close()
    except IOError:
        print("'tvseries List.txt' file does not exist")

def isInTVseriesList(tvseriesName, tvSeriesList):
    return tvseriesName in tvSeriesList


def returnCommonElement(listA, listB):
    commonElements=[]
    for element in listA:
        if element in listB:
            commonElements.append(element)
    if len(commonElements)==1:
        return commonElements[0]
    else:
        return None
"""
it makes a list with the files of the directory
and it goes through each of the files
"""

def refine_search_criteria(title, season, episode, filename):
    print('\033[1;34msearched for file %s\033[1;m' %filename)
    print("Searced with tvshow name'%s'" %title)
    new_title = raw_input("Please input a valid title, Enter for no change: ")
    if new_title != "":
        title = new_title

    print("Searced with tvshow season number'%s'" %season)
    new_season = raw_input("Please input a valid season number, Enter for no change: ")
    if new_season != "":
        season = new_season

    print("Searced with tvshow episode number'%s'" %episode)
    new_episode = raw_input("Please input a valid episode number, Enter for no change: ")
    if new_episode != "":
        episode = new_episode
    return title, season, episode

def main():
    filelist = os.listdir(os.getcwd())
    for file in filelist:
        if file[-3:] in ["mp4", "mkv", "avi", "srt"]:
            title, season, episode = getFileSeasonEpisode(file)
            print (title, season, episode)
            try:
                new_filename = searchTVDB(title, season, episode, file)
                print("renamed to \033[1;32m %s\033[1;m \n" %new_filename)
                renameFile(file, new_filename)
                ListOfchangedFiles(file, new_filename)
            except:
                print("\033[1;31m Unexcepted Error:%s " %exc_info()[0])
                print(exc_info()[1])
                print('\033[1;m\n')



if __name__ == '__main__':
    main()
