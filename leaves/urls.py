from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet

router = DefaultRouter()
router.register(r'leaves', LeaveRequestViewSet, basename='leaverequest')

urlpatterns = router.urls
