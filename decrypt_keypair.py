#!/usr/bin/env python3
import json
import base58
import click
import getpass
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password, salt):
    """Derive encryption key from password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def decrypt_keypair(encrypted_data, password):
    """Decrypt a keypair using the provided password"""
    salt = base58.b58decode(encrypted_data['salt'])
    nonce = base58.b58decode(encrypted_data['nonce'])
    ciphertext = base58.b58decode(encrypted_data['ciphertext'])
    
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return base58.b58encode(plaintext).decode('utf-8')
    except Exception as e:
        click.echo(f"Error: Failed to decrypt (incorrect password?): {e}")
        return None

@click.command()
@click.argument('wallet_file', type=click.Path(exists=True))
@click.option('--password', help='Password used to encrypt the keypair')
def main(wallet_file, password):
    """Decrypt a Solana keypair from an encrypted wallet file."""
    # Load the wallet file
    with open(wallet_file, 'r') as f:
        wallet_data = json.load(f)
    
    if not wallet_data.get('encrypted', False):
        click.echo("This wallet file is not encrypted.")
        if 'secret' in wallet_data:
            click.echo(f"Secret key: {wallet_data['secret']}")
        return
    
    # Get password if not provided
    if not password:
        password = getpass.getpass("Enter password: ")
    
    # Decrypt
    secret_key = decrypt_keypair(wallet_data, password)
    if secret_key:
        click.echo(f"Address: {wallet_data['address']}")
        click.echo(f"Secret key: {secret_key}")
        click.echo("\nWARNING: Never share your secret key with anyone!")

if __name__ == '__main__':
    main() 