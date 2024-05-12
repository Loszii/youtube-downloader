import sys
import os
import subprocess
from pytube import YouTube, Playlist

def downloader():

    path = input("Enter full path (nothing for cd):\n").replace('"', "")

    while True:
        mode = input("playlist or video? [p/v]\n")
        if mode == "p":
            playlist_url = input("url:\n")
            p = Playlist(playlist_url)
            new_path = path + "/" + p.title
            try:
                for video in p.videos:
                    stream = video.streams.filter(only_audio=True).order_by("abr").last()
                    stream.download(output_path = new_path)
                to_mp3(new_path, None)
                exit()
            except Exception as e:
                print(e)
        elif mode == "v":
            video_url = input("url:\n")
            try:
                yt = YouTube(video_url)
                stream = yt.streams.filter(only_audio=True).order_by("abr").last()
                stream.download(output_path = path)
                to_mp3(path, yt.title)
                exit()
            except Exception as e:
                print(e)
        else:
            print("Enter valid mode")
    

def to_mp3(folder, title):

    if title == None: #playlist
        for i in os.listdir(folder):
            new_name = os.path.splitext(i)[0] #removes extension
            subprocess.run(f"ffmpeg -i \"{folder}/{i}\" -vn -q:a 0 -map a \"{folder}/{new_name}.mp3\" -loglevel 0", shell=True)
            os.remove(f"{folder}/{i}")
    elif folder == "":
        subprocess.run(f"ffmpeg -i \"{title}.webm\" -vn -q:a 0 -map a \"{title}.mp3\" -loglevel 0", shell=True)
        os.remove(f"{title}.webm")
    else:
        subprocess.run(f"ffmpeg -i \"{folder}/{title}.webm\" -vn -q:a 0 -map a \"{folder}/{title}.mp3\" -loglevel 0", shell=True)
        os.remove(f"{folder}/{title}.webm")



if __name__ == "__main__":
    downloader()