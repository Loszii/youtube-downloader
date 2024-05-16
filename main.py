import sys
import os
import subprocess
import pickle
import json

#idea: make playlist and multi-song download to own dir

def main():
    #gets path, url from user, and converts the video/s to .mp3
    path = get_path()
    while True:
        mode = input("playlist | video | multi-song-video? [p/v/m]\n")
        if mode == "p":
            playlist_url = input("url:\n")
            try:
                playlist_downloader(path, playlist_url)
            except Exception as e:
                print(e)
        elif mode == "v":
            video_url = input("url:\n")
            try:
                vid_downloader(path, video_url) 
            except Exception as e:
                print(e)
        elif mode == "m":
            video_url = input("url:\n")
            try:
                multi_downloader(path, video_url)
            except Exception as e:
                print(e)
        else:
            print("Enter valid mode")

def vid_downloader(path, url):
    subprocess.run(f"yt-dlp -f \"ba*\" \"{url}\" -o \"%(title)s.%(ext)s\" -P \"temp\" --no-playlist", shell=True)
    to_mp3(path)
    os.rmdir(f"temp")

def playlist_downloader(path, url):
    subprocess.run(f"yt-dlp -f \"ba*\" \"{url}\" -o \"%(title)s.%(ext)s\" -P \"temp\"", shell=True)
    to_mp3(path)
    os.rmdir("temp")

def to_mp3(path):
    #converts video from temp to .mp3 format with ffmpeg
    files = os.listdir("temp")
    for title in files:
        new_title = os.path.splitext(title)[0] + ".mp3" #changes name to new extension
        subprocess.run(f"ffmpeg -i \"temp/{title}\" -vn -q:a 0 -map a \"{path}{new_title}\" -loglevel 0", shell=True)
        #removing temp file
        os.remove(f"temp/{title}")


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
            if new_path[len(new_path)-1] != "/" and new_path[len(new_path)-1] != "\\": #add final slash for compatability with to_mp3() func
                if ("\\" in new_path):
                    new_path += "\\"
                else:
                    new_path += "/"
            #storing new path
            data.append(new_path)
            with open(file_name, "wb") as f:
                pickle.dump(data, f)
        else:
            try:
                if int(user_input) in range(0, len(data)):
                    break #path has been chosen
            except:
                print("error")
    return data[int(user_input)]


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

def to_multi_mp3(path, song_data):
    #takes one song and splits it into multiple times mp3s
    #song_data is a dictionary with title being key and value being the time-stamp

    files = os.listdir("temp")
    if ".info.json" in files[0]:
        title = files[1]
    else:
        title = files[0]

    new_title = os.path.splitext(title)[0] + ".mp3" #changes name to new extension
    subprocess.run(f"ffmpeg -i \"temp/{title}\" -vn -q:a 0 -map a \"temp/{new_title}\" -loglevel 0", shell=True)
    #removing old format file in temp
    os.remove(f"temp/{title}")

    #path/new_title is location of parent mp3
    for i in song_data:
        name = i + ".mp3"
        start = song_data[i][0]
        duration = song_data[i][1]
        if duration == None:
            subprocess.run(f"ffmpeg -i \"temp/{new_title}\" -ss {start} -c copy \"{path}{name}\" -loglevel 0", shell=True)
        else:
            subprocess.run(f"ffmpeg -i \"temp/{new_title}\" -ss {start} -t {duration} -c copy \"{path}{name}\" -loglevel 0", shell=True)

    #delete the files after this
    files = os.listdir("temp")
    for title in files:
        os.remove(f"temp/{title}")

def multi_downloader(path, url):
    #function for a video composed of multiple songs that have time stamps in the description
    subprocess.run(f"yt-dlp -f \"ba*\" \"{url}\" -o \"%(title)s.%(ext)s\" -P \"temp\" --no-playlist --write-info-json", shell=True)

    #get time stamps here
    song_data = get_time_stamps()

    to_multi_mp3(path, song_data)
    os.rmdir(f"temp")

def get_time_stamps():
    #finds json in temp and gets description to decode time stamps and title
    files = os.listdir("temp")
    for i in files:
        if ".info.json" in i:
            data = i
            break

    desc = json.load(open(f"temp/{data}", encoding="utf-8"))["description"]
    split_desc = desc.split("\n")

    times = []
    nums = "0123456789"
    for i in range(len(split_desc)):
        if ":" in split_desc[i]:
            #find index of :
            index = split_desc[i].find(":")

            #formatting
            if index > 0 and split_desc[i][index-1] in nums and split_desc[i][index+1] in nums and split_desc[i][index+2] in nums:
                if index == 1:
                    split_desc[i] = "0" + split_desc[i]
                elif split_desc[i][index-2] not in nums:
                    split_desc[i] = split_desc[i][:index-1] + "0" + split_desc[i][index-1:]
                times.append(split_desc[i])

    song_data = {}
    temp_data = [] #using this to computer delta time and add to prev
    #temp data of format [[name, start, duration], ...]
    prev_stamp = "00:00"
    for song in times:
        index = song.find(":")
        stamp = song[index-2:index+3]
        length = time_difference(prev_stamp, stamp)
        if len(temp_data) > 0: #compute time diff and add to last song for length
            temp_data[-1] += [length]
        prev_stamp = stamp
        name = format_name(song.replace(stamp, ""))
        temp_data += [[name, stamp]] #add current song

    temp_data[-1] += [None] #last one is none since it will go to the ends of the file

    for i in range(len(temp_data)):
        song_data[temp_data[i][0]] = (temp_data[i][1], temp_data[i][2]) #add to dict

    return song_data

def time_difference(start, end):
    #takes in start and end time of format ##:## and returns difference
    end_mins = int(end[:2])
    start_mins = int(start[:2])
    total_mins = end_mins - start_mins

    end_secs = int(end[3:])
    start_secs = int(start[3:])
    total_secs = end_secs - start_secs
    if total_secs < 0:
        total_mins -= 1
        total_secs += 60

    total_mins = str(total_mins)
    total_secs = str(total_secs)

    if len(total_mins) == 1:
        total_mins = "0" + total_mins
    if len(total_secs) == 1:
        total_secs = "0" + total_secs
    return str(total_mins) + ":" + str(total_secs)

def format_name(name):
    #takes in name of song and makes sure there are no illegal characters for saving to pc
    illegal = "*\"/\\<>:|?"
    for i in illegal:
        name = name.replace(i, "")
    return name

if __name__ == "__main__":
    main()