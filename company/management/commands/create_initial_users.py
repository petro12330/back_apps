import logging

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


User = get_user_model()

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Registered initial user."

    def handle(self, *args, **kwargs):
        admin, create_admin = User.objects.get_or_create(
            username="admin",  is_superuser=True, is_active=True
        )
        admin.set_password("12345")
        admin.save()
        user, create_user = User.objects.get_or_create(username="some_user")
        user.set_password("12345")
        user.save()
        logger.info(f"Admin create {create_admin}. User create {create_user}")
