# IMPORTING DEPENDENCIES AND LIBRARIES
import pandas as pd
import sqlite3
import glob
import instaScrappy
from selenium import webdriver
import time
import os
import re

def createFinalDataFrame(followers, following, posts_data, followers_data, following_data):
    retFollowers = genericDataFrame('followers', followers)
    retFollowing = genericDataFrame('following', following)
    retPostData = genericDataFrame('postsData', posts_data)
    retFollowersData = genericDataFrame('followersData', followers_data)
    retFollowingData = genericDataFrame('followingData', following_data)

    postData = splitData(retPostData, 'postsData')
    followerData = splitData(retFollowersData, 'followersData')
    followingData = splitData(retFollowingData, 'followingData')

    if (len(followers) > len(following)):
        followDF = retFollowing.merge(retFollowers, how="right", on="ID")
        mergeAnalytics = postData.merge(followDF, how="right", on="ID")
        mergeFollowers = followerData.merge(mergeAnalytics, how="right", on="ID")
        dfToDB = followingData.merge(mergeFollowers, how="right", on="ID")
    elif (len(followers) < len(following)):
        followDF = retFollowers.merge(retFollowing, how="right", on="ID")
        mergeAnalytics = postData.merge(followDF, how="right", on="ID")
        mergeFollowers = followerData.merge(mergeAnalytics, how="right", on="ID")
        dfToDB = followingData.merge(mergeFollowers, how="right", on="ID")
    return dfToDB

def splitData(dataframe, string):
    temp_str = 'USE'
    dataframe[[temp_str, 'DELETE']] = dataframe[string].str.split('\n', n=1, expand=True)
    dataframe = dataframe.drop([string, 'DELETE'], axis=1)
    dataframe = dataframe.rename(columns={temp_str:string})
    dataframe[string].replace('([.])', '', regex=True, inplace=True)
    dataframe[string].replace('([,])', '', regex=True, inplace=True)
    dataframe[string].replace('([k])', '000', regex=True, inplace=True)
    dataframe[string].replace('([m])','000000', regex=True, inplace=True)
    dataframe[string] = dataframe[string].astype(int)
    dataframe[string].round()
    return dataframe


def genericDataFrame(string, array):
    genericDF = pd.DataFrame({string:array})
    genericDF["ID"] = range(0, len(genericDF))
    genericDF[string] = genericDF[string].astype('object')
    return genericDF

def createRightTable(instagram_holder, curs, conn):
    instagram_holder = instagram_holder.replace('.', 'idoti')
    curs.execute("DROP TABLE IF EXISTS " + instagram_holder)
    curs.execute("CREATE TABLE " + instagram_holder + """ (
                    id INTEGER NOT NULL PRIMARY KEY,
                    followingData INTEGER,
                    followersData INTEGER,
                    postsData INTEGER,
                    following TEXT,
                    followers TEXT);""")
    conn.commit()

def createLeftTable(instagram_holder, curs, conn):
    instagram_holder = instagram_holder.replace('.', 'idoti')
    curs.execute("DROP TABLE IF EXISTS " + instagram_holder)
    curs.execute("CREATE TABLE " + instagram_holder + """ (
                    id INTEGER NOT NULL PRIMARY KEY,
                    followingData INTEGER,
                    followersData INTEGER,
                    postsData INTEGER,
                    followers TEXT,
                    following TEXT);""")
    conn.commit()

def storeIntoDataBase(instagram_holder, finalDFtoDB):
    instagram_holder = instagram_holder.replace('.', 'idoti')
    instagram_holder = str.upper(instagram_holder)
    path = './instagramInfo.db'
    conn = sqlite3.connect(path)
    curs = conn.cursor()
    if (finalDFtoDB['followers'].count() >= finalDFtoDB['following'].count()):
        createRightTable(instagram_holder, curs, conn)
    elif (finalDFtoDB['followers'].count() < finalDFtoDB['following'].count()):
        createLeftTable(instagram_holder, curs, conn)
    for x in finalDFtoDB.values:
        curs.execute("INSERT INTO " + instagram_holder + """ VALUES (
                        ?,?,?,?,?,?
                        ); """, (x[0], x[1], x[2], x[3], x[4], x[5]))
        conn.commit()
    conn.close()



