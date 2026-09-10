import asyncio
import json

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
                arguments={
                    "state": "West Bengal",
                    "district": "Nadia",
                    "commodity": "Tomato",
                    "quantity": 50,
                    "mode": "buy",
                },
            )

            print("\n===== BEST MARKET BUY MCP RESULT =====")

            for content in result.content:
                if hasattr(content, "text"):
                    try:
                        data = json.loads(content.text)

                        print(
                            json.dumps(
                                data,
                                indent=2,
                                ensure_ascii=False,
                            )
                        )

                    except json.JSONDecodeError:
                        print(content.text)

                else:
                    print(content)

            print("=======================================\n")


if __name__ == "__main__":
    asyncio.run(main())