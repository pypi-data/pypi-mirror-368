from pilottai import Pilott
from pilottai.core.base_config import LLMConfig
from pilottai.tools import Tool

async def main():
    # Initialize PilottAI Serve
    pilott = Pilott(name="DocumentProcessor")

    # Configure LLM
    llm_config = LLMConfig(
        model_name="gpt-4",
        provider="openai",
        api_key="your-api-key"
    )

    # Create document processing tools
    text_extractor = Tool(
        name="text_extractor",
        description="Extract text from documents",
        function=lambda **kwargs: print(f"Extracting text from: {kwargs}"),
        parameters={
            "file_path": "str",
            "format": "str"
        }
    )

    content_analyzer = Tool(
        name="content_analyzer",
        description="Analyze document content",
        function=lambda **kwargs: print(f"Analyzing content: {kwargs}"),
        parameters={
            "text": "str",
            "analysis_type": "str"
        }
    )

    summarizer = Tool(
        name="summarizer",
        description="Generate document summaries",
        function=lambda **kwargs: print(f"Generating summary: {kwargs}"),
        parameters={
            "text": "str",
            "max_length": "int"
        }
    )

    # Create document processing agent
    doc_processor = await pilott.add_agent(
        title="document_processor",
        goal="Process and analyze documents efficiently",
        tools=[text_extractor, content_analyzer, summarizer],
        llm_config=llm_config
    )

    # Example job
    job = {
        "type": "document_analysis",
        "description": "Analyze quarterly report",
        "document": {
            "path": "reports/q2_2024.pdf",
            "type": "pdf"
        },
        "agent": doc_processor
    }

    # Execute job
    result = await pilott.serve([job])
    print(f"Analysis result: {result[0].output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
