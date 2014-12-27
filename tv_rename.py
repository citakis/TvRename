#!/usr/bin/env python

import os
from guessit import guess_file_info
from pytvdbapi import api


def getFileSeasonEpisode(filename):
    """
    The function takes the video filename as input
    and returns its title, season and episode number
    """
    #the guessit module returns a dictionary with all the information extracted from filename
    fileinfo = guess_file_info(filename)
    # with the correct dictionary keys we retrieve the filename series information
    title = fileinfo[u'series']
    season = fileinfo[u'season']
    episode = fileinfo[u'episodeNumber']
    return title, season, episode


def choiceMenu(listOfOptions, title):
    """
    The function is called when more than one options are available from TVdb.
    The function takes 2 arguements, the list of available options
    and the series title and returns a choice from the user which
    will be an int from 1 to len(listOfOptions)
    """

    print "Search with keyword %s returned more than one results" % title
    print "Please choose the appropriate from the choices below"
    count = 0
    for element in listOfOptions:
        count += 1
        print "#%d is %s" % (count, element)
    choice = raw_input("Select one of the choices: ")
    try:
        choice=int(choice)
    except ValueError:
        print "**************************************"
        print "* Your choice must be a valid number *"
        print "**************************************"
        choiceMenu(listOfOptions, title)
    return choice


def searchTVDB(title, season, episode):
    """
    Takes in the tvshow title, season and episode number
    searches for it in tvdb and returns the a new filename
    """
    l=[]
    new_filename=""
    db = api.TVDB('DF847571C94988F1')
    result = db.search(title, 'en')
    if len(result)==0:
        print "Search did not return any valid results"
    elif len(result)==1:
        tvshow = result[0]
    else:
        choice = choiceMenu(result._result, title)
        try:assert choice < len(result)
        except AssertionError:
            print "**************************************"
            print "* Your choice must be a valid number *"
            print "**************************************"
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


def main():
    filelist = os.listdir(os.getcwd())
    for file in filelist:
        if file[-3:] in ["mp4", "mkv", "avi", "srt"]:
            title, season, episode = getFileSeasonEpisode(file)
            print (title, season, episode)
            new_filename = searchTVDB(title, season, episode)
            print new_filename
            renameFile(file, new_filename)
            ListOfchangedFiles(file, new_filename)

main()

"""
dic=guess_file_info("Arrow.S03E07.HDTV.x264-LOL")
#Search for a show name::
db = api.TVDB('DF847571C94988F1')
result = db.search(dic[u'series'], 'en')
print len(result)
#print result._result

#Obtain a show instance and access the data::
show = result[1]
print show.SeriesName
print len(show)  # List the number of seasons of the show, season 0 is the specials season

#Access individual seasons::
season = show[1]
print len(season)  # List the number of episodes in the season, they start at index 1

print season.season_number

#Access an episode within the season::
episode = season[2]
print episode.EpisodeNumber

print episode.EpisodeName
"""
