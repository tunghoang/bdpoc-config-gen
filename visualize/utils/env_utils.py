import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name):
  env = os.getenv(name)
  if env is None:
    raise ValueError(f"Environment variable {name} is not set")
  return env