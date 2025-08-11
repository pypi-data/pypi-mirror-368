from pilottai import Pilott
from pilottai.core.base_config import LLMConfig
from pilottai.tools import Tool

async def main():
    # Initialize PilottAI Serve
    pilott = Pilott(name="MarketingExpert")

    # Configure LLM
    llm_config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key"
    )

    # Create marketing tools
    content_creator = Tool(
        name="content_creator",
        description="Create marketing content",
        function=lambda **kwargs: print(f"Creating content: {kwargs}"),
        parameters={
            "content_type": "str",
            "target_audience": "str",
            "key_points": "list"
        }
    )

    campaign_analyzer = Tool(
        name="campaign_analyzer",
        description="Analyze campaign performance",
        function=lambda **kwargs: print(f"Analyzing campaign: {kwargs}"),
        parameters={
            "campaign_id": "str",
            "metrics": "list"
        }
    )

    # Create marketing agent
    marketing_agent = await pilott.add_agent(
        title="marketing_expert",
        goal="Create and optimize marketing campaigns",
        tools=[content_creator, campaign_analyzer],
        llm_config=llm_config
    )

    # Example job
    jobs = [
        {
            "type": "create_content",
            "content_type": "social_post",
            "target_audience": "tech professionals",
            "key_points": ["product launch", "key features"]
        },
        {
            "type": "analyze_campaign",
            "campaign_id": "CAMP123",
            "metrics": ["engagement", "conversion"]
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
