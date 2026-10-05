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

# Scope, architecture, and validation

## Package structure

The distribution is named `pystac-ext-earthquake`, while the import path is `pystac.extensions.earthquake`. PySTAC extends its package search path to support separately installed extensions. This package's wheel preserves that namespace and excludes the shared `pystac.extensions` initializer owned by PySTAC.

`EarthquakeExtension.ext()` selects a wrapper for an Item, Asset, or ItemAssetDefinition. These wrappers write into the wrapped object's dictionaries, so serialization uses PySTAC's normal `to_dict()` method. They do not fetch or convert earthquake feeds.

## Specification scope

The [upstream specification](https://github.com/stac-extensions/earthquake) covers Items and Collections, including asset fields and Collection summaries. The current Python API has no direct Collection wrapper or summary helper. Use PySTAC's Collection APIs for those structures.

The upstream [catalog mappings](https://github.com/stac-extensions/earthquake#mappings-with-existing-catalogs) describe how USGS and EMSC data relate to STAC. Feed conversion, timestamp conversion, place keywords, and related links remain caller responsibilities.

## Validation boundaries

Setter checks catch out-of-range magnitudes, negative felt counts, empty source lists, missing source keys, and invalid source strings. Type annotations guide callers but do not enforce every JSON type or enum at runtime. Reading an existing document does not revalidate its properties.

`apply()` mutates fields sequentially. If a later setter raises `ValueError`, earlier assignments remain. It also clears optional fields whose values are omitted. Validate inputs before applying them if your application requires an all-or-nothing update.

For full STAC and extension validation, use PySTAC's JSON Schema validation support (install `pystac[validation]`) and call `item.validate()`. Validation may retrieve remote schemas, so the referenced schema URLs must be accessible or supplied through an application-configured validator. Neither `apply()` nor `to_dict()` performs that validation.

Schema validation and specification prose are not interchangeable: see the [documented required-field differences](../reference/fields.md#defaults-and-required-fields).

## Migration hooks

`EARTHQUAKE_EXTENSION_HOOKS` declares the current schema identifier, legacy identifiers `earthquake` and `eq`, and Item/Collection object types. The module exposes this hook object but does not automatically register it with PySTAC. Importing the module does not activate a feed converter or a migration workflow.
