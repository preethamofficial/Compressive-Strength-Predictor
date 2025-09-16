# settings.py

# ...existing code...

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