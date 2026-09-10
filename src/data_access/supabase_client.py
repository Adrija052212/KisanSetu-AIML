import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def get_supabase_client() -> Client:
    """
    Create and return a server-side Supabase client.

    This client is used only by the KisanSetu AI/backend layer.
    """

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL is not set.")

    if not supabase_service_role_key:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE_KEY is not set."
        )

    return create_client(
        supabase_url,
        supabase_service_role_key,
    )