from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import F, Sum
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.utils import timezone

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
    StationOwnerProfile,
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
    StationOwnerProfileSerializer,
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
    search_fields = ["name", "location", "owner__username"]
    ordering_fields = ["created_at", "name", "location", "price_per_hour", "charging_speed_kw"]


    def get_queryset(self):
        if self.request.user.is_staff:
            return ChargingPoint.objects.all()
        return ChargingPoint.objects.filter(is_verified=True, is_active=True)

    def perform_create(self, serializer):
    # this method will set the owner to the logged in user when creating a charging point
        serializer.save(
            owner=self.request.user,
            is_verified=False,
            status='claimed',
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        #Only the station owner or an admin can update a station.
        station = self.get_object()
        if station.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only update your own stations.")
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        #only the admin or station owner who can delete a station, but instead of actually deleting it, we will just mark it as inactive so we can keep the data for analytics and auditing purposes
        if instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can only delete your own stations.")
        instance.is_active = False
        instance.save()

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius_km = float(request.query_params.get('radius', 5))
        except (TypeError, ValueError):
            return Response({'error': 'lat and lng are required numeric values.'},status=status.HTTP_400_BAD_REQUEST)

        # Calculate distance using Haversine formula and filter stations within the specified radius
        qs = ChargingPoint.objects.filter(
            is_verified=True,
            is_active=True
        ).annotate(
            distance=6371 * ACos(
                Cos(Radians(lat)) *
                Cos(Radians(F('latitude'))) *
                Cos(Radians(F('longitude')) - Radians(lng)) +
                Sin(Radians(lat)) *
                Sin(Radians(F('latitude')))
            )
        ).filter(distance__lte=radius_km).order_by('distance')

        # so this will allow users to filter nearby stations by connector type, for example: ?connector=CCS
        connector = request.query_params.get('connector')
        if connector:
            qs = qs.filter(connector_types__icontains=connector)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("Only admins can perform bulk delete.")

        if request.data.get('confirm') != 'confirm':
            return Response(
                {'error': 'Send {"confirm": "confirm"} in the request body to proceed.'},
                status=status.HTTP_400_BAD_REQUEST)
        
        ChargingPoint.objects.all().delete()
        return Response({'message': 'All charging points deleted.'},status=status.HTTP_204_NO_CONTENT)


    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        station = self.get_object()
        date_str = request.query_params.get('date')

        if not date_str:
            return Response(
                {'error': 'Provide a date using ?date=YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all confirmed/pending bookings for this station on that date
        bookings = Booking.objects.filter(
            station=station,
            booking_date=date_str,
            status__in=['confirmed', 'pending']
        ).values('start_time', 'end_time')

        return Response({
            'station':       station.name,
            'date':          date_str,
            'booked_slots':  list(bookings),
            'available_bays': station.available_slots,
        })

    
  

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

def get_queryset(self):
    
    user = self.request.user
    if user.is_staff:
        return Booking.objects.all()
    if hasattr(user, 'owner_profile'):
        # Owner sees their own bookings + bookings at their stations
        return Booking.objects.filter(
            station__owner=user
        ) | Booking.objects.filter(user=user)
    return Booking.objects.filter(user=user)

def create(self, request, *args, **kwargs):
    #this method will handle the booking creation process, including validation and commission calculation
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    station = serializer.validated_data['station']

    # station must be bookable
    if station.status != 'bookable':
        raise PermissionDenied("This charging station is not available for booking.")
    

    # check for conflicting bookings on the same slot
    start_time = serializer.validated_data['start_time']
    end_time   = serializer.validated_data.get('end_time')

    if end_time:
        conflict = Booking.objects.filter(
            station=station,
            status__in=['confirmed', 'pending'],
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if conflict:
            return Response(
                {'error': 'This time slot is already booked. Please choose another time.'},
                status=status.HTTP_409_CONFLICT
            )

    #calculating platform commission and owner earnings
    amount_paid = serializer.validated_data.get('amount_paid', 0) or 0
    commission_rate    = station.commission_rate or 10
    platform_commission = round((commission_rate / 100) * float(amount_paid), 2) # the platform commission is calculated as a percentage of the amount paid, rounded to 2 decimal places
    owner_earnings      = round(float(amount_paid) - platform_commission, 2)

    # saving the booking
    booking = serializer.save(
        user=request.user,
        created_by=request.user,
        platform_commission=platform_commission,
        owner_earnings=owner_earnings,
    )

    # Update owner's pending payout balance
    if hasattr(station.owner, 'owner_profile'):
        profile = station.owner.owner_profile
        profile.pending_payout  = float(profile.pending_payout) + owner_earnings
        profile.total_earnings  = float(profile.total_earnings) + owner_earnings
        profile.save()

    #will return the created booking with calculated commission and earnings details,so the user can see what they paid for and how much the owner earns
    return Response(BookingSerializer(booking).data,status=status.HTTP_201_CREATED)

#cancelling the booking
@action(detail=True, methods=['post'])
def cancel(self, request, pk=None):
    booking = self.get_object()

    if booking.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only cancel your own bookings.")

    if booking.status in ['completed', 'cancelled']:
        return Response(
            {'error': f'Cannot cancel a booking that is already {booking.status}.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = 'cancelled'
    booking.updated_by = request.user
    booking.save()

    return Response({'message': 'Booking cancelled successfully.'})





class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "username", "email"]


def get_queryset(self):
    if self.request.user.is_staff:
        return Profile.objects.all()
    return Profile.objects.filter(user=self.request.user)  # Regular users can only see their own profile



class StationOwnerProfileViewSet(viewsets.ModelViewSet):
    queryset = StationOwnerProfile.objects.all()
    serializer_class = StationOwnerProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['business_name', 'user__username', 'user__email']
    ordering_fields = ['created_at', 'listing_tier', 'pending_payout']

    def get_queryset(self):
        #ownwers can only see their own profile, while admins can see all for management purposes
        if self.request.user.is_staff:
            return StationOwnerProfile.objects.all()
        return StationOwnerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Registers the logged in user as a station owner.
        Creates a StationOwnerProfile linked to their account.
        After registration, status is 'unverified' they must
        submit documents and wait for admin approval before
        they can list stations or receive payouts.
        """
        # Prevent duplicate registrations
        if hasattr(request.user, 'owner_profile'):
            return Response(
                {'error': 'You are already registered as a station owner.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user,verification_status='unverified')

        return Response(serializer.data,status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'])
    def submit_banking(self, request):
        """
        Owner submits their banking details for payouts.
        Records the submission timestamp and IP address
        for the security audit trail.
        After submission, banking_verified stays False until
        an admin manually confirms the details are correct.
        """
        owner_profile = get_owner_profile(request.user)

        # Only update banking related fields not the whole profile
        banking_fields = [
            'bank_name', 'account_holder', 'account_number',
            'branch_code', 'account_type'
        ]


        for field in banking_fields:
            value = request.data.get(field)
            if value:
                setattr(owner_profile, field, value)


        # Record audit info
        owner_profile.banking_submitted_at = timezone.now()
        owner_profile.banking_details_updated_at = timezone.now()
        owner_profile.banking_details_updated_by_ip = request.META.get('REMOTE_ADDR')
        owner_profile.save()

        return Response({
            'message':          'Banking details submitted. Pending admin verification.',
            'account_last_four': owner_profile.account_last_four,
            'bank_name':         owner_profile.bank_name,
            'banking_verified':  owner_profile.banking_verified,
        })




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
