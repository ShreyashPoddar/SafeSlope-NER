import os
from databases import Database

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://resiliner_user:resiliner_pass@db:5432/resiliner",
)

database = Database(DATABASE_URL)
