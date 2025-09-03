from app import create_app
from app.config import Config
import sys

use_ai = True

if __name__ == "__main__":
    if 'no_ai' in sys.argv:
        use_ai = False

app = create_app(use_ai=use_ai)
app.run(host='0.0.0.0', threaded=True, port=5001)

