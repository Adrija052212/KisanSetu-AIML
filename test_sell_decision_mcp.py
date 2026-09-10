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

            tools = await session.list_tools()

            print("\n===== AVAILABLE MCP TOOLS =====")

            for tool in tools.tools:
                print("-", tool.name)

            print("===============================\n")

            result = await session.call_tool(
                "sell_decision",
                {
                    "state": "West Bengal",
                    "district": "Nadia",
                    "market": "Ranaghat APMC",
                    "commodity": "Tomato",
                    "variety": "Other",
                    "grade": "FAQ",
                    "quantity": 50,
                    "transport_cost": 0,
                    "min_change_percent": 0,
                },
            )

            print("\n===== SELL DECISION RESULT =====")

            for content in result.content:
                print(content.text)

            print("================================\n")


if __name__ == "__main__":
    asyncio.run(main())