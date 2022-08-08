from django.db.models import Max, Min
from rest_framework import serializers

from company.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """Список компаний."""

    class Meta:
        model = Company
        fields = ["id", "name", "created_at", "last_price"]
        depth = 1
        read_only_fields = ["id", "created_at", "last_price"]


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Детальная информация по компании."""

    prices = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "created_at",
            "prices",
            "max_price",
            "min_price",
        ]

    @staticmethod
    def get_prices(obj: Company):
        return obj.price.values("id", "created_at", "value").order_by(
            "-created_at"
        )[:10]

    @staticmethod
    def get_max_price(obj: Company):
        return obj.price.aggregate(Max("value"))

    @staticmethod
    def get_min_price(obj: Company):
        return obj.price.aggregate(Min("value"))
