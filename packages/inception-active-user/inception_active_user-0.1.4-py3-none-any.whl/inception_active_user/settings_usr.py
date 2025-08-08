import os
import time
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    url: str = ""

    env_file: str = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_file)
    model_config = SettingsConfigDict(env_file=env_file)


def init_active_user_connection(url: str):

    env_file = os.path.join(os.path.dirname(__file__), ".env")
    with open(env_file, "w") as f:
        f.write(f'url="{url}"\n')

    time.sleep(3)
    os.chmod(env_file, 0o777)
    # load the settings
    # active_user_settings = get_active_user_setting().model_dump()
    # print("Active User settings: ", active_user_settings)


def get_active_user_setting():
    return Settings()
