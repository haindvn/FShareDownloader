
from __future__ import print_function

#from apiclient import errors
from colorama import init,Fore,Back,Style
from termcolor import colored
from get_fshare import FSAPI
from tqdm import tqdm
from requests.exceptions import HTTPError

import configparser 
import os
import sys
import requests
import re

# Requires: get_fshare requests  lxml  hyper apiclient colorama termcolor tqdm
# Debian package: python3-lxml
# libxml2 libxslt

# Main FShare URLs
FShare_File_URL = 'https://www.fshare.vn/file/'
FShare_Folder_URL = 'https://www.fshare.vn/folder/'
re_folder_pattern = r"(https://www\.fshare\.vn/folder/)([^\?]+)(?:(\?.*))?"
re_folder_name_pattern = r"(.*/)(.*)"
File_Indicator = '/file/'
Folder_Indicator = '/folder/'
Folder_Reference_Filename = "Folder_Information.txt"

CONFIG_FILE = "credentials.ini"

service=''


def main():
    splash_screen()
    print(colored('Loading configuration...','white'))
    login_credential = configuration_read(CONFIG_FILE)
    print(colored('Login...','white'))
    login_status = perform_login(login_credential)

    if login_status:
        print(colored('Logged in successfully!','white'))
    else:
        print(colored('Login failed! Please check login credentials in {}'.format(CONFIG_FILE),'white'))
        print(colored('Quit','white'))
        exit()

    if(len(sys.argv))<3:
        # Require user's inputs to to download / ID and location
        
        location = input("Local Path (Enter . for current directory): ")
        while not location:
            location = input("Local Path (Enter . for current directory): ")
        if location[-1] != '/':
            location += '/'
                
        downloadID = input("FShare Folder/File URL: ")
        while not downloadID:
            downloadID = input("FShare Folder/File URL: ")
        
    else:
        downloadID = sys.argv[1]
        location = sys.argv[2]
        if location[-1] != '/':
            location += '/'
    
    # Check file or folder
    if not is_folder(downloadID):
        # It's a file, download it now
        fileInfo = service.get_file_info(downloadID)
        print(colored('File: ','white'),colored('{}'.format(fileInfo['name']),'yellow'))
        # print(f'Saving to {location}')
        download_file(service.download(FShare_File_URL+fileInfo['linkcode']),location,fileInfo['name'])
        print(colored('{} downloaded'.format(fileInfo['name']),'yellow'))

    elif is_folder(downloadID):
        # It's folder, explode and download
        print("Folder detected, recursively download folder")
        download_folder(downloadID,location)
    else:
        print('Error, unknown link')

                
    splash_screen_end()
    exit(0)

def download_folder(url, location):
    """
    Download whole fshare folder / a local folder name with folderID being read from URL will be created if it doesn't exist
    """
    match = re.search(re_folder_pattern,url)
    if match is not None:
        folderID = match.group(2)
    else:
        print(colored("Folder Link error, please make sure it's welformed as https://www.fshare.vn/folder/XXXXXXXXXX (token trail is optional)",'red'))
        return 1
    
    folderList = service.get_folder_urls(url)
    if (len(folderList)) < 1:
        print("Folder empty!")
        return 1

    if not os.path.exists(location + folderID):
        os.makedirs(location + folderID)
    # Update new location to new directory
    location += folderID + "/"

    
    # detect and count sub-folders / we will ignore subfolder
    sub_folder_count = 0
    for fileInfo in folderList:
        if is_folder(fileInfo['furl']):
            sub_folder_count += 1
    if sub_folder_count > 0:
        print(colored("We found {} file(s) and {} sub-folder(s) in the link, we're skipping folder, ONLY FILES will be downloaded!".format(len(folderList)-sub_folder_count,sub_folder_count),'yellow'))

    # We will try to detect the folder name and write it down to the file for reference later
    # Fshare store the name including the parent folder so we have to regex to match

    match = re.search(re_folder_name_pattern,folderList[0]['path'])
    with open(location + Folder_Reference_Filename,"w") as f:
        f.writelines(f"Folder URL: {url} \n")
        f.writelines(f"Folder name: {match.group(2)} \n")
        f.writelines(f"File count: {len(folderList)-sub_folder_count} \n")
        f.writelines(f"Sub-Folder count: {sub_folder_count} \n")

        
    print(colored("We found {} file(s) in the link, download them now".format(len(folderList)-sub_folder_count),'yellow'))
    # loop through whole directory and download
    fileCount = 0
    for fileInfo in folderList:
        if not is_folder(fileInfo['furl']):
            print(colored('File #{}: '.format(fileCount),'white'),colored('{}'.format(fileInfo['name']),'yellow'))
            download_file(service.download(FShare_File_URL+fileInfo['linkcode']),location,fileInfo['name'])
            fileCount += 1
    
