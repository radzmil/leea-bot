"""PostgreSQL configuration shared by the bot's database operations."""

import os

import psycopg2


DATABASE_URL = os.getenv("DATABASE_URL")


def connect(database_url=None):
    """Open a connection without embedding credentials in source control."""
    url = database_url or DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(url, connect_timeout=5)