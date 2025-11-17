import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.url_context_tool  import UrlContextTool

load_dotenv()

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = 'urlcontextmanager'

load_any_page_tool = UrlContextTool()

root_agent = Agent(
        model=MODEL,
        name=AGENT_APP_NAME,
        description="Shoppiing assistant",
        instruction="You are helpful shopping assistant.",
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        tools = [load_any_page_tool],
)