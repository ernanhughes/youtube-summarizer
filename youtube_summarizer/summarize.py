import os
import typer
import click
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from ollama import chat
from youtube_summarizer.database import initialize_database
from youtube_summarizer.config import appConfig
from youtube_summarizer.utils import isSQLite3




def get_video_text(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    txt_formatted = formatter.format_transcript(transcript)
    print(txt_formatted)


def main(video_id: str):
    db_path = appConfig.get("DATABASE_URL")
    if not isSQLite3(db_path):
        schema_file = 'schema.sql'
        initialize_database(db_path, schema_file)
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    with open(f'{video_id}.json', 'w', encoding='utf-8') as f:
        f.write(str(transcript))
    formatter = TextFormatter()
    txt_formatted = formatter.format_transcript(transcript)
    print(txt_formatted)
    # Now we can write it out to a file.
    with open(f'{video_id}.txt', 'w', encoding='utf-8') as f:
        f.write(txt_formatted)

def get_filename_without_file_extension(path):
    return os.path.splitext(os.path.basename(path))[0]


@click.group()
def cli():
    pass

@click.command()
def initdb():
    click.echo('Initialized the database')

@click.command()
def dropdb():
    click.echo('Dropped the database')

cli.add_command(initdb)
cli.add_command(dropdb)


if __name__ == "__main__":
    typer.run(main)


