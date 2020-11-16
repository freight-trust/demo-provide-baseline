import os
from .config import Config
from .app import create_app


app = create_app(Config())

app.run(host='0.0.0.0', port=os.environ['PORT'])
