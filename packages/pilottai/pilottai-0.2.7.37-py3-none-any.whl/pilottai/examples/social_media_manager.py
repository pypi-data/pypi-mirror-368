from pilottai import Pilott
from pilottai.core.base_config import LLMConfig
from pilottai.tools import Tool

async def main():
    # Initialize PilottAI Serve
    pilott = Pilott(name="SocialMediaManager")

    # Configure LLM
    llm_config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key"
    )

    # Create social media tools
    content_scheduler = Tool(
        name="content_scheduler",
        description="Schedule social media content",
        function=lambda **kwargs: print(f"Scheduling content: {kwargs}"),
        parameters={
            "platform": "str",
            "content": "str",
            "schedule_time": "str",
            "media_attachments": "list"
        }
    )

    engagement_analyzer = Tool(
        name="engagement_analyzer",
        description="Analyze social media engagement",
        function=lambda **kwargs: print(f"Analyzing engagement: {kwargs}"),
        parameters={
            "post_id": "str",
            "metrics": "list",
            "timeframe": "str"
        }
    )

    # Create social media agent
    social_agent = await pilott.add_agent(
        title="social_media_manager",
        goal="Manage social media presence and engagement",
        tools=[content_scheduler, engagement_analyzer],
        llm_config=llm_config
    )

    # Example job
    jobs = [
        {
            "type": "schedule_content",
            "platform": "twitter",
            "content": "Excited to announce our latest feature release! #TechNews",
            "schedule_time": "2024-03-15T10:00:00Z"
        },
        {
            "type": "analyze_engagement",
            "post_id": "POST123",
            "metrics": ["likes", "shares", "comments"],
            "timeframe": "last_24h"
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
