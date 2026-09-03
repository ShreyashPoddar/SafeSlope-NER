import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://resiliner_user:resiliner_pass@db:5432/resiliner",
)

try:
    from databases import Database
    database = Database(DATABASE_URL)
    HAS_DATABASES = True
except ImportError:
    class DummyDatabase:
        def __init__(self, url):
            self.url = url
            self.is_connected = False
        async def connect(self):
            pass
        async def disconnect(self):
            pass
        async def execute(self, query, values=None):
            return None
        async def fetch_one(self, query, values=None):
            return None
        async def fetch_all(self, query, values=None):
            return []
    database = DummyDatabase(DATABASE_URL)
    HAS_DATABASES = False
