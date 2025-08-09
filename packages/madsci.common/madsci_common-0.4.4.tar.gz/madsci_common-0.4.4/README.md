# MADSci Common

Common types, validators, serializers, utilities, and other flotsam and jetsam used across the MADSci toolkit.

## Installation

The MADSci common components are available via [the Python Package Index](https://pypi.org/project/madsci.common/), and can be installed via:

```bash
pip install madsci.common
```

This python package is also included as part of the [madsci Docker image](https://github.com/orgs/AD-SDL/packages/container/package/madsci).

## MADSci Types

The MADSci toolkit uses a variety of "types", implemented as [Pydantic Data Models](https://docs.pydantic.dev/latest/). These data models allow us to easily create, validate, serialize, and de-serialize data structures used throughout the distributed systems. They can easily be serialized to JSON when being sent between system components over REST or stored in JSON-friendly databases like MongoDB or Redis, or to YAML for human-readable and editable definition files.

You can import these types from `madsci.common.types`, where they are organized by subsystem.

## Settings

MADSci uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) to configure many of it's subsystems. This allows users to configure managers, clients, nodes, and other MADSci components using command line arguments, environment variables, settings files in various formats (`.env`, `.toml`, `.yaml`, `.json`), and secrets files.

![Settings Precedence](./assets/drawio/config_precedence.drawio.svg)

Detailed documentation for what configuration can be set is included in the [Configuration.md](../../Configuration.md), and an example [.env](../../.env.example) is included in the root of the MADSci repository.

In general, each subsystem supports configuration via both a generic file (`.env`, `settings.yaml`, etc), and a subsystem-specific file (`event_client.env`, `event_client.yaml`, etc). In such cases, the subsystem specific version takes precedence over the generic version.
