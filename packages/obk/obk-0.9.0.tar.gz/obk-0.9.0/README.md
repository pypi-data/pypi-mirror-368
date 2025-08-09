# obk

> ⚠️ This project is in early development (pre-release/alpha).
> APIs and behavior will change rapidly as features are added.

OBK is a programmable system for documenting, validating, and querying project
knowledge via structured prompts validated with XSD and stored for later
analysis.

## Installation

```bash
pip install obk
```

## Quickstart

```bash
obk hello-world
obk divide 4 2
obk trace-id
```

## Features

* `hello-world` prints a greeting
* `divide` divides numbers with zero-checking
* `greet` greets by name; `fail` triggers a fatal error
* `validate-*` validates prompt files; `harmonize-*` normalizes them
* `trace-id` generates unique trace IDs

## Usage

For help on any command:

```bash
obk --help
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

