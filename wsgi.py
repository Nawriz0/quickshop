import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuickShop.settings')

app = get_wsgi_application()
app = WhiteNoise(app, root=os.path.join(os.path.dirname(__file__), 'media')) 