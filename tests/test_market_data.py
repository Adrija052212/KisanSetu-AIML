from unittest.mock import patch

from src.data_access.market_data import (
    normalize_market_record,
    get_market_prices,
    get_market_price_history,
)


def test_normalize_market_record():
    record = {
        "State": "West Bengal",
        "District": "Nadia",
        "Market": "Krishnanagar",
        "Commodity": "Tomato",
        "Variety": "Local",
        "Grade": "A",
        "Min Price": "1800",
        "Max Price": "2200",
        "Modal Price": "2000",
        "Price Unit": "Rs./Quintal",
        "Arrival Quantity": "150",
        "Arrival Unit": "Quintal",
        "Arrival Date": "04/09/2026",
    }

    normalized = normalize_market_record(record)

    assert normalized["State"] == "West Bengal"
    assert normalized["District"] == "Nadia"
    assert normalized["Market"] == "Krishnanagar"
    assert normalized["Commodity"] == "Tomato"
    assert normalized["Variety"] == "Local"
    assert normalized["Grade"] == "A"

    assert normalized["Min_Price"] == 1800.0
    assert normalized["Max_Price"] == 2200.0
    assert normalized["Modal_Price"] == 2000.0

    assert normalized["Arrival_Quantity"] == 150.0
    assert normalized["Arrival_Unit"] == "Quintal"

    assert normalized["Price_Unit"] == "Rs./Quintal"
    assert normalized["Date"] == "04/09/2026"


def test_get_market_prices():
    mock_response = {
        "records": [
            {
                "State": "West Bengal",
                "District": "Nadia",
                "Market": "Krishnanagar",
                "Commodity": "Tomato",
                "Variety": "Local",
                "Grade": "A",
                "Min Price": "1800",
                "Max Price": "2200",
                "Modal Price": "2000",
                "Price Unit": "Rs./Quintal",
            }
        ]
    }

    with patch(
        "src.data_access.market_data.requests.get"
    ) as mock_get:

        mock_get.return_value.json.return_value = (
            mock_response
        )

        mock_get.return_value.raise_for_status.return_value = None

        records = get_market_prices(
            commodity="Tomato",
            state="West Bengal",
            limit=5,
        )

    assert isinstance(records, list)
    assert len(records) == 1

    assert records[0]["Commodity"] == "Tomato"
    assert records[0]["State"] == "West Bengal"
    assert records[0]["Modal_Price"] == 2000.0
    assert records[0]["Min_Price"] == 1800.0
    assert records[0]["Max_Price"] == 2200.0

    mock_get.assert_called_once()

def test_get_market_price_history():
    mock_response = {
        "records": [
            {
                "State": "West Bengal",
                "District": "Nadia",
                "Market": "Krishnanagar",
                "Commodity": "Tomato",
                "Variety": "Local",
                "Grade": "A",
                "Min Price": "1800",
                "Max Price": "2200",
                "Modal Price": "2000",
                "Price Unit": "Rs./Quintal",
                "Arrival Quantity": "150",
                "Arrival Unit": "Quintal",
                "Arrival Date": "04/09/2026",
            }
        ]
    }

    with patch(
        "src.data_access.market_data.requests.get"
    ) as mock_get:

        mock_get.return_value.json.return_value = (
            mock_response
        )

        mock_get.return_value.raise_for_status.return_value = None

        records = get_market_price_history(
            state="West Bengal",
            district="Nadia",
            market="Krishnanagar",
            commodity="Tomato",
            variety="Local",
            grade="A",
            limit=1000,
        )

    assert len(records) == 1

    record = records[0]

    assert record["State"] == "West Bengal"
    assert record["District"] == "Nadia"
    assert record["Market"] == "Krishnanagar"
    assert record["Commodity"] == "Tomato"
    assert record["Variety"] == "Local"
    assert record["Grade"] == "A"

    assert record["Modal_Price"] == 2000.0
    assert record["Arrival_Quantity"] == 150.0    