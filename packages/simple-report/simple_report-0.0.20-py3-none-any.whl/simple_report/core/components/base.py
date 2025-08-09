
from abc import ABC, abstractmethod


class BaseElement(ABC):

    def __init__(self, id=None, class_name=None, style=None, **kwargs):
        self.id = id
        self.class_name = class_name
        self.style = style
        self.kwargs = kwargs

    @abstractmethod
    def to_html(self, **kwargs):
        pass

    def __str__(self):
        return self.__class__.__name__
