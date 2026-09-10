from typing import Dict

from src.schemas import MarketPrice


def dataframe_row_to_market_price(row: Dict) -> MarketPrice:
    return MarketPrice(
        Date=row["Date"],
        State=row["State"],
        District=row["District"],
        Market=row["Market"],
        Commodity_Group=row.get("Commodity_Group"),
        Commodity=row["Commodity"],
        Variety=row.get("Variety"),
        Grade=row.get("Grade", "Unknown"),
        Min_Price=row["Min_Price"],
        Max_Price=row["Max_Price"],
        Modal_Price=row["Modal_Price"],
        Price_Unit=row.get("Price_Unit", "Rs./Quintal"),
        Arrival_Quantity=row.get("Arrival_Quantity"),
        Arrival_Unit=row.get("Arrival_Unit"),
    )