import asyncio

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("\nAvailable MCP tools:")
            for tool in tools.tools:
                print("-", tool.name)

            result = await session.call_tool(
                "current_price",
                {
                    "date": "2026-09-08",
                    "state": "West Bengal",
                    "district": "Nadia",
                    "market": "Ranaghat APMC",
                    "commodity": "Tomato",
                    "variety": "Other",
                    "grade": "FAQ",
                },
            )

            print("\n===== CURRENT PRICE RESULT =====")
            print(result)
            print("================================")


if __name__ == "__main__":
    asyncio.run(main())