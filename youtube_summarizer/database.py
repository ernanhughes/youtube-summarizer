import os
import sqlite3
import json
from sqlite3 import connect
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

        # {'text': str, 'start': float, 'end': float}
        pass

    def insert_transcript(self, id: str, transcript: list[dict]):
        sql = """
            INSERT INTO TRANSCRIPT_TEXT(
                video_id, text_data, start_time, duration
            ) VALUES (?,?,?,?)
            """
        try:
            for line in transcript:
                print(line)
                data = (id, line["text"], float(line["start"]), float(line["duration"]))
                self.cur.execute(sql, data)
            self.cn.commit()
            print(f"Inserted transcript {id}")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.cn.rollback()

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
            video_dict["id"],
            video_dict["title"],
            video_dict["upload_date"],
            video_dict["duration"],
            video_dict["description"],
            video_dict["genre"],
            int(video_dict["is_paid"]),
            int(video_dict["is_unlisted"]),
            int(video_dict["is_family_friendly"]),
            video_dict["channel_id"],
            video_dict["views"],
            video_dict["likes"],
            video_dict["dislikes"],
            video_dict["regions_allowed"],
            video_dict["thumbnail_url"],
        )

        try:
            self.cur.execute(sql, data)
            self.cn.commit()
            print("Video data inserted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.cn.rollback()

    def insert_text(self, id: str, data: str, language: str = "en"):
        self.cur.execute(
            "INSERT INTO TRANSCRIPT_TEXT(video_id, language, data) VALUES (:1,:2)",
            (id, language, data),
        )
        self.cn.commit()
        print(f"Inserted file {id}")

    def insert_chat_response(self, response: dict):
        sql = """
            INSERT INTO CHAT_RESPONSE (
                model, message_role, message_content, done_reason,
                done, total_duration, load_duration, prompt_eval_count,
                prompt_eval_duration, eval_count, eval_duration
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data = (
            response["model"],
            response["message"]["role"],
            response["message"]["content"],
            response["done_reason"],
            response["done"],
            response["total_duration"],
            response["load_duration"],
            response["prompt_eval_count"],
            response["prompt_eval_duration"],
            response["eval_count"],
            response["eval_duration"]
        )
        try:
            self.cur.execute(sql, data)
            self.cn.commit()
            print("Video data inserted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.cn.rollback()


    @staticmethod
    def init_db(
        db: str = appConfig.get("DATABASE_PATH"),
        schema: str = appConfig.get("SCHEMA_FILE"),
    ):
        print("Initializing the database.....")
        base_dir = os.path.abspath(os.path.dirname(__file__))
        schema_path = os.path.join(base_dir, schema)
        print(f"Db path: {db}")
        print(f"Schema path: {schema_path}")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        with open(schema_path, "r") as f:
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
        if getsize(filename) < 100:  # SQLite database file header is 100 bytes
            return False

        with open(filename, "rb") as fd:
            header = fd.read(100)

        return header[:16] == b"SQLite format 3\x00"

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
            print(f"Database {os.path.abspath(db)} not found.")
