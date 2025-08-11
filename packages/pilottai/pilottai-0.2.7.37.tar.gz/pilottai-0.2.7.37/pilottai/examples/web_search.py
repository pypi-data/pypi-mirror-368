from pilottai import Pilott
from pilottai.core.base_config import LLMConfig
from pilottai.tools import Tool



async def main():
    # Initialize PilottAI Serve
    pilott = Pilott(name="WebSearchAgent")

    # Configure LLM
    llm_config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key"
    )

    # Create web search tools
    search_executor = Tool(
        name="search_executor",
        description="Execute web searches",
        function=lambda **kwargs: print(f"Executing search: {kwargs}"),
        parameters={
            "query": "str",
            "search_type": "str",
            "filters": "dict"
        }
    )

    result_analyzer = Tool(
        name="result_analyzer",
        description="Analyze search results",
        function=lambda **kwargs: print(f"Analyzing results: {kwargs}"),
        parameters={
            "results": "list",
            "criteria": "list"
        }
    )

    # Create web search agent
    search_agent = await pilott.add_agent(
        title="web_searcher",
        goal="Execute and analyze web searches effectively",
        tools=[search_executor, result_analyzer],
        llm_config=llm_config
    )

    # Example job
    jobs = [
        {
            "type": "web_search",
            "query": "latest AI developments 2024",
            "search_type": "news",
            "filters": {
                "date_range": "last_month",
                "sources": ["tech_news", "research_papers"]
            }
        },
        {
            "type": "analyze_results",
            "results": ["result1", "result2"],
            "criteria": ["relevance", "credibility"]
        }
    ]

    # Execute job
    results = await pilott.serve(jobs)
    for job, result in zip(jobs, results):
        print(f"Job type: {job['type']}")
        print(f"Result: {result.output}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
