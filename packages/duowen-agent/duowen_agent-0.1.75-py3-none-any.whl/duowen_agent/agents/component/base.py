from abc import ABC, abstractmethod
from typing import Any

from duowen_agent.utils.concurrency import make_async


class BaseComponent(ABC):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    async def arun(self, *args, **kwargs) -> Any:
        return await make_async(self.run(*args, **kwargs))

    # def run_for_stream(self, *args, **kwargs) -> Any:
    #     yield self.run(*args, **kwargs)
    #
    # async def arun_for_stream(self, *args, **kwargs) -> Any:
    #     raise NotImplementedError
