# Core/src/project/__init__.py
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from project.celery import app as celery_app  # noqa