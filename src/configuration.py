from os import environ

from dotenv import load_dotenv

__all__ = ['CONF']

load_dotenv()

CONF = {**environ}
