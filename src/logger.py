from logging.config import dictConfig
from flask.logging import default_handler, current_app
import os

log_file_path = os.path.join('logs', 'logfile.log')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': log_file_path,
            'formatter': 'default',
        },
        'console': {
            'class': 'logging.StreamHandler',  # Add a StreamHandler for console logging
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console'],  # Include the 'console' handler for console logging
    },
})

app = current_app._get_current_object()
app.logger.removeHandler(default_handler)
