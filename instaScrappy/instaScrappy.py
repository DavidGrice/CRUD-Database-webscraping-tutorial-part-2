# IMPORT DEPENDENCIES/LIBRARIES
import urllib
import urllib3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup as bs
import os
import getpass
import re 
import glob
import databaseFunctions

# Instagram login
def instagramLogin(wd):
    # find element username and password for inputting login info
    user = wd.find_element_by_name("username")
    password = wd.find_element_by_name("password")
    # Clear the fields
    user.clear()
    password.clear()
    # Ask user for login information
    instagram_username = getpass.getpass("Please enter your Instagram user account: ")
    user.send_keys(instagram_username)
    instagram_password = getpass.getpass("Please enter your Instagram password: ")
    password.send_keys(instagram_password)
    time.sleep(5)
    wd.find_element_by_xpath("//button[@type='submit']").click()
    time.sleep(5)
    wd.get('https://www.instagram.com/'+instagram_username+'/')
    time.sleep(5)
    return

# CREATE ONE FOLDER FOR MULTIPLE FOLDERS
def makeMainDirectory(directory):
    main_directory = directory
    if not os.path.isdir(main_directory):
        os.mkdir(main_directory)
        os.chdir(main_directory)
    else:
        os.chdir(directory)
    return

# LOCATING AND STORING INFO FOR INSTAGRAM ACCOUNT
def getInstagramAccount(instagramUsername, wd):
    instagram_holder = instagramUsername
    time.sleep(5)
    wd.get('https://www.instagram.com/'+instagram_holder+'/')
    # scraping photos
    scrapeInstagramAccountImages(instagram_holder, wd)
    print("Their photos have been collected and stored in the directory")
    print(glob.glob('./'+instagram_holder))

    # get inspector
    getInspector()

    # instagram actions
    hrefActions = getInstagramActions(instagram_holder, wd)
    posts_data = getInstagramData(hrefActions, 0)
    followers_data = getInstagramData(hrefActions, 1)
    following_data = getInstagramData(hrefActions, 2)

    # scraping followers
    hrefActions = getInstagramActions(instagram_holder, wd)
    followers = getFollowInformation(hrefActions, wd, 1)

    # scraping following
    hrefActions = getInstagramActions(instagram_holder, wd)
    following = getFollowInformation(hrefActions, wd, 2)
    print("I have collected all of their information and am now creating dataframes!")
    # DF TO DB Function
    finalDFtoDB = databaseFunctions.createFinalDataFrame(followers, following, posts_data, followers_data, following_data)
    # PRINT STATEMENTS
    print("I have made the final dataframe this is how it looks!")
    print(finalDFtoDB)
    # STORING INTO DATABASE
    print("Now I am storing the data into the database!")
    databaseFunctions.storeIntoDataBase(instagram_holder, finalDFtoDB)
    getInspector()
    time.sleep(5)
    return

def getInstagramData(actions, actionNumber):
    regex = re.compile(r'([\n])')
    text_arr = []
    generic = actions[actionNumber].text
    text_arr.append(generic)

    if (actionNumber == 0):
        y = ""
        for i, j in enumerate(text_arr):
            x = re.sub(regex, ' ', text_arr[i])
            y += (str(x) + " ")
        print("They have " + y)
    elif (actionNumber == 1):
        y = ""
        for i, j in enumerate(text_arr):
            x = re.sub(regex, ' ', text_arr[i])
            y += (str(x) + " ")
        print("They have " + y)
    elif (actionNumber == 2):
        y = ""
        for i, j in enumerate(text_arr):
            x = re.sub(regex, ' ', text_arr[i])
            y += (str(x) + " ")
        print("They have " + y)
    return text_arr

def scrapeInstagramAccountImages(instagram_holder,wd):
    time.sleep(5)
    lenOfPage = wd.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage")
    match=False
    x = 0
    instagram_urls = []
    # directory of instagram account
    directory = instagram_holder
    # create directory for instagram account
    if not os.path.isdir(directory):
        os.mkdir(directory)
    while(match == False):
        lastCount = lenOfPage
        time.sleep(15)
        
        instagram_capture = wd.find_elements_by_xpath("//img[@class='FFVAD']")

        if (x >= 1):
            # appending src for images to download
            temp_url = []
            for i in instagram_capture:
                temp_url.append(i.get_attribute('src'))
            temp_url = temp_url[30:]
            for i,k in enumerate(temp_url):
                instagram_urls.append(temp_url[i])
        elif(x==0):
            for i in instagram_capture:
                instagram_urls.append(i.get_attribute('src'))
        
        lenOfPage = wd.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage")
        x += 1
        if (lastCount==lenOfPage):
            match=True
    for i, link in enumerate(instagram_urls):
            path = os.path.join(instagram_holder, '{:06}.jpg'.format(i+x))
            try:
                urllib.request.urlretrieve(link, path)
            except:
                raise ValueError(print("Failure"))

## ACTIONS FOR GETTING FOLLOWER/FOLLOWING
def getInstagramActions(instagram_holder, wd):
    wd.get('https://www.instagram.com/'+instagram_holder+'/')
    time.sleep(5)
    href_temp = wd.find_elements_by_xpath("//li[@class=' LH36I']")
    return href_temp

def getInspector():
    # MAKE SURE THAT YOU HAVE THE CHROME DRIVER CLICKED ON
    from pynput.keyboard import Key, Controller
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press(Key.shift)
    keyboard.press('i')
    keyboard.release(Key.ctrl)
    keyboard.release(Key.shift)
    keyboard.release('i')
    time.sleep(5)

def mouseFunction():
    from pynput.mouse import Button, Controller
    mouse = Controller()
    #mouse.position = (698, 324)
    mouse.press(Button.left)
    mouse.release(Button.left)

def keyboardFunction():
    from pynput.keyboard import Key, Controller
    keyboard = Controller()
    return keyboard

def getFollowInformation(actions, wd, actionNumber):
    from pynput.keyboard import Key
    follow_names = []
    following = actions[actionNumber]
    following.click()
    time.sleep(5)
    lenOfPage = wd.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage")
    match=False
    while(match == False):
        lastCount = lenOfPage
        time.sleep(15)

        lenOfPage = wd.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage")
        if (lastCount==lenOfPage):
            match=True
    # MOUSE FUNCTION
    #mouseFunction()
    # KEYBOARD FUNCTION
    #keyboard = keyboardFunction()
    # LOGIC FOR THE ACTIONS
    #for i in range(0, 100):
    #   keyboard.press(Key.page_down)
    #    time.sleep(1)
    #    keyboard.release(Key.page_down)
    #    time.sleep(1)
    
    follow_temp = wd.page_source
    follow_data = bs(follow_temp, 'html.parser')
    follow_name = follow_data.find_all('a')
    for i in follow_name:
        follow_names.append(i.get("title"))
    # PRINTING FOLLOWER INFORMATION WHICH WAS GATHERED
    if (actionNumber == 1):
        print("I collected " + str(len(follow_names)) + " followers from their account")
    # PRINTING FOLLOWING INFORMATION WHICH WAS GATHERED
    elif (actionNumber == 2):
        print("I collected " + str(len(follow_names)) + " following from their account")
    clean_follow_names = [x for x in follow_names if x != None]
    return clean_follow_names


def main():
    databaseFunctions.mainMenu()

if __name__ == "__main__":
    main()