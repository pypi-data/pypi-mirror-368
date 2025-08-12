import os
from pathlib import Path
from loguru import logger

# Try to load environment variables from .env file in the tests directory
try:
    from dotenv import load_dotenv
    # Get the path to the tests directory
    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    # Load from .env file in tests directory
    load_dotenv(os.path.join(TESTS_DIR, '.env'))
except ImportError:
    # python-dotenv is not installed, continue without it
    pass

# Define environment variables with defaults for tests
# Base project path (default uses current value for backward compatibility)
BASE_PATH = os.environ.get('MLGAME_BASE_PATH', os.path.join(os.path.dirname(__file__),"..",".."))
# Game and AI client paths 
GAMES_PATH = os.environ.get('MLGAME_GAMES_PATH', os.path.join(BASE_PATH, 'games'))
AI_CLIENTS_PATH = os.environ.get('MLGAME_AI_CLIENTS_PATH', os.path.join(BASE_PATH, 'ai_clients'))
OUTPUT_PATH = os.environ.get('MLGAME_OUTPUT_PATH', os.path.join(BASE_PATH, 'var'))

# Azure Storage URLs - using placeholder values as defaults
# These should be overridden with actual values in .env file or environment variables
AZURE_CONTAINER_URL = os.environ.get('MLGAME_AZURE_CONTAINER_URL', 
                                     'https://example.blob.core.windows.net/container?sv=xxxx&sig=xxxx')
AZURE_BLOB_URL = os.environ.get('MLGAME_AZURE_BLOB_URL',
                               'https://example.blob.core.windows.net/container/path?sv=xxxx&sig=xxxx')

# Helper function to create full paths
def get_path(*parts):
    return str(Path(os.path.join(*parts)))
