# Timechecker

A fast, clean CLI tool for checking current time in different timezones.

## Installation

### From PyPI
```bash
pip install timechecker
```

### From Source
```bash
git clone https://github.com/timechecker/timechecker.git
cd timechecker
pip install -e .
```

## Usage

### Basic Usage
```bash
# Get current time in PST
tmt -p PST

# Get current time in EST
tmt -p EST

# Get current time in BST
tmt -p BST

# Get current time in WAT
tmt -p WAT

# Get current time in CET
tmt -p CET
```

### Options
```bash
# List all supported timezones
tmt --list

# Enable verbose logging
tmt -p PST -v

# Show help
tmt -h
```

## Supported Timezones

- **PST** - Pacific Standard Time (US/Pacific)
- **EST** - Eastern Standard Time (US/Eastern) 
- **BST** - British Summer Time (Europe/London)
- **WAT** - West Africa Time (Africa/Lagos)
- **CET** - Central European Time (Europe/Berlin)

## Development

### Setup
```bash
# Clone repository
git clone https://github.com/timechecker/timechecker.git
cd timechecker

# Install dependencies
pip install -e .

# Run tests
python -m pytest tests/
```

### Build and Deploy
```bash
# Setup tokens in .env file (see setup.md)
cp .env.example .env
# Edit .env with your PyPI tokens

# Build and deploy
./cook.sh
```

## License

MIT License