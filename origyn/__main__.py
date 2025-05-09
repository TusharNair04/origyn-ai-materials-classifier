"""Main entry point for the Origyn application."""

import sys
from .cli import main
import os
import logging

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)

if __name__ == "__main__":
    sys.exit(main())