# FShare Downloader
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)   [![forthebadge](https://forthebadge.com/images/badges/uses-git.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

**FShare VIP account required**

Since I can not find any working script for my headless Sheevaplug / Raspberry Pi with Debian distro installed to download files / folders from Fshare.vn (they provide a GUI program on Windows / Mac, not Linux), I searched and was inspired by the [FShare API](https://github.com/tudoanh/get_fshare) / **tudoanh**, then I coded this Python script for my own use and recently I enhanced it a little bit to share with others. Note that you will need a FShare VIP account for this script to work properly.

![alt text](https://github.com/haindvn/FShareDownloader/blob/master/screenshot2.JPG)

![alt text](https://github.com/haindvn/FShareDownloader/blob/master/screenshot3.JPG)

## Required packages:
* Pyhon 3.5+
* lxml (for Debian system, please install python3-lxml package, we don't need pip to compile from source)
* requests
* get_fshare
* requests
* hyper
* colorama
* termcolor 
* tqdm

In short, please run these commands on Debian system to install the neccessary packages
```
$ sudo apt-get install python3-lxml
$ sudo pip3 install get_fshare requests hyper colorama termcolor tqdm
```

## Getting Started / Usage

* Download / clone or fork this repo
* Update `credentials.ini` with your `FShare username` / `password`
* Download file or whole folder from FShare by running this command
```
python3 fdownload.py <file or folder URL> <path_to_save>
```
Or just run the script without parameters, then input them manually through guided program flow
```
python3 fdownload.py
```

**Example**

To download a file (Unattended mode)
```
$ python3 fdownload.py https://www.fshare.vn/file/XXXXXXXX /home/haind/movies
```
To download a folder  (Unattended mode)
```
$ python3 fdownload.py https://www.fshare.vn/folder/XXXXXXXX /home/haind/movies
```
Then a folder `XXXXXXXXXX` will be created in `/home/haind/movies` then all files will be put in `XXXXXXXXXX` (we won't create a folder basing on the folder name as per FShare's folder name since I found folder name with Vietnamese accent will be corrupted or give some ab-normal disk operations later, please change the folder name by yourself)

**Note**: if there are sub-folders in the folder link, **they will be skipped, ONLY FILES IN THE FOLDER WILL BE DOWNLOADED**, the script will not recursively download any sub-folder to avoid uncontrollable linked folders/files. The script will also write down a short text file with some useful information for later reference later. 

All credits goes to [FShare API](https://github.com/tudoanh/get_fshare)

Enjoy Downloading !!!
