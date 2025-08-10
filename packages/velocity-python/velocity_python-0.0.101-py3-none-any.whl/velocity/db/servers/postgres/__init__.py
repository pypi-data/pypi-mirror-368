import os
import psycopg2
from .sql import SQL
from velocity.db.core import engine



def initialize(config=None, **kwargs):
    if not config:
        # Keep the default config inside this function.
        config = {
            "database": os.environ["DBDatabase"],
            "host": os.environ["DBHost"],
            "port": os.environ["DBPort"],
            "user": os.environ["DBUser"],
            "password": os.environ["DBPassword"],
        }
    config.update(kwargs)
    return engine.Engine(psycopg2, config, SQL)
