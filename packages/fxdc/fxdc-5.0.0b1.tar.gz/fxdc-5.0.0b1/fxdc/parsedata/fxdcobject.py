import json
from typing import Any


class FxDCObject:
    """
    FxDC Object class
    -----------------
    Contains All the Data Extracted from the FxDC File
    """

    def dict(self):
        """
        Convert the Object to a Dictionary
        """
        return self.__dict__

    def json(self):
        """
        Convert the Object to a JSON

        !!! MIGHT RAISE ERROR IF OBJECT IS NOT JSON SERIALIZABLE !!!
        """
        return json.dumps(self.original, indent=4)

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def __iter__(self):
        return iter(self.__dict__.items())

    def __serialize__(self):
        """
        Serialize the Object to a Dictionary
        """
        return self.__dict__

    @property
    def original(self) -> object:
        """
        Get the Original Object
        """
        if len(self.__dict__) == 0:
            raise ValueError("The Object is Empty")
        if len(self.__dict__) == 1:
            if "main" in self.__dict__:
                return self.__dict__["main"]
        return self.__dict__

    @original.setter
    def original(self, value: Any) -> None:
        """
        Set the Original Object
        """
        self.__dict__["original"] = value
