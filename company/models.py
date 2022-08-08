import uuid

from django.contrib.auth import get_user_model
from django.db import models

# from django.contrib.auth.models import User
from django.utils import timezone


User = get_user_model()


class Company(models.Model):
    """Список всех компаний занесенных в систему."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255, null=False, blank=False, unique=True
    )
    created_at = models.DateTimeField(
        verbose_name="Дата основания", default=timezone.now, auto_created=True
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата обновления", default=timezone.now, auto_created=True
    )
    last_price = models.DecimalField(
        max_digits=15, decimal_places=3, default=0
    )

    def __str__(self):
        return f"Company {self.name}"


class Price(models.Model):
    """Список цен для компаний."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="price",
        verbose_name="Компания",
    )
    value = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    created_at = models.DateTimeField(
        verbose_name="Актуальное время",
        default=timezone.now,
        auto_created=True,
    )


class PriceUser(models.Model):
    """Список подписок пользователя на цену компании."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    current_user = models.ForeignKey(
        User, related_name="user", blank=True, on_delete=models.DO_NOTHING
    )
    current_company = models.ForeignKey(
        Company, related_name="company", blank=True, on_delete=models.CASCADE
    )
