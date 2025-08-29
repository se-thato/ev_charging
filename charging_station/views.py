from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    ChargingPoint,
    ChargingSession,
    Booking,
    Profile,
    PaymentMethod,
    Payment,
    Rating,
    IssueReport,
    Comment,
    SubscriptionPlan,
    UserSubscription,
    ChargingStationAnalitics,
)

from .serializers import (
    ChargingPointSerializer,
    ChargingSessionSerializer,
    BookingSerializer,
    ProfileSerializer,
    PaymentMethodSerializer,
    PaymentSerializer,
    RatingSerializer,
    IssueReportSerializer,
    CommentSerializer,
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    ChargingStationAnaliticsSerializer,
)


# Pagination
class DefaultPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100



class ChargingPointViewSet(viewsets.ModelViewSet):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["location", "name"]

    # Map DELETE on the collection path to this action to preserve existing behavior.
    @action(detail=False, methods=["delete"], url_path="", url_name="bulk-delete")
    def bulk_delete(self, request, *args, **kwargs):
        confirmation = request.data.get("confirm")
        if confirmation != "confirm":
            return Response(
                {"error": "Please provide confirmation to delete all charging points."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Mimic original response (204 with a JSON body, even though 204 usually has no content)
        ChargingPoint.objects.all().delete()
        return Response({"message": "All charging points have been deleted"}, status=status.HTTP_204_NO_CONTENT)



class ChargingSessionViewSet(viewsets.ModelViewSet):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["start_time", "end_time", "status"]



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "status", "booking_date"]



class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email"]



class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "is_default"]



class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "amount", "status"]



class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "rating"]



class IssueReportViewSet(viewsets.ModelViewSet):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "resolved"]



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "upvotes", "downvotes"]



class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["price", "name", "created_at"]



class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["start_date", "end_date", "is_active"]



class ChargingStationAnaliticsViewSet(viewsets.ModelViewSet):
    queryset = ChargingStationAnalitics.objects.all()
    serializer_class = ChargingStationAnaliticsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["total_sessions", "total_revenue", "created_at"]
