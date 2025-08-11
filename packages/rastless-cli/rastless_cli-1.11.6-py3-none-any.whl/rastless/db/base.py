import uuid

from pydantic import BaseModel, model_validator


def camel_case(string: str) -> str:
    return "".join(word.capitalize() if i > 0 else word for i, word in enumerate(string.split("_")))


def str_uuid():
    return str(uuid.uuid4())


class DynamoBaseModel(BaseModel):
    _pk_tag: str
    _pk_value: str = None
    _sk_tag: str
    _sk_value: str = None
    pk: str = None
    sk: str = None

    def __eq__(self, other):
        return self.pk == other.pk and self.sk == other.sk

    @model_validator(mode="after")
    def new(self):
        self.pk = self.create_tag(self._pk_tag, self._pk_value)
        self.sk = self.create_tag(self._sk_tag, self._sk_value)
        return self

    def create_tag(self, tag, value):
        return tag if not value else f"{tag}#{getattr(self, value)}"

    class Config:
        populate_by_name = True
        alias_generator = camel_case
