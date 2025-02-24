import yt_dlp
import os

folder_name = "AtakanYouTubeDownloader"

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

url = input("Enter video URL: ")

ydl_opts = {
    'format': 'best',  #Downloads in best quality mp4.
    'outtmpl': f'{folder_name}/%(title)s.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
    print("Download completed!")