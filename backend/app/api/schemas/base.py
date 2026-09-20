from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base for all API schemas: serializes/accepts camelCase (matching the frontend contract)
    while keeping snake_case Python field names. `populate_by_name=True` lets input payloads use
    either form; `from_attributes=True` lets responses be built straight from domain
    dataclasses/SQLModel rows via `model_validate(obj)`."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
