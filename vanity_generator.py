#!/usr/bin/env python3
import os
import time
import json
import base58
import click
import datetime
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from solders.keypair import Keypair

def generate_keypair():
    """Generate a new Solana keypair"""
    return Keypair()

def has_pattern(address, prefix=None, suffix=None, contains=None, case_sensitive=True):
    """Check if the address has the specified pattern"""
    addr_str = str(address)
    
    if not case_sensitive:
        addr_str = addr_str.lower()
        prefix = prefix.lower() if prefix else None
        suffix = suffix.lower() if suffix else None
        contains = contains.lower() if contains else None
    
    if prefix and not addr_str.startswith(prefix):
        return False
    if suffix and not addr_str.endswith(suffix):
        return False
    if contains and contains not in addr_str:
        return False
    
    return True

def derive_key(password, salt):
    """Derive encryption key from password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def encrypt_keypair(keypair, password):
    """Encrypt keypair using password"""
    salt = os.urandom(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    
    # Convert keypair to bytes
    keypair_bytes = keypair.to_bytes()
    
    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, keypair_bytes, None)
    
    return {
        'salt': base58.b58encode(salt).decode('utf-8'),
        'nonce': base58.b58encode(nonce).decode('utf-8'),
        'ciphertext': base58.b58encode(ciphertext).decode('utf-8')
    }

def save_keypair(keypair, filename=None, password=None):
    """Save keypair securely"""
    keypair_data = {
        'address': str(keypair.pubkey()),
        'created_at': datetime.datetime.now().isoformat(),
    }
    
    if password:
        # Encrypted storage
        keypair_data.update(encrypt_keypair(keypair, password))
        keypair_data['encrypted'] = True
    else:
        # WARNING: Storing unencrypted
        keypair_data['secret'] = base58.b58encode(keypair.to_bytes()).decode('utf-8')
        keypair_data['encrypted'] = False
    
    if not filename:
        # Create a wallet directory if it doesn't exist
        wallet_dir = Path('wallets')
        wallet_dir.mkdir(exist_ok=True)
        
        # Use address as filename
        filename = wallet_dir / f"{str(keypair.pubkey())}.json"
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(keypair_data, f, indent=2)
    
    return str(filename)

@click.command()
@click.option('--prefix', help='Desired prefix for the wallet address')
@click.option('--suffix', help='Desired suffix for the wallet address')
@click.option('--contains', help='String that should be contained in the address')
@click.option('--case-sensitive/--no-case-sensitive', default=True, 
              help='Whether the pattern matching is case sensitive')
@click.option('--max-attempts', default=100000, help='Maximum number of attempts')
@click.option('--password', help='Password to encrypt the keypair')
@click.option('--output', help='Output file for the keypair')
def generate_vanity_address(prefix, suffix, contains, case_sensitive, max_attempts, password, output):
    """Generate a Solana wallet address with specific vanity patterns."""
    if not any([prefix, suffix, contains]):
        click.echo("Error: You must specify at least one of --prefix, --suffix, or --contains")
        return
    
    click.echo(f"Searching for a Solana address with the following criteria:")
    if prefix:
        click.echo(f"- Prefix: {prefix}")
    if suffix:
        click.echo(f"- Suffix: {suffix}")
    if contains:
        click.echo(f"- Contains: {contains}")
    click.echo(f"- Case sensitive: {case_sensitive}")
    
    click.echo("Generating. This may take a while...")
    start_time = time.time()
    attempts = 0
    
    try:
        while attempts < max_attempts:
            kp = generate_keypair()
            address = str(kp.pubkey())
            attempts += 1
            
            if attempts % 1000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed
                click.echo(f"Tried {attempts} addresses ({rate:.2f}/s)...")
            
            if has_pattern(address, prefix, suffix, contains, case_sensitive):
                elapsed = time.time() - start_time
                click.echo(f"\nFound matching address after {attempts} attempts ({elapsed:.2f} seconds):")
                click.echo(f"Address: {address}")
                
                filename = save_keypair(kp, output, password)
                
                click.echo(f"\nKeypair {'securely encrypted and ' if password else ''}saved to: {filename}")
                if not password:
                    click.echo("\nWARNING: The keypair was saved without encryption!")
                    click.echo("Anyone with access to the file can access your funds.")
                
                return
        
        # If we reach here, max attempts exceeded
        click.echo(f"Maximum attempts ({max_attempts}) reached without finding a matching address.")
        
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        click.echo(f"\nSearch interrupted after {attempts} attempts ({elapsed:.2f} seconds)")

if __name__ == '__main__':
    generate_vanity_address() 