def findDatabase():
    print("I have found the following database(s)")
    databases = glob.iglob('**/*.db', recursive=True)
    databases = list(databases)
    temp_dir = []
    for i, j in enumerate(databases):
        temp_dir.append(databases[i])
    return temp_dir[0]

def retrieveMenuInfo(curs):
    table_names = curs.execute("SELECT * FROM sqlite_master WHERE type = 'table';")
    for row in table_names.fetchall():
        print(row[1])

def retrieveTableInfo(conn, instagram_holder):
    sql = "SELECT * FROM " + instagram_holder + " ;"
    df = pd.read_sql_query(sql, conn)
    return print(df)

def accountMenu(curs, conn, instagram_holder):
    while(True):
        retrieveTableInfo(conn, instagram_holder)
        print("Please type 'delete' to delete info on table\n'update' to update table\n'retrieve' to retrieve table info\n'return' to go back to main menu")
        menuSelection = input(str("-> "))
        menuSelection = str.lower(menuSelection)
        if (menuSelection == 'delete'):
            # DELETE TABLE INFO
            deleteTableInfo(curs, conn, instagram_holder)
        elif (menuSelection == 'update'):
            # UPDATE TABLE INFO
            updateTableInfo(curs, conn, instagram_holder)
        elif (menuSelection == 'retrieve'):
            # RETIREVE TABLE INFO
            retrieveTableInfo(curs, instagram_holder)
        elif(menuSelection == 'return'):
            # RETURN TO MAIN MENU
            return False
        else:
            print("Invalid option")

def deleteTableInfo(curs, conn, instagram_holder):
    while(True):
        retrieveTableInfo(conn, instagram_holder)
        instagram_holder = str.upper(instagram_holder)
        print("Please type 'id' to delete an id\n'followers' to delete followers\n'following' to delete following\n'postsdata' to delete postsdata\n'return' to go back to main menu")
        menuSelection = input(str("-> "))
        menuSelection = str.lower(menuSelection)
        if (menuSelection == 'id'):
            while(True):
                curs.execute("SELECT id FROM " + instagram_holder + ";")
                selection = input(str("Please type the id to delete or 'return' to return to menu selection -> "))
                selection = str.lower(selection)
                if (selection == 'return'):
                    return False
                else:
                    try:
                        print(int(selection))
                        curs.execute("DELETE FROM " + instagram_holder + " WHERE id = " + selection + ";")
                        conn.commit()
                    except:
                        raise ValueError(print("You entered a non-integer value"))
        elif (menuSelection == 'followers'):
            while(True):
                curs.execute("SELECT followers FROM " + instagram_holder + ";")
                selection = input(str("Please type the follower to delete or 'return' to menu selection -> "))
                selection = selection.lower(selection)
                if (selection == 'return'):
                    return False
                else:
                    try:
                        curs.execute("DELETE FROM " + instagram_holder + " WHERE followers = " + selection + ";")
                        conn.commit()
                    except:
                        raise ValueError(print("You entered a non-valid value"))
        elif (menuSelection == 'following'):
            while(True):
                curs.execute("SELECT following FROM " + instagram_holder + ";")
                selection = input(str("Please type the following to delete or 'return' to return to menu selection"))
                selection = str.lower(selection)
                if (selection == 'return'):
                    return False
                else:
                    try:
                        curs.execute("DELETE FROM " + instagram_holder + " WHERE following = " + selection + ";")
                        conn.commit()
                    except:
                        raise ValueError(print("You entered a non-valid value"))
        elif (menuSelection == 'postsdata'):
            while(True):
                curs.execute("SELECT postsdata FROM " + instagram_holder + ";")
                selection = input(str("Please type the postsdata to delete or 'return' to return to menu selection"))
                selection = str.lower(selection)
                if (selection == 'return'):
                    return False
                else:
                    try:
                        curs.execute("DELETE FROM " + instagram_holder + " WHERE postsdata = " + selection + ";")
                        conn.commit()
                    except:
                        raise ValueError(print("You entered a non-valid value"))
        elif (menuSelection == 'return'):
            return False
        else:
            print("Invalid argument")

