from pydantic import BaseModel


class Base(BaseModel):
    """Base model with custom serialization"""

    def __str__(self):
        return self.model_dump_json(indent=4)

    def __repr__(self):
        return self.__str__()
