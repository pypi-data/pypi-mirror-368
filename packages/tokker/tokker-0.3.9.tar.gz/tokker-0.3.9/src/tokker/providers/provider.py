from abc import ABC, abstractmethod


class Provider(ABC):
    @abstractmethod
    def tokenize(
        self,
        text: str,
        model_name: str,
    ) -> dict[str, str | int | list[str] | list[int]]:
        pass