def updateTableInfo(curs, conn, instagram_holder):
    while(True):
        retrieveTableInfo(conn, instagram_holder)
        instagram_holder = str.upper(instagram_holder)
        print("Please type an id number to update information or 'return' to go back to main menu")
        menuSelection = input(str("-> "))
        menuSelection = str.lower(menuSelection)
        if (int(menuSelection)):
            while(True):
                curs.execute("SELECT * FROM " + instagram_holder + ";")
                print("Please type 'followers' to update followers\n'following' to update following\n'postsdata' to update posts\n'return' to return to menu selection")
                selection = input(str("-> "))
                selection = str.lower(selection)
                if (selection == 'followers'):
                    curs.execute("SELECT id,followers FROM " + instagram_holder + ";")
                    updateValue = input(str("Please enter new follower info -> "))
                    curs.execute("UPDATE " + instagram_holder + " SET followers = '" + updateValue + "' WHERE id = " + menuSelection + ";")
                    conn.commit()
                elif (selection == 'following'):
                    curs.execute("SELECT id,following FROM " + instagram_holder + ";")
                    updateValue = input(str("Please enter new following info -> "))
                    curs.execute("UPDATE " + instagram_holder + " SET following = '" + updateValue + "' WHERE id = " + menuSelection + ";")
                    conn.commit()
                elif (selection == 'postsdata'):
                    curs.execute("SELECT id,postsData FROM " + instagram_holder + ";")
                    updateValue = input(str("Please enter new postsdata info -> "))
                    curs.execute("UPDATE " + instagram_holder + " SET postsdata = '" + updateValue + "' WHERE id = " + menuSelection + ";")
                    conn.commit()
                elif (selection == 'return'):
                    return False
                else:
                    print("Invalid argument")
        elif (menuSelection=='return'):
            return False
        else:
            print("Invalid argument")
                
                

def mainMenu():
    while(True):
        # FINDING DATABASES
        dirpath = findDatabase()
        action = input(str("Please type 'database' to open database\n'webscrape' to webscrape\n or 'quit' to exit program -> "))
        action = str.lower(action)
        if (action == 'database'):
            path = os.path.abspath(dirpath)
            conn = sqlite3.connect(path)
            curs = conn.cursor()
            # RETRIEVING DATABASE TABLES
            retrieveMenuInfo(curs)
            instagram_holder = input(str("Please select a table to open -> "))
            instagram_holder = str.upper(instagram_holder)
            accountMenu(curs, conn, instagram_holder)
        elif (action == 'webscrape'):
            DRIVER_PATH = './chromedriver.exe'
            wd = webdriver.Chrome(executable_path=DRIVER_PATH)
            time.sleep(5)
            wd.get('https://www.instagram.com/accounts/login/')
            time.sleep(5)
            instaScrappy.instagramLogin(wd)
            directory = input(str("Please enter a name for folder to hold photos -> "))
            instaScrappy.makeMainDirectory(directory)
            while(True):
                action = input(str("Please enter an instagram account for me to find or 'return' to return to menu -> "))
                action = str.lower(action)
                if (action == 'return'):
                    wd.close()
                    break
                else:
                    instaScrappy.getInstagramAccount(action, wd)
        elif(action == 'quit'):
            return False
        else:
            print("Invalid option")