def download_file(url, location,filename):
    """
    Download a particular file from with direct link provided from service payload with download bar
    """
    # local_filename = url.split('/')[-1]
    local_filename = filename
    local_filename = no_accent_vietnamese(local_filename)
    if os.path.exists(location + local_filename):
        print('Local File Existed ! Ignore downloading')
        return 1
    else:
        try:
            with requests.get(url, stream=True,timeout=(2,3)) as r:
                try:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length'))
                    if (total_size > (2*1024*1024*1024)):
                    #File is greater than 2Gb, use bigger chunk size
                        download_chunk_size = 2*1024*1024
                    else:
                        download_chunk_size = 1024*1024
                    downloaded_chunk = 0
                    progressbar = tqdm(total=total_size,desc="Downloading",ncols=70, unit_scale=True, unit="B")
                    with open(location + local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=download_chunk_size): 
                            if chunk: # filter out keep-alive new chunks
                                f.write(chunk)
                                f.flush()
                                progressbar.update(len(chunk))
                                # progressbar.update(float((downloaded_chunk*(download_chunk_size)/total_size)))
                                # downloaded_chunk += 1
                        progressbar.close()
                except HTTPError:
                    print("HTTP Error")
            return (location + local_filename)
        except Timeout:
            print('Please check Internet connection, the request timed out')
        
        
def is_folder(url):
    if (url.find(Folder_Indicator)) != -1:
        return True
    else:
        return False

def perform_login(login_credential):
    """
    Perform login and return the status True/False
    """    
    global service
    service = FSAPI(login_credential['username'],login_credential['password'])
    login_status = True
    try:
        service.login()
    except KeyError:
        login_status=False
    return login_status

def configuration_read(filename):
    """
    Read configuration from file / without header section
    """
    config = configparser.ConfigParser()
    # Append a header section to avoid header section in the configuration file
    # config.read(filename,encoding="utf-8")
    with open(filename) as f:
        config.read_string('[DEFAULT]\n'+f.read())
    return config['DEFAULT']


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def splash_screen():
# use Colorama to make Termcolor work on Windows too
    init()
    # now, to clear the screen
    cls()


    print(colored('_______      _______. __    __       ___      .______       _______     ____    ____ .__   __.                     ', 'red'))
    print(colored('|   ____|    /       ||  |  |  |     /   \     |   _  \     |   ____|    \   \  /   / |  \ |  |                    ', 'red'))
    print(colored('|  |__      |   (----`|  |__|  |    /  ^  \    |  |_)  |    |  |__        \   \/   /  |   \|  |                    ', 'red')) 
    print(colored('|   __|      \   \    |   __   |   /  /_\  \   |      /     |   __|        \      /   |  . `  |                    ', 'yellow'))
    print(colored('|  |     .----)   |   |  |  |  |  /  _____  \  |  |\  \----.|  |____  __    \    /    |  |\   |                    ', 'yellow'))
    print(colored('|__|     |_______/    |__|  |__| /__/     \__\ | _| `._____||_______|(__)    \__/     |__| \__|                    ', 'green'))
    print(colored('_______   ______   ____    __    ____ .__   __.  __        ______        ___       _______   _______ .______       ', 'blue'))
    print(colored('|       \ /  __  \  \   \  /  \  /   / |  \ |  | |  |      /  __  \      /   \     |       \ |   ____||   _  \     ', 'blue'))
    print(colored('|  .--.  |  |  |  |  \   \/    \/   /  |   \|  | |  |     |  |  |  |    /  ^  \    |  .--.  ||  |__   |  |_)  |    ', 'magenta'))
    print(colored('|  |  |  |  |  |  |   \            /   |  . `  | |  |     |  |  |  |   /  /_\  \   |  |  |  ||   __|  |      /     ', 'magenta'))
    print(colored("|  '--'  |  `--'  |    \    /\    /    |  |\   | |  `----.|  `--'  |  /  _____  \  |  '--'  ||  |____ |  |\  \----.", 'cyan'))
    print(colored('|_______/ \______/      \__/  \__/     |__| \__| |_______| \______/  /__/     \__\ |_______/ |_______|| _| `._____|', 'cyan'))
    print(colored('===================================================================================================================', 'white'))
    print(colored('                                                                             Version : ', 'yellow'), (1.0))
    print(colored('                                                                              Author : ', 'yellow'), ('haind'))
    print(colored('                                        Github : ', 'yellow'), ('https://github.com/haindvn/FShareDownloader'))
    print(colored('===================================================================================================================', 'white'))

def splash_screen_end():
    print(colored('===================================================================================================================', 'white'))
    print(colored('Download Finished','green'))

def no_accent_vietnamese(s):
    #s = s.decode('utf-8', errors='ignore')
    s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(u'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(u'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(u'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(u'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(u'[ìíịỉĩ]', 'i', s)
    s = re.sub(u'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(u'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(u'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(u'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(u'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(u'[Đ]', 'D', s)
    s = re.sub(u'[đ]', 'd', s)
    return s

if __name__ == '__main__':
    main()

#fileinfo = bot.get_file_info(URL)
#print("Direct Link:",bot.download("https://www.fshare.vn/file/{}".format(fileinfo['linkcode'])))
