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

# Work with earthquake metadata

These examples continue from the Item created in the [tutorial](../tutorials/first-steps.md).

## Update or remove one field

```python
earthquake = EarthquakeExtension.ext(item)
earthquake.depth = 9.2
earthquake.felt = None
assert "eq:felt" not in item.properties
```

`ext(item)` requires the extension to be declared already. Use `add_if_missing=True` when first attaching it. Assigning `None` removes a field, including fields that the specification describes as required.

`apply()` sets every supported field. Omitted optional arguments become `None` and remove existing values. Use property setters when you want to preserve other fields.

## Read and override asset fields

```python
asset = pystac.Asset(href="https://example.org/event.json", media_type="application/json")
item.add_asset("event", asset)
asset_earthquake = EarthquakeExtension.ext(asset)
assert asset_earthquake.magnitude == earthquake.magnitude
asset_earthquake.depth = 7.5
assert asset.extra_fields["eq:depth"] == 7.5
assert earthquake.depth == 9.2
```

Attach an asset to its owner before wrapping it. An Item asset reads missing fields from its owner's properties; writes affect the asset only. Removing an asset override exposes the Item value again. Collection assets have no equivalent fallback to Collection properties.

## Use Collection item asset definitions

For an existing `pystac.Collection` with item asset definitions, retrieve the definition from `collection.item_assets`, then call `EarthquakeExtension.ext(definition, add_if_missing=True)`. This declares the extension on the owning Collection and writes fields to the definition's `properties`.

The wrapper accepts Items, Assets, and ItemAssetDefinitions. It does not accept a Collection directly or provide a Collection summaries API.

## Add a source link

Use ordinary PySTAC links for the specification's source relation:

```python
item.add_link(
    pystac.Link(
        rel="source",
        target="https://example.org/events/event-001",
        media_type="text/html",
        extra_fields={"source": "example-network"},
    )
)
```

Keep the link's `source` aligned with a source record's `name`. Source links are not created by `apply()`. See the upstream [relation types](https://github.com/stac-extensions/earthquake#relation-types) for the convention.
