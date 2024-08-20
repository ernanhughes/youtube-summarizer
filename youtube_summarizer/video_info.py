from urllib.request import urlopen
from rich import print
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, asdict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


@dataclass
class VideoInfoData:
    id: str
    title: str = ''
    url: str = ''
    upload_date: str = ''
    duration: str = ''
    description: str = ''
    genre: str = ''
    is_paid: bool = False
    is_unlisted: bool = False
    is_family_friendly: bool = False
    channel_id: str = ''
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    thumbnail_url: str = ''
    player_type: str = ''
    regions_allowed: str = ''


class VideoInfo:

    def __init__(self, video_id: str):
        self.video_id = video_id
        self.video_data = self._scrape_video_data()
        self.transcript = None
        self.text = None

    def get_transcript(self):
        if self.transcript == None:
            self.transcript = YouTubeTranscriptApi.get_transcript(self.video_id)
        return self.transcript

    def get_text(self):
        if self.text == None:
            formatter = TextFormatter()
            self.text = formatter.format_transcript(self.get_transcript())
        return self.text


    def _is_true(self, val: str) -> bool:
        return val.lower() not in ["false", "0"]

    def _remove_comma(self, s: str) -> str:
        return "".join(s.split(","))

    def _scrape_video_data(self) -> VideoInfoData:
        """Scrap video information into a data object"""
        url = f"https://www.youtube.com/watch?v={self.video_id}"
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "lxml")
        video = VideoInfoData(id=self.video_id, url=url)

        item_props = soup.find(id="watch7-content")
        if not item_props or len(item_props.contents) <= 1:
            raise MissingIdError(f"Video with the ID {self.video_id} does not exist")

        self._extract_basic_info(item_props, video)
        self._extract_likes_dislikes(soup, video)

        print(asdict(video))  # Print the video data as a dictionary
        return video

    def _extract_basic_info(self, item_props, video: VideoInfoData) -> None:
        """Extract basic video info from item properties."""
        for tag in item_props.find_all(itemprop=True, recursive=False):
            key = tag["itemprop"]
            if key == "name":
                video.title = tag["content"]
            elif key == "duration":
                video.duration = tag["content"]
            elif key == "datePublished":
                video.upload_date = tag["content"]
            elif key == "genre":
                video.genre = tag["content"]
            elif key == "paid":
                video.is_paid = self._is_true(tag["content"])
            elif key == "unlisted":
                video.is_unlisted = self._is_true(tag["content"])
            elif key == "isFamilyFriendly":
                video.is_family_friendly = self._is_true(tag["content"])
            elif key == "thumbnailUrl":
                video.thumbnail_url = tag["href"]
            elif key == "interactionCount":
                video.views = int(tag["content"])
            elif key == "channelId":
                video.channel_id = tag["content"]
            elif key == "description":
                video.description = tag["content"]
            elif key == "playerType":
                video.player_type = tag["content"]
            elif key == "regionsAllowed":
                video.regions_allowed = tag["content"]

    def _extract_likes_dislikes(self, soup, video: VideoInfoData) -> None:
        """Extract likes and dislikes from the script tags."""
        all_scripts = soup.find_all("script")
        for script in all_scripts:
            try:
                if script.string and "ytInitialData" in script.string:
                    video.likes = self._extract_stat("LIKE", script.string)
                    video.dislikes = self._extract_stat("DISLIKE", script.string)
            except (AttributeError, IndexError, ValueError) as e:
                print(f"Error parsing like/dislike counts: {e}")

    def _extract_stat(self, label: str, script_content: str) -> int:
        """Extract specific statistic (likes/dislikes) from the script content."""
        try:
            match = re.findall(f'label(.*)', re.findall(f'{label}(.*?){label.lower()}', script_content)[0])[0]
            result = ("".join(match.split(",")).split('"')[-1]).strip()
            return int(result)
        except (IndexError, ValueError) as e:
            print(f"Error extracting {label} count: {e}")
            return 0


class MissingIdError(ValueError):
    pass
