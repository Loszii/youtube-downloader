import sys
import os
import subprocess
import pickle
import json

def main():
    #gets path, url from user, and converts the video/s to .mp3
    path = get_path()
    if path != "" and not os.path.isdir(path): #make path if not already made
        print("path not found, creating now...")
        os.mkdir(path)
    while True:
        mode = input("playlist | video | chapters | exit [p/v/c/x]\n")
        if mode == "p":
            playlist_url = input("url:\n")
            try:
                print("starting download..")
                playlist_downloader(path, playlist_url)
            except Exception as e:
                print(e)
        elif mode == "v":
            video_url = input("url:\n")
            try:
                print("starting download..")
                vid_downloader(path, video_url) 
            except Exception as e:
                print(e)
        elif mode == "c":
            video_url = input("url:\n")
            try:
                print("starting download..")
                multi_downloader(path, video_url)
            except Exception as e:
                print(e)
        elif mode == "x":
            sys.exit()
        else:
            print("Enter valid mode")

def vid_downloader(path, url):
    #downloads a single video
    subprocess.run(f"yt-dlp -q --no-warnings --no-playlist -f \"ba*\" -o \"%(title)s.%(ext)s\" -P \"temp\" \"{url}\"")
    to_mp3(path)

def playlist_downloader(path, url):
    #downloads all videos in a playlist

    subprocess.run(f"yt-dlp -q --no-warnings -I 0 --write-info-json -P \"temp\" \"{url}\"") #-I 0 downloads no videos, leaving just the json file for playlist
    playlist_info = os.listdir("temp")[0]
    playlist_name = format_name(json.load(open(f"temp/{playlist_info}", encoding="utf-8", errors="ignore"))["title"]) #gets playlist name from json and formats to become dir
    os.remove(f"temp/{playlist_info}") #removing json

    new_path = path_join(path, playlist_name)
    os.mkdir(new_path)

    #download all playlist videos
    subprocess.run(f"yt-dlp -q --no-warnings --yes-playlist -f \"ba*\" -o \"%(title)s.%(ext)s\" -P \"temp\" \"{url}\"")
    to_mp3(new_path)

def multi_downloader(path, url):
    #function for a video composed of multiple songs that have time stamps in the description

    #download all chapters and original video
    subprocess.run(f"yt-dlp -q --no-warnings --no-playlist --write-info-json --split-chapters -f \"ba*\" -o \"%(title)s.%(ext)s\" -o \"chapter:%(section_title)s.%(ext)s\" -P \"temp\" \"{url}\"")
    
    files = os.listdir("temp")
    for i in files:
        if ".info.json" in i:
            json_file = i
            data = json.load(open(f"temp/{i}", encoding="utf-8", errors="ignore"))

    non_split_file = format_name(data["title"]) #get original video title and format
    non_split_ext = data["ext"]
    
    to_remove = os.path.splitext(json_file)[0][:-5] + "." + non_split_ext #using json file to get post-window filename format to delete

    os.remove(f"temp/{to_remove}")
    os.remove(f"temp/{json_file}")

    new_path = path_join(path, non_split_file)
    os.mkdir(new_path) #make folder for songs

    to_mp3(new_path)

def to_mp3(path):
    #converts video from temp to .mp3 format at path with ffmpeg
    files = os.listdir("temp")
    for title in files:
        new_title = os.path.splitext(title)[0] + ".mp3" #changes name to new extension
        print(f"downloading: {new_title}")
        subprocess.run(f"ffmpeg -loglevel 0 -i \"temp/{title}\" -vn -q:a 0 -map a \"{path}{new_title}\"") #to mp3
        #removing temp file
        os.remove(f"temp/{title}")
    os.rmdir(f"temp")

def get_path():
    #prompts user to select or add path, returns string of path to download
    file_name = "paths.pk" #pickle file
    data = get_data(file_name)
    
    while True:
        print_paths(data)
        user_input = input("select a path, or [p] to add:\n")
        if user_input == "p" :
            #putting path into correct format
            new_path = input("enter path below:\n").replace("\"", "") #removes quotes from copying path via file explorer
            if len(new_path) > 0 and new_path[len(new_path)-1] != "/" and new_path[len(new_path)-1] != "\\":
                new_path = path_join(new_path, "") #add final slash for compatability with to_mp3() func
            
            if new_path in data:
                print("path already listed...")
            else:
                if not os.path.isdir(new_path): #make path if not already made
                    print("path not found, creating now...")
                    os.mkdir(new_path)
                
                #storing new path
                data.append(new_path)
                with open(file_name, "wb") as f:
                    pickle.dump(data, f)
                return new_path
        else:
            try:
                if int(user_input) in range(len(data)):
                    return data[int(user_input)]
                else:
                    print(f"enter number in [{0}-{len(data)-1}]")
            except:
                print("enter a number")

def get_data(file_name):
    #gets pickled data
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

def path_join(path, ext):
    #custom path joiner, maintains path formatting throughout
    if "\\" in path:
        new_path = path + ext + "\\"
    else: 
        new_path = path + ext + "/"
    return new_path

def format_name(name):
    #takes in name of song and makes sure there are no illegal characters for saving to pc
    illegal = "*\"/\\<>:|?"
    for i in illegal:
        name = name.replace(i, "")
    return name

if __name__ == "__main__":
    main()