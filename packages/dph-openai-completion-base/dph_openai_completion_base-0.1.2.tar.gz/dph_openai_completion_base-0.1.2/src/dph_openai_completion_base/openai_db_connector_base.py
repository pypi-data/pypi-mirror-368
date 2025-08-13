import abc

class OpenAIDBConnectorBase(abc.ABC):
    @abc.abstractmethod
    async def get_vector_store_id(self):
        pass

    @abc.abstractmethod
    async def get_chat_completion_history(self, thread_id: str):
        pass

    @abc.abstractmethod
    async def set_chat_completion_history(self, thread_id: str, history):
        pass