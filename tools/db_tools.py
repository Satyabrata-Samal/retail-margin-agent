
from clients.supabase_client import get_client

from typing import Any
from clients.supabase_client import get_client


def get_calculation(calculation_id: str) -> dict[str, Any]:
    client = get_client()
    response = (
        client
        .table("calculations")
        .select("*")
        .eq("calculation_id", calculation_id.strip())
        .execute()
    )
    return response.data


def get_sales_breakdown(tpnb: int, supplier_id: int, week: int) -> list:
    client = get_client()
    response = (
        client
        .table("sales")
        .select("*")
        .eq("tpnb", tpnb)
        .eq("sales_supplier", supplier_id)
        .eq("year_week_number", week)
        .execute()
    )
    return response.data


def get_agreement(promo_ref: int, supplier_id: int, tpnb: int) -> list:
    client = get_client()
    response = (
        client
        .table("agreements")
        .select("*")
        .eq("promotion_reference_number", promo_ref)
        .eq("funded_supplier_number", supplier_id)
        .eq("tpnb", tpnb)
        .execute()
    )
    return response.data


def get_supplier(supplier_id: int) -> list:
    client = get_client()
    response = (
        client
        .table("suppliers")
        .select("*")
        .eq("supplier_number", supplier_id)
        .execute()
    )
    return response.data


def execute_analyst_query(sql: str) -> list:
    """
    Execute a read-only SQL query.
    Analyst agent writes the SQL, this function runs it safely.
    """
    sql_upper = sql.strip().upper()
    blocked = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]

    if any(keyword in sql_upper for keyword in blocked):
        raise ValueError("Only SELECT queries are allowed.")

    client = get_client()
    response = client.rpc("execute_query", {"query": sql}).execute()
    return response.data