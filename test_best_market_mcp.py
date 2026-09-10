import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp.server"],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "best_market",
                {
                    "state": "West Bengal",
                    "district": "Nadia",
                    "commodity": "Tomato",
                    "quantity": 50,
                    "mode": "sell",
                    "transport_costs": {}
                },
            )

            print("\n===== BEST MARKET MCP RESULT =====")

            for content in result.content:
                print(content.text)

            print("==================================\n")


if __name__ == "__main__":
    asyncio.run(main())