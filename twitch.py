import requests
import json
import os.path
import time
import pandas as pd

#headers = {'Client-ID': '<your token>',}
followYesList, followNoList, userList, idList = [], [], [], []
usersInChat, amountOfViewers = 0, 0

def inputFunction():
    twitchLink = input("Twitch link?\nType q to quit\n")
    channelName = twitchLink.replace("https://www.twitch.tv/","")
    if channelName == "q":
        exit
    else:
        liveFunction(channelName)
    
def liveFunction(channelName):
    paramsForLive = (("user_login", channelName),)
    try:
        responseForLive = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=paramsForLive)
    except requests.exceptions.RequestException as e:
        try:
            responseForLive = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=paramsForLive)
        except requests.exceptions.RequestException as e1:
            print(e1)
            print("Twitch is not answering...")
            exit
    if responseForLive.status_code == 200:
        liveJson = responseForLive.json()
        if liveJson["data"] != []:
            startTimer(channelName)
        else:
            print("User is not live/found")
            inputFunction()
    else:
        print("ERROR! ResponseForLiveStatus:", responseForLive.status_code)
        exit

def viewersFunction(startTime, channelName):
    paramsForViewers = (("user_login", channelName),)
    try:
        responseViewers = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=paramsForViewers)
    except requests.exceptions.RequestException as e:
        try:
            responseViewers = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=paramsForViewers)
        except requests.exceptions.RequestException as e1:
            print(e1)
            print("Twitch is not answering...")
            exit
    if responseViewers.status_code == 200:
        viewerJson = responseViewers.json()
        for viewers in viewerJson["data"]:
            amountOfViewers = viewers["viewer_count"]
            channelFunction(amountOfViewers, startTime, channelName)
    else:
        print("ERROR! ResponseViewers:", responseViewers.status_code)
        exit

def channelFunction(amountOfViewers, startTime, channelName):
    paramsForChannel = (("login", channelName),)
    try:
        responseIDChannel = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=paramsForChannel)
    except requests.exceptions.RequestException as e:
        try:
            responseIDChannel = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=paramsForChannel)
        except requests.exceptions.RequestException as e1:
            print(e1)
            print("Twitch is not answering...")
            exit
    if responseIDChannel.status_code == 200:
        jsonIDResponseChannel = responseIDChannel.json()
        for dataChannel in jsonIDResponseChannel["data"]:
            channelID = dataChannel["id"]
            userFunction(channelID, amountOfViewers, startTime, channelName)
    else:
        print("ERROR! ResponseIDChannel:", responseIDChannel.status_code)
        exit        
        
def userFunction(channelID, amountOfViewers, startTime, channelName):
    try:
        userResponse = requests.get("https://tmi.twitch.tv/group/user/{}/chatters".format(channelName))
    except requests.exceptions.RequestException as e:
        try:
            userResponse = requests.get("https://tmi.twitch.tv/group/user/{}/chatters".format(channelName))
        except requests.exceptions.RequestException as e1:
            print(e1)
            print("Twitch is not answering...")
            exit
    if userResponse.status_code == 200:
        userJson = userResponse.json()
        userChatters = userJson["chatters"]
        for users in userChatters["viewers"]:
            userList.append(users)
        print(len(userList), "users in chat and", amountOfViewers,"viewers")
        userIDFunction(usersInChat, channelID, amountOfViewers, startTime, channelName)
    else:
        print("ERROR! UserResponse:", userResponse.status_code)
        exit
        
