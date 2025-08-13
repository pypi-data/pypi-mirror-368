from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()


class MyCustomDuckDuckGoToolInput(BaseModel):
    """Input schema for MyCustomDuckDuckGoTool."""

    query: str = Field(..., description="URL to search for.")


class MyCustomDuckDuckGoTool(BaseTool):
    name: str = "DuckDuckGo Search Tool"
    description: str = "Search the web for a given query."
    args_schema: Type[BaseModel] = MyCustomDuckDuckGoToolInput

    def _run(self, query: str) -> str:
        duckduckgo_tool = DuckDuckGoSearchResults()
        response = duckduckgo_tool.invoke(query)
        return response


search_tool = MyCustomDuckDuckGoTool()

# Define Agents
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI and data science",
    backstory="Expert at identifying emerging trends; presents actionable insights.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)

writer = Agent(
    role="Tech Content Strategist",
    goal="Craft compelling content on tech advancements",
    backstory="Renowned strategist who transforms complex concepts into compelling narratives.",
    verbose=True,
    allow_delegation=True,
)

# Define Tasks
research_task = Task(
    description="Research recent trends in AI.",
    expected_output="A summary of latest AI developments.",
    agent=researcher,
)

writing_task = Task(
    description="Write a blog post based on the research summary.",
    expected_output="A well-structured tech blog post.",
    agent=writer,
)

# Define Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)

# # Kick off
# result = crew.kickoff(inputs={"topic": "AI trends"})
# print(result)
