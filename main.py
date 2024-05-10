import sys
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
                    stream.download(output_path = f"C:/Users/jiozz/Desktop/youtube-downloader/{p.title}")
                print("Success!")
            except:
                print("An error has occured, enter a valid playlist URL")
        elif mode == "v":
            video_url = input("Copy and paste video url:\n")
            try:
                yt = YouTube(video_url)
                stream = yt.streams.filter(only_audio=True).order_by("abr").last()
                stream.download(output_path = yt.title)
                print("Success!")
            except:
                print("An error has occured, enter a valid video URL")
        elif mode == "x":
            sys.exit()
        else:
            print("Enter valid mode")
    
if __name__ == "__main__":
    downloader()