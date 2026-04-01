from clients.supabase_client import get_client

clients.supabase_client

def get_calculation(calculation_id: str):
    supabase = get_client()

    response = (
        supabase
        .table("calculations")
        .select("*")
        .eq("calculation_id", calculation_id.strip())
        .execute()
    )

    return response.data

def get_sales_breakdown(tpnb: int, supplier_id: int, week: int) -> list:
    supabase = get_client()

    response = (
        supabase
        .table("sales")
        .select("*")
        .eq("tpnb", tpnb)
        .eq("sales_supplier", supplier_id)   # ← was sales_parent_supplier_no
        .eq("year_week_number", week)
        .execute()
    )
    return response.data

def get_agreement(promo_ref: int, supplier_id: int, tpnb: int) -> dict:
    supabase = get_client()

    response = (
        supabase
        .table("agreements")
        .select("*")
        .eq("promotion_reference_number", promo_ref)
        .eq("funded_supplier_number", supplier_id)
        .eq("tpnb", tpnb)
        .execute()
    )
    return response.data

def get_supplier(supplier_id: int) -> dict:
    supabase = get_client()

    response = (
        supabase
        .table("suppliers")
        .select("*")
        .eq("supplier_number", supplier_id)
        .execute()
    )
    return response.data
