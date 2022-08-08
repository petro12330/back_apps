from rest_framework.routers import SimpleRouter

from company.views import CompanyViewSet


router = SimpleRouter()
router.register(r"company", CompanyViewSet, basename="companies")
urlpatterns = router.urls
