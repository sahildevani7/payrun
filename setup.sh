#!/bin/bash

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make the generator executable
chmod +x vanity_generator.py
chmod +x decrypt_keypair.py

# Test if the imports are working
echo ""
echo "Testing imports..."
python -c "from solders.keypair import Keypair; kp = Keypair(); kp.pubkey(); kp.to_bytes(); print('Import test successful!')" || echo "Import test failed. Please check your installation."

echo ""
echo "Setup complete! You can now use the Solana Vanity Address Generator."
echo ""
echo "To activate the environment and use the tool, run:"
echo "  source venv/bin/activate"
echo "  ./vanity_generator.py --help"
echo ""
echo "Example usage:"
echo "  ./vanity_generator.py --prefix ABC --password mysecretpassword"
echo "" 