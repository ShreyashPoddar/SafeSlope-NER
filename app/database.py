import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://resiliner_user:resiliner_pass@localhost:5432/resiliner",
)

try:
    from databases import Database
    database = Database(DATABASE_URL)
except ImportError:
    class MockDatabase:
        is_connected = False

        async def connect(self):
            self.is_connected = False
            print("Notice: Running in local memory/cache mode ('databases' not installed)")

        async def disconnect(self):
            self.is_connected = False

        async def execute(self, query, values=None):
            return 1

        async def fetch_all(self, query, values=None):
            return []

        async def fetch_one(self, query, values=None):
            return None

    database = MockDatabase()

