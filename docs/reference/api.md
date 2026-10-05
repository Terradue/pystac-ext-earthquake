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

# Python API

Import the extension from `pystac.extensions.earthquake`. Prefer `EarthquakeExtension.ext()` over constructing the concrete wrappers directly.

::: pystac.extensions.earthquake
    options:
      members:
        - EarthquakeExtension
        - EarthquakeSource
        - MagnitudeType
        - StatusType
        - ItemEarthquakeExtension
        - AssetEarthquakeExtension
        - ItemAssetsEarthquakeExtension
        - EarthquakeExtensionHooks
        - EARTHQUAKE_EXTENSION_HOOKS
        - SCHEMA_URI
      inherited_members: false
      show_root_heading: true
      show_signature_annotations: true
