from src.data_access.supabase_client import get_supabase_client


def test_supabase_connection():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("profiles")
        .select("id")
        .limit(1)
        .execute()
    )

    assert response.data is not None