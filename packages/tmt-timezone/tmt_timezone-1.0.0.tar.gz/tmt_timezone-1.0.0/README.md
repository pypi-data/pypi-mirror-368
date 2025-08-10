# TMT - Timezone Tool

A simple CLI tool to get the current time in different timezones.

## Installation

```bash
pip install tmt-timezone
```

## Usage

```bash
tmt -p <timezone>
```

### Supported Timezones

- `PST` - Pacific Standard Time (US/Pacific)
- `EST` - Eastern Standard Time (US/Eastern)
- `BST` - British Summer Time (Europe/London)
- `CET` - Central European Time (Europe/Berlin)
- `WAT` - West Africa Time (Africa/Lagos)

### Examples

```bash
# Get current time in PST
tmt -p PST

# Get current time in EST
tmt -p EST

# Get current time in BST
tmt -p BST
```

## Output Format

```
PST: 2024-08-09 14:30:45 PDT
```

## Development

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install in development mode: `pip install -e .`

### Testing
```bash
python -m tmt.cli -p PST
```

### Building
```bash
python -m build
```

### Deployment
See `setup.md` for deployment instructions.

## License

MIT