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

# Create an earthquake Item

Install the package using the [installation guide](../how-to/install.md). The following example uses synthetic event data.

## Create and extend an Item

```python
from datetime import datetime, timezone

import pystac
from pystac.extensions.earthquake import EarthquakeExtension

item = pystac.Item(
    id="example-earthquake",
    geometry={"type": "Point", "coordinates": [12.5, 42.0]},
    bbox=[12.5, 42.0, 12.5, 42.0],
    datetime=datetime(2026, 1, 1, tzinfo=timezone.utc),
    properties={"title": "Synthetic earthquake example"},
)
earthquake = EarthquakeExtension.ext(item, add_if_missing=True)
earthquake.apply(
    magnitude=6.1,
    magnitude_type="mww",
    sources=[{"name": "example-network", "code": "event-001"}],
    felt=12,
    status="reviewed",
    tsunami=False,
    depth=8.4,
)

assert earthquake.magnitude == 6.1
assert item.properties["eq:depth"] == 8.4
assert EarthquakeExtension.get_schema_uri() in item.stac_extensions
```

Coordinates use longitude, latitude order. `depth` is expressed in kilometers. `add_if_missing=True` adds the extension identifier to the Item. The wrapper mutates the Item in place.

## Serialize and read back

Continue in the same Python session:

```python
import json

payload = item.to_dict()
print(json.dumps(payload, indent=2))
restored_item = pystac.Item.from_dict(payload)
restored = EarthquakeExtension.ext(restored_item)
assert restored.sources == earthquake.sources
```

Serialization does not perform JSON Schema validation. See [validation boundaries](../explanation/architecture.md#validation-boundaries) for the distinction between setter checks and full document validation.

Use [individual setters](../how-to/use-extension.md) for partial updates: `apply()` also clears optional fields whose arguments are omitted.
