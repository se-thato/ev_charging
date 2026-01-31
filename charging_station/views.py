from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import F, Sum
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError  
from rest_framework.views import APIView
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
    Post,
)

from .serializers import (
    ChargingPointSerializer,
    ChargingSessionSerializer,
    BookingSerializer,
    PostSerializer,
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

    # This will allow ordering by fields and distance if provided
    @action(detail=False, methods=["delete"], url_path="", url_name="bulk-delete")
    def bulk_delete(self, request, *args, **kwargs):
        confirmation = request.data.get("confirm")
        if confirmation != "confirm":
            return Response(
                {"error": "Please provide confirmation to delete all charging points."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Delete all charging points
        ChargingPoint.objects.all().delete()
        return Response({"message": "All charging points have been deleted"}, status=status.HTTP_204_NO_CONTENT)
    

    def get_queryset(self):
        return ChargingPoint.objects.filter(is_verified=True)  # Only show verified
    
    # This function will set the owner to the logged in user when creating a charging point
    # Only the owner can update or delete their charging points
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, is_verified=False)  # the owner will add and the admin verify

    # This custom action will return nearby charging points based on lat/lng and radius
    @action(detail=False, methods=["get"])
    def nearby(self, request):
        """Return stations within X km of given lat/lng"""
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
            radius_km = float(request.query_params.get("radius", 5))
        except (TypeError, ValueError):
            return Response({"error": "lat, lng, and optional radius are required."}, status=400)

        # Calculate distance using Haversine formula
        qs = ChargingPoint.objects.filter(is_verified=True).annotate(
            distance=6371 * ACos(
                Cos(Radians(lat)) *  # the radius of the Earth in kilometers
                Cos(Radians(F('latitude'))) * # the latitude of the charging point, converted to radians
                Cos(Radians(F('longitude')) - Radians(lng)) +  # the longitude of the charging point, converted to radians
                Sin(Radians(lat)) * # the latitude of the user, converted to radians
                Sin(Radians(F('latitude')))
            )
        ).filter(distance__lte=radius_km).order_by("distance")


        serializer = self.get_serializer(qs, many=True)  # Serialize the queryset
        return Response(serializer.data)




class ChargingSessionViewSet(viewsets.ModelViewSet):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["start_time", "end_time", "status"]

    #this method calculates the duration of the session
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            if self.end_time < self.start_time:
                raise ValidationError("Opps!! end time cannot be before start time.")
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "status", "booking_date"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        station = serializer.validated_data['station']

        # This function will check if the station is bookable before allowing booking
        if station.status != 'bookable':
            raise PermissionDenied(
                "This charging station is not available for booking."
            )

        booking = serializer.save(user=request.user) # Save the booking with the logged-in user

        return Response(BookingSerializer(booking).data,status=status.HTTP_201_CREATED) # Return the created booking details




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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = serializer.save(user=request.user)

        # So this will calculate the platform commission and station earnings
        if payment.charging_session:
            station = payment.charging_session.station
            commission_rate = station.commission_rate

            commission = (commission_rate / 100) * payment.amount # calculate commission
            payment.platform_commission = commission
            payment.station_earnings = payment.amount - commission
            payment.save()

        # Return the created payment with details, including commission info and earnings, So that the user can see what they paid for
        headers = self.get_success_headers(serializer.data)
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


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


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ["created_at", "title"]


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


#This view will provide dashboard data for station owners
class StationOwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        stations = ChargingPoint.objects.filter(owner=user)
        bookings = Booking.objects.filter(station__in=stations,status='completed') #This is to get only completed bookings
        #This will get all payments related to the bookings
        payments = Payment.objects.filter(booking__in=bookings)

        #Then calculate the total earnings, total bookings, and total stations
        return Response({
            "total_stations": stations.count(),
            "total_bookings": bookings.count(),
            "total_earnings": payments.aggregate(
                total=Sum('station_earnings')
            )['total'] or 0
        })
