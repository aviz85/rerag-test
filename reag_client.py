from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from litellm import acompletion

class Document(BaseModel):
    name: str
    content: str
    metadata: Dict[str, Any] = {}

class Response(BaseModel):
    content: str
    reasoning: str
    is_irrelevant: bool
    document: Document

class ReagClient:
    def __init__(self, model: str, api_base: Optional[str] = None, system: Optional[str] = None):
        self.model = model
        self.api_base = api_base
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
        
        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system} if self.system else None,
                {"role": "user", "content": prompt}
            ],
            api_base=self.api_base
        )
        
        content = response.choices[0].message.content
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