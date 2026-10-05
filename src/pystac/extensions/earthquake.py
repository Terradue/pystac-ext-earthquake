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

"""Implementation of the STAC :stac-ext:`Earthquake Extension <earthquake>`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, TypedDict, TypeVar, cast

from pystac.errors import ExtensionTypeError
from pystac.extensions.base import ExtensionManagementMixin, PropertiesExtension
from pystac.extensions.hooks import ExtensionHooks

import pystac

if TYPE_CHECKING:
    from collections.abc import Iterable

SCHEMA_URI: str = "https://stac-extensions.github.io/earthquake/v1.0.0/schema.json"

MAGNITUDE_PROP = "eq:magnitude"
MAGNITUDE_TYPE_PROP = "eq:magnitude_type"
FELT_PROP = "eq:felt"
STATUS_PROP = "eq:status"
TSUNAMI_PROP = "eq:tsunami"
SOURCES_PROP = "eq:sources"
DEPTH_PROP = "eq:depth"

MagnitudeType = Literal[
    "0",
    "2",
    "4",
    "fa",
    "H",
    "hn",
    "lg",
    "m",
    "ma",
    "mb",
    "MbLg",
    "mb_lg",
    "mc",
    "md",
    "mdl",
    "Me",
    "mfa",
    "mh",
    "Mi",
    "mint",
    "mj",
    "ml",
    "ml(texnet)",
    "mlg",
    "mlr",
    "mlv",
    "Ms",
    "ms_20",
    "ms_vx",
    "Mt",
    "muk",
    "mun",
    "mw",
    "mwb",
    "mwc",
    "mwp",
    "mwr",
    "mww",
    "no",
    "uk",
    "Unknown",
]
StatusType = Literal["automatic", "reviewed", "deleted"]


class EarthquakeSource(TypedDict, total=False):
    """A single source entry stored in the ``eq:sources`` field."""

    name: str
    code: str
    catalog: str


def _validate_magnitude(v: float | None) -> float | None:
    if v is None:
        return None
    if v < -3 or v > 10:
        raise ValueError(f"{MAGNITUDE_PROP} must be in [-3, 10]. Got: {v}")
    return float(v)


def _validate_felt(v: int | None) -> int | None:
    if v is None:
        return None
    if v < 0:
        raise ValueError(f"{FELT_PROP} must be >= 0. Got: {v}")
    return int(v)


def _validate_sources(
    sources: list[EarthquakeSource] | None,
) -> list[EarthquakeSource] | None:
    """Validate source records, preserving their order and contents.

    Raises:
        ValueError: If sources are empty, required keys are missing, or a
            source field is not a non-empty string.
    """
    if sources is None:
        return None
    if not sources:
        raise ValueError(f"{SOURCES_PROP} must have at least 1 source.")

    for index, source in enumerate(sources):
        _validate_source(source, index)

    return sources


def _validate_source(source: EarthquakeSource, index: int) -> None:
    """Validate one source, identifying invalid fields by their list position.

    Raises:
        ValueError: If required fields are absent or field values are empty
            or are not strings.
    """
    if "name" not in source or "code" not in source:
        raise ValueError(
            f"{SOURCES_PROP}[{index}] must include required keys 'name' and 'code'. Got: {source}"
        )
    for field in ("name", "code", "catalog"):
        if field == "catalog" and field not in source:
            continue
        value = source.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{SOURCES_PROP}[{index}].{field} must be a non-empty string.")


T = TypeVar("T", pystac.Item, pystac.Asset, pystac.ItemAssetDefinition)


class EarthquakeExtension(
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[pystac.Item | pystac.Collection],
):
    """
    Implements the STAC Earthquake Extension for Items and also supports reading/writing
    extension fields on Assets and Collection Item Asset Definitions.

    Schema: https://stac-extensions.github.io/earthquake/v1.0.0/schema.json
    """

    name: Literal["eq"] = "eq"

    @classmethod
    def get_schema_uri(cls) -> str:
        """Return the published schema URI for this extension."""
        return SCHEMA_URI

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False) -> EarthquakeExtension[T]:
        """
        Extend an Item, Asset, or ItemAssetDefinition with earthquake fields.

        Args:
            obj: The PySTAC object to wrap.
            add_if_missing: If ``True``, add the earthquake schema URI to the owning
                Item or Collection before returning the extension wrapper.
        """
        if isinstance(obj, pystac.Item):
            cls.ensure_has_extension(obj, add_if_missing)
            return cast("EarthquakeExtension[T]", ItemEarthquakeExtension(obj))
        if isinstance(obj, pystac.Asset):
            cls.ensure_owner_has_extension(obj, add_if_missing)
            return cast("EarthquakeExtension[T]", AssetEarthquakeExtension(obj))
        if isinstance(obj, pystac.ItemAssetDefinition):
            cls.ensure_owner_has_extension(obj, add_if_missing)
            return cast("EarthquakeExtension[T]", ItemAssetsEarthquakeExtension(obj))
        raise ExtensionTypeError(cls._ext_error_message(obj))

    def apply(
        self,
        *,
        magnitude: float,
        sources: list[EarthquakeSource],
        magnitude_type: MagnitudeType | None = None,
        felt: int | None = None,
        status: StatusType | None = None,
        tsunami: bool | None = None,
        depth: float | None = None,
    ) -> None:
        """
        Apply earthquake fields to the wrapped object.

        Note: schema marks `eq:magnitude` and `eq:sources` as required.
        """
        self.magnitude = magnitude
        self.sources = sources
        self.magnitude_type = magnitude_type
        self.felt = felt
        self.status = status
        self.tsunami = tsunami
        self.depth = depth

    @property
    def magnitude(self) -> float | None:
        """Magnitude of the earthquake event."""
        return self._get_property(MAGNITUDE_PROP, float)

    @magnitude.setter
    def magnitude(self, v: float | None) -> None:
        self._set_property(MAGNITUDE_PROP, _validate_magnitude(v), pop_if_none=True)

    @property
    def magnitude_type(self) -> MagnitudeType | None:
        """Magnitude scale used to compute :attr:`magnitude`."""
        return cast("MagnitudeType | None", self._get_property(MAGNITUDE_TYPE_PROP, str))

    @magnitude_type.setter
    def magnitude_type(self, v: MagnitudeType | None) -> None:
        self._set_property(MAGNITUDE_TYPE_PROP, v, pop_if_none=True)

    @property
    def felt(self) -> int | None:
        """Reported number of people who felt the event."""
        return self._get_property(FELT_PROP, int)

    @felt.setter
    def felt(self, v: int | None) -> None:
        self._set_property(FELT_PROP, _validate_felt(v), pop_if_none=True)

    @property
    def status(self) -> StatusType | None:
        """Review status of the event metadata."""
        return cast("StatusType | None", self._get_property(STATUS_PROP, str))

    @status.setter
    def status(self, v: StatusType | None) -> None:
        self._set_property(STATUS_PROP, v, pop_if_none=True)

    @property
    def tsunami(self) -> bool | None:
        """Whether the event was associated with a tsunami."""
        return self._get_property(TSUNAMI_PROP, bool)

    @tsunami.setter
    def tsunami(self, v: bool | None) -> None:
        self._set_property(TSUNAMI_PROP, v, pop_if_none=True)

    @property
    def depth(self) -> float | None:
        """Depth of the event in kilometers."""
        return self._get_property(DEPTH_PROP, float)

    @depth.setter
    def depth(self, v: float | None) -> None:
        self._set_property(DEPTH_PROP, None if v is None else float(v), pop_if_none=True)

    @property
    def sources(self) -> list[EarthquakeSource] | None:
        """Provider-specific source records associated with this event."""
        return cast(
            "list[EarthquakeSource] | None",
            self._get_property(SOURCES_PROP, list),
        )

    @sources.setter
    def sources(self, v: list[EarthquakeSource] | None) -> None:
        self._set_property(SOURCES_PROP, _validate_sources(v), pop_if_none=True)


class ItemEarthquakeExtension(EarthquakeExtension[pystac.Item]):
    """Concrete earthquake implementation for :class:`~pystac.Item` objects."""

    item: pystac.Item
    properties: dict[str, Any]

    def __init__(self, item: pystac.Item) -> None:
        self.item = item
        self.properties = item.properties

    def __repr__(self) -> str:
        return f"<ItemEarthquakeExtension Item id={self.item.id}>"


class AssetEarthquakeExtension(EarthquakeExtension[pystac.Asset]):
    """Concrete earthquake implementation for :class:`~pystac.Asset` objects."""

    asset_href: str
    properties: dict[str, Any]
    additional_read_properties: Iterable[dict[str, Any]] | None = None

    def __init__(self, asset: pystac.Asset) -> None:
        self.asset_href = asset.href
        self.properties = asset.extra_fields
        if asset.owner and isinstance(asset.owner, pystac.Item):
            self.additional_read_properties = [asset.owner.properties]

    def __repr__(self) -> str:
        return f"<AssetEarthquakeExtension Asset href={self.asset_href}>"


class ItemAssetsEarthquakeExtension(EarthquakeExtension[pystac.ItemAssetDefinition]):
    """Concrete earthquake implementation for item asset definitions."""

    asset_defn: pystac.ItemAssetDefinition
    properties: dict[str, Any]

    def __init__(self, item_asset: pystac.ItemAssetDefinition) -> None:
        self.asset_defn = item_asset
        self.properties = item_asset.properties


class EarthquakeExtensionHooks(ExtensionHooks):
    """Hook registration used when reading or migrating STAC objects."""

    schema_uri: str = SCHEMA_URI
    prev_extension_ids: ClassVar[set[str]] = {"earthquake", "eq"}
    stac_object_types: ClassVar[set[pystac.STACObjectType]] = {
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


EARTHQUAKE_EXTENSION_HOOKS: ExtensionHooks = EarthquakeExtensionHooks()
