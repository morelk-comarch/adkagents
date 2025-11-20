import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools import VertexAiSearchTool
from google.adk.apps import App
from google.adk.plugins.bigquery_logging_plugin import BigQueryAgentAnalyticsPlugin

load_dotenv()

instruction_prompt = """
        You are a Documentation Assistant. Your role is to provide accurate and detailed
        answers to questions based on documents that are retrievable using provided tool. If you believe
        the user is just discussing, don't use the retrieval tool. But if the user is asking a question and you are
        uncertain about a query, ask clarifying questions; if you cannot
        provide an answer, clearly explain why.

        When crafting your answer,
        you may use the retrieval tool to fetch code references or additional
        details. If you are not certain or the
        information is not available, clearly state that you do not have
        enough information.
        """

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = 'legalexpert'

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
SEARCH_DATASTORE_ID = os.getenv('SEARCH_DATASTORE_ID')

privatecorpus = VertexAiSearchTool(
    ##data_store_id = SEARCH_DATASTORE_ID,
    search_engine_id = SEARCH_ENGINE_ID,
    ##data_store_specs = [],
    max_results = 10
)

root_agent = Agent(
        model=MODEL,
        name=AGENT_APP_NAME,
        description="You are RAG expert",
        instruction=instruction_prompt,
        tools=[
            privatecorpus
        ]
)



bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, # project_id is required input from user
    dataset_id="adkevents", # dataset_id is required input from user
    table_id="agent_events" # Optional: defaults to "agent_events". The plugin automatically creates this table if it doesn't exist.
)

"""A plugin that logs agent analytic events to Google BigQuery."""
app = App(
    name="a01_send_logs_to_bigquery",
    root_agent=root_agent,
    plugins=[bq_logging_plugin],
)