from urllib.request import urlopen
from rich import print
from bs4 import BeautifulSoup
import re

Info = {
    "id": str,
    "title": str,
    "url": str,
    "upload_date": str,
    "duration": str,
    "description": str,
    "genre": str,
    "is_paid": int,
    "is_unlisted": int,
    "is_family_friendly": int,
    "channel_id": str,
    "views": int, 
    "likes": int, 
    "dislikes": int,
}

class VideoInfo:

    def __init__(self, id: str):
        self.video_data = self.scrape_video_data(id)

    def is_true(self, val: str):
        return val.lower() not in ["false", "0"]

    def remove_comma(self, s: str):
        return "".join(s.split(","))

    def scrape_video_data(self, id: str):
        """
        Scrapes data from the YouTube video's page whose ID is passed in the URL,
        and returns a JSON object as a response.
        """

        url = "https://www.youtube.com/watch?v=" + id

        html = urlopen(url).read()
        soup = BeautifulSoup(html, "lxml")
        item_props = soup.find(id="watch7-content")

        if len(item_props.contents) > 1:
            video = Info
            video["id"] = id
            video["url"] = url
            # get data from tags having `itemprop` attribute
            for tag in item_props.find_all(itemprop=True, recursive=False):
                key = tag["itemprop"]
                if key == "name":
                    # get video's title
                    video["title"] = tag["content"]
                elif key == "duration":
                    # get video's duration
                    video["duration"] = tag["content"]
                elif key == "datePublished":
                    # get video's upload date
                    video["upload_date"] = tag["content"]
                elif key == "genre":
                    # get video's genre (category)
                    video["genre"] = tag["content"]
                elif key == "paid":
                    # is the video paid?
                    video["is_paid"] = self.is_true(tag["content"])
                elif key == "unlisted":
                    # is the video unlisted?
                    video["is_unlisted"] = self.is_true(tag["content"])
                elif key == "isFamilyFriendly":
                    # is the video family friendly?
                    video["is_family_friendly"] = self.is_true(tag["content"])
                elif key == "thumbnailUrl":
                    # get video thumbnail URL
                    video["thumbnail_url"] = tag["href"]
                elif key == "interactionCount":
                    # get video's views
                    video["views"] = int(tag["content"])
                elif key == "channelId":
                    # get uploader's channel ID
                    video["channel_id"] = tag["content"]
                elif key == "description":
                    video["description"] = tag["content"]
                elif key == "playerType":
                    video["playerType"] = tag["content"]
                elif key == "regionsAllowed":
                    video["regionsAllowed"] = tag["content"]

            all_scripts = soup.find_all("script")
            for i in range(len(all_scripts)):
                try:
                    if "ytInitialData" in all_scripts[i].string:
                        match = re.findall(
                            "label(.*)",
                            re.findall("LIKE(.*?)like", all_scripts[i].string)[0],
                        )[0]
                        hasil = ("".join(match.split(",")).split('"')[-1]).strip()
                        try:
                            video["likes"] = eval(hasil)
                        except:
                            video["likes"] = 0

                        match = re.findall(
                            "label(.*)",
                            re.findall("DISLIKE(.*?)dislike", all_scripts[i].string)[0],
                        )[0]
                        hasil = ("".join(match.split(",")).split('"')[-1]).strip()
                        try:
                            video["dislikes"] = eval(hasil)
                        except:
                            video["dislikes"] = 0

                except:
                    pass

            print(video)        
            return video
        raise MissingIdError(f'Video with the ID {id} does not exist')


class MissingIdError(ValueError):
    pass