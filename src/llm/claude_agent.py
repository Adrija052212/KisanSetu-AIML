import os

from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import Client

from src.mcp.server import mcp


load_dotenv()


class ClaudeAgent:

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set."
            )

        self.client = Anthropic(
            api_key=api_key
        )

        self.conversation_history = []

    def ask(self, user_message: str) -> str:
        """Send a normal message to Claude."""

        self.conversation_history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=512,
            messages=self.conversation_history,
        )

        assistant_text = ""

        for block in response.content:
            if block.type == "text":
                assistant_text += block.text

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": assistant_text,
            }
        )

        return assistant_text

    def reset_conversation(self):
        """Clear the conversation history."""

        self.conversation_history = []

    async def ask_with_mcp(
        self,
        user_message: str,
        language: str = "English",
        location: str | None = None,
    ) -> str:
        """Send a message to Claude with MCP tools."""

        system_prompt = (
            "You are KisanSetu AI, an intelligent agricultural market "
            "FARMER CONTEXT:\n"
            f"- Farmer location: {location or 'Not provided'}\n"
            "- The farmer's district is Ahilyanagar (formerly Ahmednagar) "
            "and the state is Maharashtra.\n"
            "- When using KisanSetu market tools, use the canonical district "
            "name 'Ahilyanagar', not 'Ahmednagar'.\n"
            "- Use this location when it is relevant to the user's question.\n"
            "- Do not ask the farmer for their location again if it "
            "has already been provided in this context.\n"
            "- If a market, variety, or grade is required by a tool "
            "and is not known, ask the farmer only for the missing "
            "information.\n\n"
            "decision-support assistant for farmers and agricultural "
            "market participants in India.\n\n"

            "Your purpose is to help users make better decisions about "
            "agricultural buying and selling using reliable KisanSetu "
            "data, predictions, calculations, and matching tools.\n\n"

            "KISANSETU CAPABILITIES:\n"
            "1. Forecast future market prices.\n"
            "2. Recommend whether to buy now or wait.\n"
            "3. Recommend whether to sell now or wait.\n"
            "4. Identify the best market for buying or selling.\n"
            "5. Identify the best future time to buy or sell.\n"
            "6. Calculate expected net return after applicable costs.\n"
            "7. Find suitable buyers for a farmer's crop lot.\n"
            "8. Find suitable farmer lots for a buyer's requirement.\n\n"

            "TOOL USAGE RULES:\n"
            "- Use KisanSetu tools whenever the question requires a "
            "calculation, prediction, recommendation, market comparison, "
            "current price, or matching result.\n"
            "- Do not invent current prices, predicted prices, market data, "
            "buyer information, farmer information, or recommendation "
            "results.\n"
            "- Use the farmer context to resolve location-based questions. "
            "If the user says 'my area', 'near me', 'my market', or similar, "
            "use the farmer location already provided in FARMER CONTEXT.\n"
            "- When the user asks for a current price and does not specify "
            "a market, first use the best_market tool to identify a suitable "
            "market using the farmer's state, district, and commodity. "
            "Do not ask the farmer for the market name before trying this.\n"
            "- After best_market identifies a suitable market, use the "
            "current_price tool to obtain the current price for that market.\n"
            "- For current price questions, use today's date unless the user "
            "explicitly asks for another date.\n"
            "- Use the complete market name returned by best_market when "
            "calling current_price.\n"
            "- Do not ask for variety or grade unless the current_price tool "
            "actually requires them or the available data cannot be resolved "
            "without them. Both variety and grade are optional for current_price.\n"
            "- If best_market cannot identify a suitable market, then explain "
            "that a suitable market could not be found rather than immediately "
            "asking the farmer for a market name.\n"
            "- For price forecasts, variety and grade are optional. "
            "If the user provides them, try the requested combination first. "
            "If historical data is unavailable for that exact combination, "
            "allow the forecasting tool to use an available historical series "
            "for the same market and commodity.\n"
            "- If the forecasting tool returns fallback_used=true, clearly "
            "tell the farmer which variety and grade were actually used for "
            "the forecast. Do not claim that the forecast was generated for "
            "the originally requested unavailable combination.\n"

            "MATCHING RESULT RULES:\n"
            "- Preserve the exact scores, score denominators, match score, "
            "match level, rank, names, prices, quantities, and other "
            "values returned by matching tools.\n"
            "- Do not recalculate or change score denominators.\n"
            "- For example, if quantity_score is 15 out of a maximum "
            "weight of 20, report 15/20, not 15/15.\n"
            "- Do not claim that there are no competing matches or "
            "alternatives unless the tool result explicitly establishes "
            "that.\n"
            "- Do not invent farmer or buyer names when a name is not "
            "provided by the tool.\n\n"

            "DATA ACCURACY RULES:\n"
            "- Preserve commodity names, market names, locations, "
            "quantities, dates, and prices accurately.\n"
            "- When a user provides a market name, preserve the complete "
            "market name exactly as provided.\n"
            "- Do not shorten or remove official terms such as APMC, "
            "Mandi, Market, or other market-name components.\n"
            "- When calling a market-specific tool, use the complete "
            "market name provided by the user.\n\n"

            "ERROR HANDLING:\n"
            "- If a tool reports that the requested market, commodity, "
            "variety, grade, or combination is unavailable, explain that "
            "the requested combination was not found.\n"
            "- Do not describe such a result as a general system outage "
            "unless the tool explicitly indicates a system failure.\n\n"

            "RESPONSE STYLE:\n"
            "- Be clear, concise, practical, and farmer-friendly.\n"
            "- Avoid unnecessary technical terminology.\n"
            "- Give the recommendation first when applicable.\n"
            "- Follow with the important supporting values.\n"
            "- Use bullet points when useful.\n"
            "- Never present uncertain predictions as guaranteed outcomes.\n\n"

            "SCOPE:\n"
            "- Focus on agricultural market intelligence, trading "
            "decisions, price forecasting, market selection, timing, "
            "buyer-farmer matching, and financial outcomes related to "
            "agricultural transactions.\n"
            "- Do not pretend to provide information that is unavailable "
            "through KisanSetu or its connected tools.\n\n"

            "LANGUAGE:\n"
            "- Respond in the language selected by the application.\n"
            f"- The selected language for this conversation is: {language}.\n"
            "- Do not ask the user to select a language.\n"
            "- Do not switch languages unless the application provides "
            "a different language.\n"
            "- Keep numerical values, prices, quantities, dates, and "
            "market names accurate.\n"
        )

        async with Client(mcp) as mcp_client:

            tools_result = await mcp_client.list_tools()

            claude_tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.input_schema,
                }
                for tool in tools_result.tools
            ]

            self.conversation_history.append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

            while True:

                response = self.client.messages.create(
                    model="claude-sonnet-5",
                    max_tokens=1024,
                    system=system_prompt,
                    tools=claude_tools,
                    messages=self.conversation_history,
                )

                if response.stop_reason == "end_turn":

                    text_parts = [
                        block.text
                        for block in response.content
                        if block.type == "text"
                    ]

                    assistant_text = "\n".join(text_parts)

                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response.content,
                        }
                    )

                    return assistant_text

                if response.stop_reason == "tool_use":

                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": response.content,
                        }
                    )

                    tool_results = []

                    for block in response.content:

                        if block.type != "tool_use":
                            continue

                        result = await mcp_client.call_tool(
                            block.name,
                            block.input,
                        )

                        tool_text = ""

                        if result.content:
                            for content_block in result.content:
                                if hasattr(content_block, "text"):
                                    tool_text += content_block.text

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": tool_text,
                            }
                        )

                    self.conversation_history.append(
                        {
                            "role": "user",
                            "content": tool_results,
                        }
                    )

                else:

                    raise RuntimeError(
                        "Unexpected Claude stop reason: "
                        f"{response.stop_reason}"
                    )