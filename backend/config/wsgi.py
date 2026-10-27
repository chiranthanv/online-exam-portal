import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

from .frontend import DIST

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = WhiteNoise(get_wsgi_application(), root=str(DIST), prefix="/", index_file=False)
