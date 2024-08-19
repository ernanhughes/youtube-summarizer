import os
import click
import sqlite3
from rich import print

from youtube_summarizer.config import appConfig

@click.command()
@click.option("--db", default='summarizer.db', help="File path of the sqlite database to use.")
@click.option("--schema", default='schema.sql', help="The schema file used to create the database.")
def init_db(db= 'summarizer.db', 
            schema='schema.sql'):
    """
        Will generate the sqlite database using the schema file.
    """
    click.echo("Initializing the database.....")
    base_dir = os.path.abspath(os.path.dirname(__file__))
    schema_path = os.path.join(base_dir, schema)
    print(f'Db path: {db}')
    print(f'Schema path: {schema_path}')
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        print(schema_sql)
        cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    click.echo("Initialized the database")

@click.command()
@click.option("--db", default='summarizer.db', help="File path of the sqlite database to drop.")
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
    click.echo(appConfig)



@click.group()
def cli():
    pass

cli.add_command(init_db)
cli.add_command(drop_db)
