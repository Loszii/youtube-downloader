import sys
import os
import subprocess
from pytube import YouTube, Playlist

def downloader():

    while True:
        mode = input("Enter \"p\" for playlist, \"v\" for video, or \"x\" to exit:\n")
        if mode == "p":
            playlist_url = input("Copy and paste playlist url:\n")
            p = Playlist(playlist_url)
            try:
                for video in p.videos:
                    stream = video.streams.filter(only_audio=True).order_by("abr").last()
                    stream.download(output_path = p.title)
                to_mp3(p.title)
                print("Success!")
            except:
                print("An error has occured, enter a valid playlist URL")
        elif mode == "v":
            video_url = input("Copy and paste video url:\n")
            try:
                yt = YouTube(video_url)
                stream = yt.streams.filter(only_audio=True).order_by("abr").last()
                stream.download(output_path = yt.title)
                to_mp3(yt.title)
                print("Success!")
            except:
                print("An error has occured, enter a valid video URL")
        elif mode == "x":
            sys.exit()
        else:
            print("Enter valid mode")
    

def to_mp3(folder):
    for i in os.listdir(folder):
        if ".mp3" not in i:
            new_name = os.path.splitext(i)[0] #removes extension
            subprocess.run(f"ffmpeg -i \"{folder}/{i}\" -vn -q:a 0 -map a \"{folder}/{new_name}.mp3\"", shell=True)
            os.remove(f"{folder}/{i}")



if __name__ == "__main__":
    downloader()