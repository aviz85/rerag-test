from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from openai import AsyncOpenAI

class Document(BaseModel):
    name: str
    content: str
    metadata: Dict[str, Any] = {}

class Response(BaseModel):
    content: str
    reasoning: str
    is_irrelevant: bool
    document: Document

OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-001",
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-2024-11-20",
    "cohere/command-r-plus-08-2024",
    "x-ai/grok-2-1212"
]

class ReagClient:
    def __init__(self, model: str, api_base: Optional[str] = None, system: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.system = system or ""
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def query(self, query: str, documents: List[Document], options: Optional[Dict] = None) -> Response:
        prompt = f"""Given the following documents, answer the query.
        
Documents:
{chr(10).join(f'[{doc.name}]: {doc.content}' for doc in documents)}

Query: {query}

Respond in the following format:
Content: <your answer>
Reasoning: <your reasoning>
Is Irrelevant: <true/false>
Document Used: <document name>
"""
        
        messages = []
        if self.system:
            messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": prompt})
        
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://github.com/superagent-ai/reag",
                "X-Title": "ReAG Demo",
            }
        )
        
        content = completion.choices[0].message.content
        parts = content.split('\n')
        
        content_text = next((p.replace('Content:', '').strip() for p in parts if p.startswith('Content:')), '')
        reasoning = next((p.replace('Reasoning:', '').strip() for p in parts if p.startswith('Reasoning:')), '')
        is_irrelevant = next((p.replace('Is Irrelevant:', '').strip().lower() == 'true' for p in parts if p.startswith('Is Irrelevant:')), False)
        doc_name = next((p.replace('Document Used:', '').strip() for p in parts if p.startswith('Document Used:')), documents[0].name)
        doc = next((d for d in documents if d.name == doc_name), documents[0])
        
        return Response(
            content=content_text,
            reasoning=reasoning,
            is_irrelevant=is_irrelevant,
            document=doc
        ) 