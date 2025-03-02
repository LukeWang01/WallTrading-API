import argparse
import sys
import schwab
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

def load_secrets():
    """Dynamically load secrets from _secrete.py"""
    secrete_path = Path("./env/_secrete.py")
    try:
        spec = spec_from_file_location("secrets", secrete_path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.Schwab_app_key, module.Schwab_secret
    except Exception as e:
        raise ImportError(f"Failed to load secret file: {e}")

def main(app_key, secret, callback_url, token_path):
    try:
        schwab.auth.client_from_manual_flow(app_key, secret, callback_url, token_path)
        print("\nToken successfully generated and written to file!")
        return 0
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return 1

if __name__ == '__main__':
    try:
        default_app_key, default_secret = load_secrets()
    except Exception as e:
        default_app_key = None
        default_secret = None
        print(f"Warning: {e}")

    parser = argparse.ArgumentParser(
        description='Fetch a new token and write it to a file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    required = parser.add_argument_group('required arguments')
    required.add_argument('--app_key', 
                         default=default_app_key,
                         required=default_app_key is None,
                         help='Schwab App Key (default loads from ./env/_secrete.py)')
    required.add_argument('--secret',
                         default=default_secret,
                         required=default_secret is None,
                         help='Schwab Secret (default loads from ./env/_secrete.py)')
    required.add_argument('--callback_url', 
                         default="https://127.0.0.1:8182",
                         help='Callback URL')
    required.add_argument('--token_file', 
                         default="./env/_schwab_token.json",
                         help='Path to save token file')

    args = parser.parse_args()
    
    if not args.app_key or not args.secret:
        parser.error("API key and app secret must be provided (via defaults or command line)")

    sys.exit(main(args.app_key, args.secret, args.callback_url, args.token_file))