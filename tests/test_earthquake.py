# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from datetime import datetime

import pytest

import pystac
from pystac.extensions.earthquake import (
    DEPTH_PROP,
    EARTHQUAKE_EXTENSION_HOOKS,
    FELT_PROP,
    MAGNITUDE_PROP,
    MAGNITUDE_TYPE_PROP,
    SOURCES_PROP,
    STATUS_PROP,
    TSUNAMI_PROP,
    EarthquakeExtension,
    EarthquakeSource,
)


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def make_item() -> pystac.Item:
    return pystac.Item(
        id="eq-item",
        geometry=None,
        bbox=None,
        datetime=_dt("2020-01-01T00:00:00Z"),
        properties={},
        start_datetime=None,
        end_datetime=None,
    )


def test_item_apply_roundtrip() -> None:
    item = make_item()
    ext = EarthquakeExtension.ext(item, add_if_missing=True)

    magnitude = 6.1
    felt_count = 12
    depth = 8.4
    sources: list[EarthquakeSource] = [{"name": "usgs", "code": "ak021"}]
    ext.apply(
        magnitude=magnitude,
        sources=sources,
        magnitude_type="mww",
        felt=felt_count,
        status="reviewed",
        tsunami=False,
        depth=depth,
    )

    assert item.properties[MAGNITUDE_PROP] == magnitude
    assert item.properties[SOURCES_PROP] == sources
    assert item.properties[MAGNITUDE_TYPE_PROP] == "mww"
    assert item.properties[FELT_PROP] == felt_count
    assert item.properties[STATUS_PROP] == "reviewed"
    assert item.properties[TSUNAMI_PROP] is False
    assert item.properties[DEPTH_PROP] == depth

    assert ext.magnitude == magnitude
    assert ext.sources == sources
    assert ext.magnitude_type == "mww"
    assert ext.status == "reviewed"


def test_validation_errors() -> None:
    item = make_item()
    ext = EarthquakeExtension.ext(item, add_if_missing=True)

    with pytest.raises(ValueError):
        ext.magnitude = 25.0

    with pytest.raises(ValueError):
        ext.felt = -1

    with pytest.raises(ValueError):
        ext.sources = []

    with pytest.raises(ValueError):
        ext.sources = [{"name": "usgs"}]


def test_asset_reads_from_owner_and_writes_to_asset() -> None:
    item = make_item()
    iext = EarthquakeExtension.ext(item, add_if_missing=True)
    magnitude = 5.0
    depth = 7.5
    iext.magnitude = magnitude

    asset = pystac.Asset(href="s3://bucket/quake.json")
    item.add_asset("quake", asset)

    aext = EarthquakeExtension.ext(asset)
    assert aext.magnitude == magnitude

    aext.depth = depth
    assert asset.extra_fields[DEPTH_PROP] == depth


def test_extension_hooks_are_declared() -> None:
    assert EARTHQUAKE_EXTENSION_HOOKS.schema_uri == EarthquakeExtension.get_schema_uri()
    assert "eq" in EARTHQUAKE_EXTENSION_HOOKS.prev_extension_ids
    assert pystac.STACObjectType.ITEM in EARTHQUAKE_EXTENSION_HOOKS.stac_object_types


@pytest.mark.parametrize(
    "source",
    [
        {"code": "ak021"},
        {"name": "", "code": "ak021"},
        {"name": "usgs", "code": ""},
        {"name": "usgs", "code": "ak021", "catalog": ""},
    ],
)
def test_rejects_incomplete_source_records(source: EarthquakeSource) -> None:
    extension = EarthquakeExtension.ext(make_item(), add_if_missing=True)
    with pytest.raises(ValueError, match="eq:sources"):
        extension.sources = [source]


def test_sources_preserve_catalog_and_can_be_removed() -> None:
    item = make_item()
    extension = EarthquakeExtension.ext(item, add_if_missing=True)
    sources: list[EarthquakeSource] = [
        {"name": "usgs", "code": "ak021", "catalog": "us"},
        {"name": "emsc", "code": "123"},
    ]
    extension.sources = sources
    assert extension.sources == sources
    extension.sources = None
    assert extension.sources is None
    assert SOURCES_PROP not in item.properties
