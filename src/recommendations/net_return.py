from typing import Dict


def calculate_net_return(
    price: float,
    quantity: float,
    transport_cost: float = 0.0,
    storage_cost: float = 0.0,
    other_costs: float = 0.0,
    mode: str = "sell",
    price_unit: str = "Rs./Quintal",
) -> Dict:
    if price < 0:
        raise ValueError("price cannot be negative.")

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero.")

    if transport_cost < 0:
        raise ValueError("transport_cost cannot be negative.")

    if storage_cost < 0:
        raise ValueError("storage_cost cannot be negative.")

    if other_costs < 0:
        raise ValueError("other_costs cannot be negative.")

    if mode not in {"sell", "buy"}:
        raise ValueError("mode must be either 'sell' or 'buy'.")

    gross_value = price * quantity

    transport_total = transport_cost * quantity
    storage_total = storage_cost * quantity
    other_total = other_costs * quantity

    total_costs = (
        transport_total
        + storage_total
        + other_total
    )

    if mode == "sell":
        net_return = gross_value - total_costs
    else:
        net_return = gross_value + total_costs

    return {
        "mode": mode,
        "price": round(price, 2),
        "quantity": quantity,
        "gross_value": round(gross_value, 2),
        "transport_cost": round(transport_cost, 2),
        "storage_cost": round(storage_cost, 2),
        "other_costs": round(other_costs, 2),
        "total_costs": round(total_costs, 2),
        "net_return": round(net_return, 2),
        "price_unit": price_unit,
    }