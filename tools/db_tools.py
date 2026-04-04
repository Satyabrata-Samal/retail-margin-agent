
from clients.supabase_client import get_client

class DatabaseHandler:
    """
    Database access layer for analyst agents.
    
    Uses singleton pattern: one client instance for all tools.
    All agent queries go through this class.
    """
    
    def __init__(self):
        """Initialize with singleton client (reused across all instances)."""
        self._client = get_client()  # One client for whole app

    def execute(self, **params: Any) -> dict[str, str]:
        """
        Execute a db tool command.

        Args:
            **params: Command parameters from Claude's tool use

        Returns:
            Dict with either 'success' or 'error' key

        Supported commands:
            - get_calculation: Retrieve a specific calculation record.
            - get_sales_breakdown:  Retrieve sales data for product-supplier-week.
            - get_agreement: Retrieve promotional agreement constraints.
            - get_supplier: Retrieve supplier metadata.
        """
        command = params.get("command")

        try:
            if command == "_get_calculation":
                return self._get_calculation(params.get("calculation_id"))
            elif command == "_get_sales_breakdown":
                return self._get_sales_breakdown(params)
            elif command == "_get_agreement":
                return self._get_agreement(params)
            elif command == "_get_supplier":
                return self._get_supplier(params)
            else:
                return {
                    "error": f"Unknown command: '{command}'. "
                    "Valid commands are: get_calculation, get_sales_breakdown, get_agreement, get_supplier"
                }
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error executing {command}: {e}"}
    
    def _get_calculation(self, calculation_id: str) -> list:
        """
        Retrieve a specific calculation record.
        
        AGENT: Call this to view calculation id level details
        """
        response = (
            self._client
            .table("calculations")
            .select("*")
            .eq("calculation_id", calculation_id.strip())
            .execute()
        )
        return response.data
    
    def _get_sales_breakdown(self, tpnb: int, supplier_id: int, week: int) -> list:
        """
        Retrieve sales data for product-supplier-week.
        
        AGENT: Call this to understand sales.
        """
        response = (
            self._client
            .table("sales")
            .select("*")
            .eq("tpnb", tpnb)
            .eq("sales_supplier", supplier_id)
            .eq("year_week_number", week)
            .execute()
        )
        return response.data
    
    def _get_agreement(self, promo_ref: int, supplier_id: int, tpnb: int) -> dict:
        """
        Retrieve promotional agreement constraints.
        
        AGENT: Call this to find agreement details
        """
        response = (
            self._client
            .table("agreements")
            .select("*")
            .eq("promotion_reference_number", promo_ref)
            .eq("funded_supplier_number", supplier_id)
            .eq("tpnb", tpnb)
            .execute()
        )
        return response.data
    
    def _get_supplier(self, supplier_id: int) -> dict:
        """
        Retrieve supplier metadata.
        
        AGENT: Call this to assess supplier details
        """
        response = (
            self._client
            .table("suppliers")
            .select("*")
            .eq("supplier_number", supplier_id)
            .execute()
        )
        return response.data
 