from app import create_app
from app.config import Config
import sys

if __name__ == "__main__":
    use_ai = True
    if 'no_ai' in sys.argv:
        use_ai = False

    app = create_app(use_ai=use_ai)
    app.run(threaded=True)

