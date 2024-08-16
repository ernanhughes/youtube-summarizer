import typer
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def main(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    txt_formatted = formatter.format_transcript(transcript)
    print(txt_formatted)
    # Now we can write it out to a file.
    with open(f'{video_id}.txt', 'w', encoding='utf-8') as f:
        f.write(txt_formatted)


if __name__ == "__main__":
    typer.run(main)


