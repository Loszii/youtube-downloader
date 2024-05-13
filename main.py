import sys
import os
import subprocess
from pytube import YouTube, Playlist

def main():
    #gets path, url from user, and converts the video/s to .mp3
    path = get_path()
    while True:
        mode = input("playlist or video? [p/v]\n")
        if mode == "p":
            playlist_url = input("url:\n")
            p = Playlist(playlist_url)
            try:
                for video in p.videos:
                    downloader(path, video)
            except Exception as e:
                print(e)
        elif mode == "v":
            video_url = input("url:\n")
            try:
                yt = YouTube(video_url)
                downloader(path, yt)
            except Exception as e:
                print(e)
        else:
            print("Enter valid mode")
    

def downloader(path, obj):
    #downloads video using pytube
    print("downloading video...")
    stream = obj.streams.filter(only_audio=True).order_by("abr").last()
    stream.download(output_path = path)
    print("converting to mp3...")
    to_mp3(path, stream.default_filename)

def to_mp3(path, title):
    #converts video to .mp3 format with ffmpeg
    new_title = os.path.splitext(title)[0] + ".mp3" #changes name to new extension
    subprocess.run(f"ffmpeg -i \"{path}{title}\" -vn -q:a 0 -map a \"{path}{new_title}\" -loglevel 0", shell=True)
    os.remove(f"{path}{title}")

def get_path():
    #to-do
    return ""

if __name__ == "__main__":
    main()