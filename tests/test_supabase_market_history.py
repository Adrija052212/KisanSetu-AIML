from src.data_access.market_data import (
    get_market_price_history,
)


def test_get_market_price_history():

    records = get_market_price_history(
        state="Andaman and Nicobar",
        district="North and Middle Andaman",
        market=(
            "Diglipur Vegetable Market "
            "(Subhashgram)"
        ),
        commodity="Tomato",
        variety="Other",
        grade="FAQ",
        limit=20,
    )

    assert isinstance(records, list)

    assert len(records) > 0

    first_record = records[0]

    assert first_record["State"] == (
        "Andaman and Nicobar"
    )

    assert first_record["Commodity"] == (
        "Tomato"
    )

    assert first_record["Modal_Price"] is not None

    assert first_record["Date"] is not None