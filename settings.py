from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔑 Add your secret key here
SECRET_KEY = 'djshf87#@fdskjhfsd8f7sdf8@#kjhfd'

# Other settings…

INSTALLED_APPS = [
    # ...existing apps...
    'django.contrib.staticfiles',
    # ...existing apps...
]

TEMPLATES = [
    {
        # ...existing code...
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ...existing code...
                'django.template.context_processors.static',
            ],
        },
    },
]

# ...existing code...
