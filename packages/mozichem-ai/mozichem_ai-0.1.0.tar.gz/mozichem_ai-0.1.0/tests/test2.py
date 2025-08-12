# import libs
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

# load environment variables
load_dotenv()

# langchain
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACING_V2'] = os.getenv('LANGCHAIN_TRACING_V2')

# open ai
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# open ai
llm_openai = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

server_params_ = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["E:\\Python Projects\\mozichem-hub\\tests\\test2.py"],
)

# "eos-models-mcp": {
#                 "type": "stdio",
#                 "command": "uv",
#                 "args": [
#                     "--directory",
#                     "E:\\Python Projects\\mozichem-hub\\tests",
#                     "run",
#                     "test1.py"
#                 ]
#             },
server_params = StdioServerParameters(
    command="uv",
    args=[
        "--directory",
        "E:\\Python Projects\\mozichem-hub\\tests",
        "run",
        "test1.py"
    ],
)


async def main():
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                try:
                    # Initialize the connection
                    await session.initialize()

                    # Get tools
                    tools = await load_mcp_tools(session)

                    # Create the agent
                    agent = create_react_agent(
                        model=llm_openai,
                        tools=tools
                    )

                    # Chat loop
                    while True:
                        user_input = input("You: ")
                        if user_input.lower() == "quit":
                            print("Exiting chat. Goodbye!")
                            break

                        agent_response = await agent.ainvoke(
                            {"messages": user_input}
                        )

                        print("Agent Response:",
                              agent_response['messages'][-1].content)
                except Exception as e:
                    print("Error during session operations:", e)
    except Exception as e:
        print("Error initializing stdio client or ClientSession:", e)

if __name__ == "__main__":
    asyncio.run(main())
