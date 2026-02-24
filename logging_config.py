
 # Zentrale Logging Konfig. für alle Microservices

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),                 # aktueller Zeitpunkt
            'level': record.levelname,                                 # Log Level wie info oder error
            'service': record.name,                                     # Name des Service - Logger
            'message': record.getMessage(),                             # Log Nachricht
            'module': record.module,                                    # Name des Moduls
            'function': record.funcName,                                # Name der Funktion
            'line': record.lineno,                                      # Zeilennummer
        }

                                                                          # Wenn ein Fehler aufgetreten, auch Exception speichern
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # bestehende Logger nicht ausschalten
    'formatters': {
        'json': {
            '()': 'logging_config.JSONFormatter',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/microservice.log',                                 # Speicherort
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {                                                             # spezieller Logger für Django
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {                                                     # Fehler von Requests loggen
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


