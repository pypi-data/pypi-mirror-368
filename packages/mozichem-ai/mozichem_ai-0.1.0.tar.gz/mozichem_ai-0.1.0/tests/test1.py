# import libs
import traceback
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# models
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
# mcp
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
# agents
from langgraph.prebuilt import create_react_agent
# python dot env
from dotenv import load_dotenv

# SECTION: environment variables
# load environment variables
load_dotenv()

# langchain
langchain_api_key = os.getenv('LANGCHAIN_API_KEY')
if langchain_api_key:
    os.environ['LANGCHAIN_API_KEY'] = langchain_api_key

langchain_tracing = os.getenv('LANGCHAIN_TRACING_V2')
if langchain_tracing:
    os.environ['LANGCHAIN_TRACING_V2'] = langchain_tracing

# open ai
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    os.environ['OPENAI_API_KEY'] = openai_api_key
else:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# NOTE: llm initialization
# open ai
llm_openai = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# SECTION: MCP client

# NOTE: math server
math_server = {
    "command": "python",
    "args": ["E:\\Python Projects\\LLM\\mcp2\\math-server.py"],
    "transport": "stdio",
}

# NOTE: eos models mcp
# E:\Python Projects\mozichem-hub\tests\test1.py
eos_models_mcp = {
    "command": "python",
    "args": ["E:\\Python Projects\\mozichem-hub\\tests\\test1.py"],
    "transport": "stdio",
}


# NOTE: client
# client = MultiServerMCPClient(
#     {
#         "eos_models": eos_models_mcp,
#     },
# )


async def main():
    try:
        client = MultiServerMCPClient(
            {
                "eos_models": eos_models_mcp,
            },
        )

        # Get tools
        tools = await client.get_tools()

        # Create the agent
        agent = create_react_agent(model=llm_openai, tools=tools)

        # Chat loop
        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                print("Exiting chat. Goodbye!")
                break

            agent_response = await agent.ainvoke(
                {"messages": user_input}
            )

            print("Agent Response:", agent_response['messages'][-1].content)

    except Exception as e:
        print("Error initializing stdio client or ClientSession:", e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
