import asyncio

from mcp import Client
from src.mcp.server import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "forecast_price",
            {
                "state": "West Bengal",
                "district": "Nadia",
                "market": "Ranaghat APMC",
                "commodity": "Tomato",
                "variety": "Other",
                "grade": "FAQ",
            },
        )

        print("is_error:", result.is_error)
        print("content:", result.content)


asyncio.run(main())