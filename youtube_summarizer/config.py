import json
import os
import logging
from pathlib import Path
from typing import Union, get_type_hints
from dotenv import load_dotenv

from youtube_summarizer.utils import get_default_data_dir

load_dotenv()


class EnvConfigError(Exception):
    pass


def _parse_bool(val: Union[str, bool]) -> bool:
    return val if isinstance(val, bool) else val.lower() in ["true", "yes", "1"]


class EnvConfig:
    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
    """

    ENV: str = "development"
    OLLAMA_HOST: str = "localhost:11434"
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///youtube_summarizer.db')
    OLLAMA_URL: str = os.environ.get('OLLAMA_URL', 'http://127.0.0.1:5000')
    OLLAMA_MODEL: str = os.environ.get('OLLAMA_MODEL', 'llama3.1')
    RAG_VERIFY_SSL: bool = False
    DATA_DIR: Path = get_default_data_dir('rag')
    LOG_FILE: str = os.environ.get('LOG_FILENAME', 'rag.log')
    def __init__(self, env='Development'):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise EnvConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise EnvConfigError("The {} field is required".format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(EnvConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                elif var_type == list[str]:
                    value = env.get(field)
                    if value is None:
                        value = default_value
                    else:
                        value = json.loads(value)
                else:
                    value = var_type(env.get(field, default_value))
                self.__setattr__(field, value)
            except ValueError:
                raise EnvConfigError(
                    'Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                        env[field], var_type, field  # type: ignore
                    )
                )
        if self.OLLAMA_URL == "":
            self.OLLAMA_URL = f"http://{self.OLLAMA_HOST}"

    def __repr__(self):
        return str(self.__dict__)


# Expose EnvConfig object for app to import
envConfig = EnvConfig(os.environ)


class AppConfig(EnvConfig):
    def __init__(self, path: Path | None = None):
        super().__init__(os.environ)
        if path is None:
            path = envConfig.DATA_DIR / "config.json"
        self._path = path
        self._data = {
            "theme": "dark",
        }
        try:
            with open(self._path, "r") as f:
                saved = json.load(f)
                self._data = self._data | saved
        except FileNotFoundError:
            Path.mkdir(self._path.parent, parents=True, exist_ok=True)
            self.save()

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def get(self, key):
        return self._data.get(key)

    def save(self):
        with open(self._path, "w") as f:
            json.dump(self._data, f)

    def __str__(self):
        """Return a string representation of the configuration."""
        return '\n'.join(f'{attr}: {value}' for attr, value in self.__dict__.items())

    def __repr__(self):
        """Return a string representation for debugging."""
        return self.__str__()


# Expose AppConfig object for app to import
appConfig = AppConfig()


def configure_logging(log_file='app.log', level=logging.DEBUG):
    """Configures logging for the Flask application.

    Args:
        log_file (str, optional): Path to the log file. Defaults to 'app.log'.
        level (int, optional): Logging level. Defaults to logging.DEBUG.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)


    # add to file
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    logger.addHandler(fh)

    return logger