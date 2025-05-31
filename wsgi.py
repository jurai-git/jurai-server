from app import create_app
import os

use_ai = os.getenv("USE_AI", "false").lower() == "true"
app = create_app(use_ai=use_ai)
