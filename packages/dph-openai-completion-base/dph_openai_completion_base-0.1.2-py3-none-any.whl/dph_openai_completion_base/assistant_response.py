from pydantic import BaseModel

class AssistantResponse(BaseModel):
    final_response_str: str|None
    called_functions: dict