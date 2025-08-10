# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GraphInsertNodeParams", "Data", "Position"]


class GraphInsertNodeParams(TypedDict, total=False):
    query_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    body_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    data: Required[Data]

    position: Required[Position]

    type: Required[str]

    description: str

    label: str

    location: str

    metadata_version: str

    sim_global: bool

    status: str


class Data(TypedDict, total=False):
    label: Required[str]

    simulation_id: Required[str]


class Position(TypedDict, total=False):
    x: Required[float]

    y: Required[float]
