from logging.config import dictConfig 
from flask.logging import default_handler, current_app
import os

log_file_path = os.path.join('logs', 'logfile.log')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'file': {  # Change 'wsgi' to 'file' here
        'class': 'logging.FileHandler',
        'filename': log_file_path,
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['file']  # Use 'file' handler for the root logger
    }
})

app = current_app._get_current_object()
app.logger.removeHandler(default_handler)
