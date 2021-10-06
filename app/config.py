from starlette.config import Config

config = Config(".env")

RAW_CT_PATH = config("RAW_CT_PATH", default="Path not set")
DEID_CT_PATH = config("DEID_CT_PATH", default="Path not set")
VIDA_PROCESSED_CT_PATH = config("VIDA_PROCESSED_CT_PATH", default="Path not set")
