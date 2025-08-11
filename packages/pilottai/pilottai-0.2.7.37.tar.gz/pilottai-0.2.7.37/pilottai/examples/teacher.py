from pilottai import Pilott
from pilottai.core.base_config import LLMConfig
from pilottai.tools import Tool

async def main():
    # Initialize PilottAI Serve
    pilott = Pilott(name="LearningAgent")

    # Configure LLM
    llm_config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key"
    )

    # Create learning tools
    knowledge_base = Tool(
        name="knowledge_base",
        description="Store and retrieve knowledge",
        function=lambda **kwargs: print(f"Knowledge operation: {kwargs}"),
        parameters={
            "operation": "str",
            "content": "str",
            "tags": "list"
        }
    )

    pattern_recognizer = Tool(
        name="pattern_recognizer",
        description="Identify patterns in data",
        function=lambda **kwargs: print(f"Pattern analysis: {kwargs}"),
        parameters={
            "data": "str",
            "pattern_type": "str"
        }
    )

    # Create learning agent
    await pilott.add_agent(
        title="learner",
        goal="Acquire and organize knowledge effectively",
        tools=[knowledge_base, pattern_recognizer],
        llm_config=llm_config
    )

    # Example job
    jobs = [
        {
            "type": "learn_topic",
            "content": "Introduction to Machine Learning",
            "store_results": True
        },
        {
            "type": "analyze_patterns",
            "data": "Historical market trends",
            "pattern_type": "trends"
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
