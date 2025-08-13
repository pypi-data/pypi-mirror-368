from .abstract_callback import AbstractCallback
import abc

class AbstractCallbackFactory(abc.ABC):
    @abc.abstractmethod
    def make(self, function_name, thread_id) -> AbstractCallback:
        pass