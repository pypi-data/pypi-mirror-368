import abc

class AbstractCallback(abc.ABC):

    @abc.abstractmethod
    async def process(self, function_args):
        pass