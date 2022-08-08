from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from company.models import Company
from company.serializers import CompanyDetailSerializer, CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_classes = {
        "list": CompanySerializer,
        "create": CompanySerializer,
        "update": CompanySerializer,
        "retrieve": CompanyDetailSerializer,
    }

    queryset = Company.objects.all()


    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    def retrieve(self, request, *args, **kwargs):
        instance = Company.objects.get(id=kwargs["pk"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
