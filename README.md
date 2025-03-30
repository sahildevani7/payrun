# Solana Vanity Address Generator

A command-line tool for generating Solana wallet addresses with custom patterns.

## Features

- Generate Solana addresses with specific prefixes, suffixes, or containing specific strings
- Fast and efficient address generation
- Secure key storage with optional password encryption
- Easy to use CLI interface

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/vanity-solana-generator.git
cd vanity-solana-generator
```

2. Run the setup script:

```bash
./setup.sh
```

This will create a virtual environment and install all the required dependencies.

> **Note:** This tool uses the `solders` package, which is the new Rust-based library for Solana that replaces some functionality from the older `solana-py` package.

## Usage

### Basic Usage

To generate a Solana address with a specific pattern:

```bash
./vanity_generator.py --prefix ABC
```

This will search for a Solana address starting with "ABC".

### More Options

```bash
# Generate address ending with "XYZ"
./vanity_generator.py --suffix XYZ

# Generate address containing "123" anywhere
./vanity_generator.py --contains 123

# Generate address starting with "sol" (case insensitive)
./vanity_generator.py --prefix sol --no-case-sensitive

# Combine multiple patterns
./vanity_generator.py --prefix A --suffix Z --contains 123

# Encrypt the generated keypair with a password
./vanity_generator.py --prefix ABC --password mySecurePassword

# Specify a custom output file
./vanity_generator.py --prefix ABC --output my_wallet.json

# Set maximum number of attempts
./vanity_generator.py --prefix ABC --max-attempts 1000000
```

### Full Command Reference

```
Options:
  --prefix TEXT           Desired prefix for the wallet address
  --suffix TEXT           Desired suffix for the wallet address
  --contains TEXT         String that should be contained in the address
  --case-sensitive / --no-case-sensitive
                          Whether the pattern matching is case sensitive
  --max-attempts INTEGER  Maximum number of attempts
  --password TEXT         Password to encrypt the keypair
  --output TEXT           Output file for the keypair
  --help                  Show this message and exit
```

## Decrypting Keypairs

To decrypt and view a previously generated keypair that was encrypted with a password:

```bash
./decrypt_keypair.py wallets/youraddress.json
```

You will be prompted to enter the password. Alternatively, you can provide the password directly:

```bash
./decrypt_keypair.py wallets/youraddress.json --password yourpassword
```


## Performance

The speed of address generation depends on your hardware. On most modern computers, you can expect:

- Simple patterns (1-2 characters): Found within seconds
- More complex patterns (3-4 specific characters): May take minutes to hours
- Very specific patterns (5+ characters): May take many hours or days

## License

MIT 