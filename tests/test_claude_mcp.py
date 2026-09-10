import pytest

from src.llm.claude_agent import ClaudeAgent


@pytest.mark.anyio
async def test_claude_can_use_mcp_tools():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        Which market is best for selling 10 quintals?

        Market A:
        current price = 2500
        transport cost = 100

        Market B:
        current price = 2650
        transport cost = 80

        Market C:
        current price = 2700
        transport cost = 250
        """
    )

    assert response
    assert isinstance(response, str)


@pytest.mark.anyio
async def test_claude_chooses_market_tool():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I have 10 quintals of tomatoes.
        I want to sell them.
        Which is better after considering transport?

        Market A: price 2500, transport 100
        Market B: price 2650, transport 80
        Market C: price 2700, transport 250
        """
    )

    assert response
    assert "B" in response


@pytest.mark.anyio
async def test_claude_handles_buy_decision():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        The current tomato price is 2000 per quintal.
        The predicted future price is 2100 per quintal.
        I need to buy 10 quintals.
        Should I buy now?
        """
    )

    assert response
    assert "BUY" in response.upper()


@pytest.mark.anyio
async def test_claude_handles_sell_decision():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I can sell tomatoes today for 2000 per quintal.
        The predicted future price is 2100 per quintal.
        Should I sell now or wait?
        """
    )

    assert response
    assert "WAIT" in response.upper()

@pytest.mark.anyio
async def test_claude_handles_price_forecast():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        Forecast the next market price for this tomato series.

        Historical data:

        Date: 2026-09-01
        State: West Bengal
        District: Nadia
        Market: Krishnanagar
        Commodity: Tomato
        Variety: Local
        Grade: A
        Min Price: 1900
        Max Price: 2100
        Modal Price: 2000
        Price Unit: Rs./Quintal
        Arrival Quantity: 100
        Arrival Unit: Quintal

        Date: 2026-09-02
        State: West Bengal
        District: Nadia
        Market: Krishnanagar
        Commodity: Tomato
        Variety: Local
        Grade: A
        Min Price: 1950
        Max Price: 2150
        Modal Price: 2050
        Price Unit: Rs./Quintal
        Arrival Quantity: 110
        Arrival Unit: Quintal

        Date: 2026-09-03
        State: West Bengal
        District: Nadia
        Market: Krishnanagar
        Commodity: Tomato
        Variety: Local
        Grade: A
        Min Price: 2000
        Max Price: 2200
        Modal Price: 2100
        Price Unit: Rs./Quintal
        Arrival Quantity: 105
        Arrival Unit: Quintal

        What is the expected future price?
        """
    )

    assert response
    assert isinstance(response, str)


@pytest.mark.anyio
async def test_claude_handles_best_time():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I want to sell my tomatoes.
        These are the predicted prices for the coming days:

        2026-09-06: 2400
        2026-09-07: 2460
        2026-09-08: 2510

        Which date is the best time to sell?
        """
    )

    assert response
    assert "2026-09-08" in response


@pytest.mark.anyio
async def test_claude_handles_net_return():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I am selling 10 quintals at ₹2500 per quintal.

        Transport cost: ₹100 per quintal
        Storage cost: ₹50 per quintal
        Other costs: ₹20 per quintal

        How much will my net return be?
        """
    )

    assert response
    assert "23,300" in response


@pytest.mark.anyio
async def test_claude_handles_buyer_matching():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I am a farmer with 50 quintals of Tomato.

        Grade: A
        Variety: Hybrid
        Location: Nadia
        Expected selling price: ₹2300 per quintal.

        Find the best buyer for my produce from the available buyer requirements.
        """
    )

    assert response
    assert "buyer" in response.lower()
    assert "match" in response.lower()


@pytest.mark.anyio
async def test_claude_handles_farmer_matching():

    agent = ClaudeAgent()

    response = await agent.ask_with_mcp(
        """
        I am a buyer looking for:

        Commodity: Tomato
        Variety: Local
        Required quantity: 50 quintals
        Grade: A
        Location: Nadia
        Offered price: ₹2300
        Required by: 2026-09-07

        Available farmer lots:

        F001:
        Lot ID: L001
        Commodity: Tomato
        Variety: Local
        Quantity: 50 quintals
        Grade: A
        Location: Nadia
        Expected price: ₹2200
        Available date: 2026-09-06

        F002:
        Lot ID: L002
        Commodity: Tomato
        Variety: Local
        Quantity: 30 quintals
        Grade: A
        Location: Kolkata
        Expected price: ₹2200
        Available date: 2026-09-06

        F003:
        Lot ID: L003
        Commodity: Potato
        Variety: Local
        Quantity: 50 quintals
        Grade: A
        Location: Nadia
        Expected price: ₹2000
        Available date: 2026-09-06

        Which farmer lot is the best match?
        """
    )

    assert response
    assert "F001" in response    