<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Earthquake fields

The table combines the [upstream field definitions](https://github.com/stac-extensions/earthquake#fields), [JSON Schema](https://github.com/stac-extensions/earthquake/blob/main/json-schema/schema.json), and current setter behavior. Values are stored under Item `properties`, asset extra fields, or item asset definition properties.

| STAC field | Python property | Meaning and current behavior |
| --- | --- | --- |
| `eq:magnitude` | `magnitude` | Event magnitude; the setter accepts values from −3 through 10 and stores a float. |
| `eq:magnitude_type` | `magnitude_type` | Magnitude scale; annotated with `MagnitudeType`. No default is inserted. |
| `eq:felt` | `felt` | Felt-report count; annotated as an integer, rejects negatives. |
| `eq:status` | `status` | Review state: `automatic`, `reviewed`, or `deleted`. |
| `eq:tsunami` | `tsunami` | Boolean flag; upstream describes large events in oceanic regions. It is not a confirmation of an observed tsunami. |
| `eq:sources` | `sources` | Ordered list of source records; the setter rejects an empty list. |
| `eq:depth` | `depth` | Event depth in kilometers, stored as a float. |

All getters can return `None` for an absent field, and all setters accept `None` to remove the stored value. `MagnitudeType` and `StatusType` provide static typing; their setters do not check membership at runtime.

## Source records

`EarthquakeSource` is the existing dictionary type used by the API. Each record must contain `name` and `code`; `catalog` is optional. The setter requires non-empty strings for all three when present. Preserve ordering: upstream treats the first record as preferred.

```python
from pystac.extensions.earthquake import EarthquakeSource

sources: list[EarthquakeSource] = [
    {"name": "example-network", "code": "event-001", "catalog": "USGS"},
]
```

The static dictionary type permits omitted keys, so the setter remains responsible for checking required keys. Catalog names are not restricted by the wrapper.

## Defaults and required fields

The upstream prose marks magnitude and sources as required and describes `mww` as the magnitude-type default. Pass these explicitly when creating an event. `apply()` requires magnitude and sources but does not supply `mww` automatically.

The current upstream schema's `fields` definition has no `required` array for magnitude or sources. This differs from its prose. The schema requires source-record `name` and `code` when a source record is present. The Python setter additionally rejects empty names and codes and negative felt counts, which that schema does not reject.

Consult [validation boundaries](../explanation/architecture.md#validation-boundaries) when checking exported documents.
