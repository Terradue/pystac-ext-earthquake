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

# Earthquake PySTAC extension

`pystac-ext-earthquake` reads and writes earthquake metadata on PySTAC objects using the `eq:` prefix. Import the API from `pystac.extensions.earthquake`.

The implementation uses the [Earthquake extension v1.0.0 identifier](https://stac-extensions.github.io/earthquake/v1.0.0/schema.json). The [upstream specification](https://github.com/stac-extensions/earthquake) currently has Proposal maturity. The Python distribution version is independent of the specification version.

## Start here

```bash
pip install pystac-ext-earthquake
```

- [Create an earthquake Item](tutorials/first-steps.md) with a complete Python example.
- [Work with earthquake fields](how-to/use-extension.md), assets, and source links.
- [Look up fields](reference/fields.md) and the [Python API](reference/api.md).
- [Understand validation and scope](explanation/architecture.md) before exporting data.

This is a Python library; it does not provide a command-line entry point.
