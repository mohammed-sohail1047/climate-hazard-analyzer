
from pymongo import MongoClient
# from pymongo.errors import PyMongoError

from app.config import MONGODB_URI, DATABASE_NAME

client = None
db = None


def connect_to_mongodb():
    """Connect to MongoDB Atlas and verify the connection."""
    global client, db

    if not MONGODB_URI:
        raise ValueError(
            "MONGODB_URI is missing. Check your backend/.env file."
        )

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
    )

    # Send a command to verify that MongoDB is reachable.
    client.admin.command("ping")

    db = client[DATABASE_NAME]
    return db


def get_database():
    """Return the database, connecting if necessary."""
    if db is None:
        return connect_to_mongodb()

    return db


def close_mongodb_connection():
    """Close the MongoDB client connection."""
    global client, db

    if client is not None:
        client.close()

    client = None
    db = None


def get_weather_collection():
    """Return the MongoDB collection for cached weather data."""
    database = get_database()
    return database["weather_cache"]
