from app import create_app
from app.config import Config
import sys

app = create_app(use_ai=False)
