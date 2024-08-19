import os
import sqlite3
from sqlite3 import connect
from typing import Dict
from dataclasses import asdict
from youtube_summarizer.config import appConfig
from youtube_summarizer.video_info import VideoInfoData


class SummarizeDb:
    def __init__(self, db_file: str = appConfig.get("DATABASE_PATH")):
        super().__init__()
        self.db_file = db_file
        self.cn = connect(self.db_file)
        self.cur = self.cn.cursor()


    def insert_video(transcript):
        
        #{'text': str, 'start': float, 'end': float}
        pass


    def insert_transcript(self, id:str, transcript:list[dict]):
#        {'text': str, 'start': float, 'end': float}
        for line in transcript:
            print(line)
            text_data = line["text"]
            start_time = float(line["start"])
            end_time = float(line["duration"])
            self.cur.execute(
                'INSERT INTO TRANSCRIPT_TEXT(video_id, text_data, start_time, duration) VALUES (:1,:2,:3,:4)', 
                (id, text_data, start_time, end_time))
        self.cn.commit()
        print(f'Inserted transcript {id}')

    def insert_video_data(self, video_data: VideoInfoData):
        """
        Inserts video data into the VIDEO_DATA table.
        
        :param video_data: VideoInfoData object containing the video information to insert.
        """
        # Convert the VideoInfoData dataclass to a dictionary
        video_dict = asdict(video_data)
        
        # Prepare the SQL statement
        sql = """
        INSERT INTO VIDEO_DATA (
            video_id, title, upload_date, duration, description, genre, 
            is_paid, is_unlisted, is_family_friendly, channel_id, 
            views, likes, dislikes, regionsAllowed, thumbnail_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare the data for insertion
        data = (
            video_dict['id'], 
            video_dict['title'], 
            video_dict['upload_date'], 
            video_dict['duration'], 
            video_dict['description'], 
            video_dict['genre'], 
            int(video_dict['is_paid']), 
            int(video_dict['is_unlisted']), 
            int(video_dict['is_family_friendly']), 
            video_dict['channel_id'], 
            video_dict['views'], 
            video_dict['likes'], 
            video_dict['dislikes'], 
            video_dict['regionsAllowed'], 
            video_dict['thumbnail_url']
        )
        
        try:
            self.cur.execute(sql, data)
            self.cn.commit()
            print("Video data inserted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.cn.rollback()


    def insert_file(self, id: str, data: str):
        self.cur.execute(
            'INSERT INTO TRANSCRIPT_FILE(video_id, data) VALUES (:1,:2)', 
            (id, data))
        self.cn.commit()
        print(f'Inserted file {id}')

    @staticmethod
    def init_db(db: str = appConfig.get("DATABASE_PATH"),
                schema: str = appConfig.get("SCHEMA_FILE")):
        print("Initializing the database.....")
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
        print("Initialized the database")

    @staticmethod
    def is_sqlite3_db(filename):
        from os.path import isfile, getsize

        if not isfile(filename):
            return False
        if getsize(filename) < 100: # SQLite database file header is 100 bytes
            return False

        with open(filename, 'rb') as fd:
            header = fd.read(100)

        return header[:16] == b'SQLite format 3\x00'


    def drop_db(self):
        if self.cn:
            self.cn.close()
        self.remove_file(self.db_file)

    @staticmethod
    def remove_file(db):
        if os.path.isfile(db):
            os.remove(db)
            print(f"Dropped the database:{os.path.abspath(db)}.")
        else:
            print(f'Database {os.path.abspath(db)} not found.')

