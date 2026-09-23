from databases import Database

from config.config import Config

config: Config = Config()
database: Database = Database(config.DATABASE_URL)