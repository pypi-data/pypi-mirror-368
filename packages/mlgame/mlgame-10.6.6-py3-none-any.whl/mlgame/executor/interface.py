import abc


class ExecutorInterface(abc.ABC):
    @abc.abstractmethod
    def run(self):
        pass