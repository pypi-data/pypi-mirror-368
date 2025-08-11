from haiku.rag.client import HaikuRAG
from haiku.rag.qa.prompts import SYSTEM_PROMPT


class QuestionAnswerAgentBase:
    _model: str = ""
    _system_prompt: str = SYSTEM_PROMPT

    def __init__(self, client: HaikuRAG, model: str = ""):
        self._model = model
        self._client = client

    async def answer(self, question: str) -> str:
        raise NotImplementedError(
            "QABase is an abstract class. Please implement the answer method in a subclass."
        )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_documents",
                "description": "Search the knowledge base for relevant documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant documents",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            },
        }
    ]
