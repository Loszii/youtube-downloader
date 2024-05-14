import sys
import os
import subprocess
import pickle
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
    #prompts user to select or add path, returns string of path to download
    file_name = "paths.pk" #pickle file
    data = get_data(file_name)
    
    while True:
        print_paths(data)
        user_input = input("select a path, or [p] to add:\n")
        if user_input == "p" :
            #improve compatibility of below code

            new_path = input("enter path below:\n").replace("\"", "") #remove quotes from copying path via file explorer
            if new_path[len(new_path)-1] != "/" and new_path[len(new_path)-1] != "\\": #add final slash for compatability with to_mp3() func
                new_path += "\\" #make this back or foward slash depending on format given via path
            data.append(new_path)
            with open(file_name, "wb") as f:
                pickle.dump(data, f)
        else:
            try:
                if int(user_input) in range(0, len(data)):
                    break
            except:
                print("error")
    return data[int(user_input)]

def get_data(file_name):
    try:
        with open(file_name, "rb") as f:
            data = pickle.load(f)
    except:
        data = [""]
    return data

def print_paths(data):
    #prints list of all pickled paths
    for i in range(len(data)):
        if i == 0:
            print("0. -working dir-")
        else:
            print(str(i) + ". " + data[i])

if __name__ == "__main__":
    main()