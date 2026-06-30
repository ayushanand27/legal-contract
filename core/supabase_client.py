import os
from functools import lru_cache

from supabase import Client, create_client

import config


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    if not config.SUPABASE_URL or not config.SUPABASE_SERVICE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    return create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
