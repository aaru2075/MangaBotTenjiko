env_vars = {
    # Get from my.telegram.org
    "API_HASH": "057fd0be9d7c38526b143c582bceb24b",
    # Get from my.telegram.org
    "API_ID": "20445873",
    # Get from @BotFather
    "BOT_TOKEN": "7885135779:AAFJZZAiRjU6tc0Mx8j2vPnmrzreCLBNhlI",
    # Get from tembo.io
    "DATABASE_URL_PRIMARY": "postgres://avnadmin:AVNS_u7YLST7hs-iUBX5w6nh@pg-29adbac6-kagut67.j.aivencloud.com:16924/defaultdb",
    # Logs channel username without @
    "CACHE_CHANNEL": "",
    # Force subs channel username without @
    "CHANNEL": "",
    # {chap_num}: Chapter Number
    # {chap_name}: Manga Name
    # Example: Chapter {chap_num} {chap_name} @Manhwa_Arena
    "FNAME": "[MC] [{chap_num}] {chap_name} @Manga_Campus",
    # Thumb Path (Optional)
    "THUMB": "thumbnail.jpg",
    # Add authorized user IDs, separated by commas in a list
    "SUDOS": [5543390445]
}

# Determine the database URL (default to SQLite if not provided)
dbname = (
    env_vars.get("DATABASE_URL_PRIMARY") 
    or env_vars.get("DATABASE_URL") 
    or "sqlite:///test.db"
)

# Ensure compatibility with SQLAlchemy if using older Postgres URL formats
if dbname.startswith("postgres://"):
    dbname = dbname.replace("postgres://", "postgresql://", 1)
