import os
import click
from rich import print
from rich.pretty import Pretty
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from youtube_summarizer.config import appConfig
from youtube_summarizer.database import SummarizeDb

from youtube_summarizer.video_info import VideoInfo, VideoInfoData


@click.command()
@click.option("--db", default=appConfig.get("DATABASE_PATH"), 
              help="File path of the sqlite database to use.")
@click.option("--schema", default='schema.sql', help="The schema file used to create the database.")
def init_db(db, schema):
    """
        Will generate the sqlite database using the schema file.
    """
    SummarizeDb.init_db(db, schema)

@click.command()
@click.option("--db", default=appConfig.get("DATABASE_PATH"), help="File path of the sqlite database to drop.")
def drop_db(db = 'summarizer.db'):
    """ Drop the database """
    click.echo("Dropping the database ...")
    if os.path.isfile(db):
        os.remove(db)
        click.echo(f"Dropped the database:{os.path.abspath(db)}.")
    else:
        click.echo(f'Database {os.path.abspath(db)} not found.')


@click.command()
def config():
    """ Dump the configuration. """
    print(Pretty(appConfig, expand_all=True))

@click.command()
@click.option("--id", default='KyD8VIK032o', help="The id of the video to get text from.")
def video_text(id: str):
    """ Get video text. """
    db = SummarizeDb()
    info = VideoInfo(id)
    info_data = info.scrape_video_data()
    db.insert_video_data(info_data)
    transcript = YouTubeTranscriptApi.get_transcript(id)
    db.insert_transcript(id, transcript)
    formatter = TextFormatter()
    txt_formatted = formatter.format_transcript(transcript)
    db.insert_file(id, txt_formatted)
    info = VideoInfo(id)
    print(info)


@click.group()
def cli():
    pass

cli.add_command(init_db)
cli.add_command(drop_db)
cli.add_command(config)
cli.add_command(video_text)
