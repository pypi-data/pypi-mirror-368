from decimal import Decimal
from typing import Annotated, List, Optional, Set

from pydantic import BaseModel, Field, PlainSerializer, ValidationError, field_validator, model_validator

from rastless.db.base import DynamoBaseModel, camel_case, str_uuid

FloatDecimal = Annotated[Decimal, PlainSerializer(lambda x: float(x), return_type=float, when_used="json")]


class LayerModel(DynamoBaseModel):
    layer_id: str = Field(default_factory=str_uuid)
    client: str
    product: str
    title: str
    region_id: int = 1
    unit: Optional[str] = None
    background_id: Optional[str] = None
    colormap: Optional[str] = None
    description: Optional[str] = None
    category: Optional[set[str]] = None

    _pk_tag = "layer"
    _sk_tag = "layer"
    _sk_value = "layer_id"

    @field_validator("category", mode="before")
    @classmethod
    def empty_category_to_none(cls, v):
        return v if v else None


class PermissionModel(DynamoBaseModel):
    permission: str
    layer_id: str

    _pk_tag = "permission"
    _pk_value = "permission"
    _sk_tag = "layer"
    _sk_value = "layer_id"


class CogFile(BaseModel):
    s3_filepath: str
    bbox: tuple[Decimal, Decimal, Decimal, Decimal]

    @classmethod
    @field_validator("bbox", mode="before")
    def to_decimal(cls, value):
        return [Decimal(str(item)) if not isinstance(item, Decimal) else item for item in value]

    class Config:
        populate_by_name = True
        alias_generator = camel_case


class LayerStepModel(DynamoBaseModel):
    layer_id: str
    cog_filepath: Optional[str] = None
    cog_layers: Optional[dict[str, CogFile]] = None
    datetime: str
    sensor: str
    resolution: Decimal
    temporal_resolution: str
    maxzoom: int
    minzoom: int
    bbox: tuple[Decimal, Decimal, Decimal, Decimal]

    _pk_tag = "step"
    _pk_value = "datetime"
    _sk_tag = "layer"
    _sk_value = "layer_id"

    @classmethod
    @field_validator("bbox", mode="before")
    def to_decimal(cls, value):
        return [Decimal(str(item)) if not isinstance(item, Decimal) else item for item in value]


class BaseColorMap(DynamoBaseModel):
    name: str
    description: Optional[str] = None

    _pk_tag = "cm"
    _sk_tag = "cm"
    _sk_value = "name"

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name and self.description == other.description

    @classmethod
    def colormap_factory(cls, item):
        cm_models = [MplColorMap, DiscreteColorMap, SldColorMap]
        for model in cm_models:
            try:
                return model.model_validate(item)
            except ValidationError:
                continue
        raise ValidationError("Colormap could not be validated.")


class SldColorMap(BaseColorMap):
    values: List[FloatDecimal]
    colors: List[List[FloatDecimal]]
    nodata: List[FloatDecimal]
    legend_image: Optional[str] = None

    _pk_tag = "cm"
    _sk_tag = "cm"
    _sk_value = "name"

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.values == other.values
            and self.colors == other.colors
            and self.nodata == other.nodata
            and self.legend_image == other.legend_image
        )


class DiscreteColorMap(BaseColorMap):
    values: List[int]
    colors: List[tuple[int, int, int, int]]
    labels: List[str]

    @model_validator(mode="after")
    def validate_list_lengths(self):
        if len(self.values) != len(self.colors) != len(self.labels):
            raise ValueError(f"Invalid colormap, cm#{self.sk} does not have same amount of colors, labels and values")
        return self

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.values == other.values
            and self.colors == other.colors
            and self.labels == other.labels
        )


class MplColorMap(BaseColorMap):
    min: FloatDecimal
    max: FloatDecimal
    log: bool
    cmap_name: str
    transparent_bounds: bool = False

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.min == other.min
            and self.max == other.max
            and self.log == other.log
            and self.cmap_name == other.cmap_name
            and self.transparent_bounds == other.transparent_bounds
        )


class AccessToken(DynamoBaseModel):
    token: str
    layer_ids: Set[str]

    _pk_tag = "token"
    _pk_value = "token"
    _sk_tag = "token"
