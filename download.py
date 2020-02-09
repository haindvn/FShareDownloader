from get_fshare import FSAPI

URL = 'https://www.fshare.vn/file/Y81358DVZ5D8'

with open("credentials.txt") as f:
    email = f.readline().rstrip()
    password = f.readline().strip()

bot = FSAPI(email,password)
bot.login()
fileinfo = bot.get_file_info(URL)

print("Direct Link:",bot.download("https://www.fshare.vn/file/{}".format(fileinfo['linkcode'])))
