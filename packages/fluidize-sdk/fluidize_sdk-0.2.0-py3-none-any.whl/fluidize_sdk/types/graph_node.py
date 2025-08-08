# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["GraphNode", "Data", "Position"]


class Data(BaseModel):
    label: str

    simulation_id: str


class Position(BaseModel):
    x: float

    y: float


class GraphNode(BaseModel):
    id: str

    data: Data

    position: Position

    type: str