def userIDFunction(usersInChat, channelID, amountOfViewers, startTime, channelName):
    for user in userList:
        usersInChat += 1
        print("%.2f" % (usersInChat / (len(userList*2)) * 100), "%",end="\r")
        paramsForUsers = (("login", user),)
        try:
            responseID = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=paramsForUsers, timeout=0.5)
        except requests.exceptions.RequestException as e:
            print(e)
            print("Trying again user",user)
            try:
                responseID = requests.get('https://api.twitch.tv/helix/users', headers=headers, params=paramsForUsers, timeout=5)
            except requests.exceptions.RequestException as e1:
                print(e1)
                print("Not trying user",user,"again...")
                continue
            continue
        if responseID.status_code == 200:
            jsonIDResponse = responseID.json()
            for data in jsonIDResponse["data"]:
                idList.append(data["id"])
        else:
            print("ERROR! ResponseID:", responseID.status_code)
            exit
    followFunction(usersInChat, channelID, amountOfViewers, startTime, channelName)
    
def followFunction(usersInChat, channelID, amountOfViewers, startTime, channelName):
    for userID in idList:
        usersInChat += 1
        print("%.2f" % (usersInChat / (len(userList*2)) * 100), "%",end="\r")
        paramsForID = (("from_id", userID),("to_id", channelID),)
        try:
            responseFollow = requests.get('https://api.twitch.tv/helix/users/follows', headers=headers, params=paramsForID, timeout=0.5)
        except requests.exceptions.RequestException as e:
            print(e)
            print("Trying again user ID",userID)
            try:
                responseFollow = requests.get('https://api.twitch.tv/helix/users/follows', headers=headers, params=paramsForID, timeout=5)
            except requests.exceptions.RequestException as e1:
                print(e1)
                print("Not trying user ID",userID,"again...")
                continue
            continue
        if responseFollow.status_code == 200:
            jsonFollowResponse = responseFollow.json()
            if jsonFollowResponse["total"] == 0:
                followNoList.append("0")
            elif jsonFollowResponse["total"] == 1:
                followYesList.append("1")
            else:
                print("Something went wrong")
                exit
        else:
            print("ERROR! ResponseFollow", responseFollow.status_code)
            exit
    calculateAndWrite(amountOfViewers, startTime, channelName)
            
def calculateAndWrite(amountOfViewers, startTime, channelName):
    percentFollows = round((len(followYesList) / len(userList) * 100),2)
    percentNotFollow = round((len(followNoList) / len(userList) * 100),2)
    print(len(followYesList), "/", len(userList),"=", percentFollows,"{}".format("%"), "of the users in the chat are following")
    print(len(followNoList), "/", len(userList),"=", percentNotFollow,"{}".format("%"), "of the users in the chat are not following")
    # If you want to write your findings into a csv file

    #if os.path.exists("C:/Users/knappe/Desktop/twitchFollowers.csv") == False:
        #twitchFollowersDF = pd.DataFrame({"Follows": percentFollows,"Amount1": len(followYesList),"Does not follow": percentNotFollow,"Amount2": len(followNoList),"Viewers": amountOfViewers}, index=[channelName])
        #twitchFollowersDF.to_csv("C:/Users/knapp/Desktop/twitchFollowers.csv", encoding="utf-8")
    #else:
        #twitchFollowersDF = pd.DataFrame({"     ": percentFollows,"    ": len(followYesList),"   ": percentNotFollow,"  ": len(followNoList)," ": amountOfViewers}, index=[channelName])
        #with open("C:/Users/knappe/Desktop/twitchFollowers.csv", "a", newline="", encoding="utf-8") as twitchFollowersFile:
            #twitchFollowersDF.to_csv(twitchFollowersFile, encoding="utf-8")
    endTime(startTime)
        
def startTimer(channelName):
    startTime = time.time()
    viewersFunction(startTime, channelName)
    
def endTime(startTime):
    finalTime = int(time.time() - startTime)
    finalTime = finalTime % (24 * 3600)
    hour = finalTime // 3600
    finalTime %= 3600
    minutes = finalTime // 60
    finalTime %= 60
    seconds = finalTime
    print("The script ran for",("%d" % (hour)),"hours",("%d" % (minutes)),"minutes",("%d" % (seconds)),"seconds")
    
inputFunction()
