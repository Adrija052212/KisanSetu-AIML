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
                "best_farmers",
                arguments={
                    "buyer_requirement": {
                        "commodity": "Tomato",
                        "required_quantity": 50,
                        "grade": "A",
                        "location": "Nadia",
                        "variety": "Hybrid",
                        "offered_price": 2500,
                    },
                    "farmers": [
                        {
                            "farmer_id": "F001",
                            "lot_id": "L001",
                            "name": "Farmer One",
                            "commodity": "Tomato",
                            "quantity": 70,
                            "grade": "A",
                            "location": "Nadia",
                            "variety": "Hybrid",
                            "expected_price": 2400,
                        },
                        {
                            "farmer_id": "F002",
                            "lot_id": "L002",
                            "name": "Farmer Two",
                            "commodity": "Tomato",
                            "quantity": 40,
                            "grade": "A",
                            "location": "Nadia",
                            "variety": "Hybrid",
                            "expected_price": 2300,
                        },
                        {
                            "farmer_id": "F003",
                            "lot_id": "L003",
                            "name": "Farmer Three",
                            "commodity": "Potato",
                            "quantity": 100,
                            "grade": "A",
                            "location": "Nadia",
                            "variety": "Hybrid",
                            "expected_price": 2000,
                        },
                    ],
                },
            )

            print("\n===== BEST FARMERS MCP RESULT =====")

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

            print("====================================\n")


if __name__ == "__main__":
    asyncio.run(main())