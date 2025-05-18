from django.shortcuts import render
from rest_framework import generics, status, viewsets
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
Comment, SubscriptionPlan, 
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
ChargingStationAnaliticsSerializer
)

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now

from django.http import JsonResponse
import geopy.distance


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny



#charging points views 
class ChargingPointListCreateView(generics.ListCreateAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination


    #search filter
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['location', 'name']
    pagination_class = PageNumberPagination


    @api_view(['GET'])
    def charging_points_list(request):
        #this will return list of all charging stations/points with their details
        stations = ChargingPoint.objects.all()
        serializer = ChargingPointSerializer(stations, many=True)
        return Response(serializer.data)
    

    #allowing to add a charging station
    @api_view(['POST'])
    def create_charging_station(request):
        serializer = ChargingPointSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #this will update a charging station
    @api_view(['PUT'])
    def update_charging_station(request, pk):
        try:
            station = ChargingPoint.objects.get(pk=pk)
        except ChargingPoint.DoesNotExist:
            return Response({"error": "Sorry!! Station Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChargingPointSerializer(station, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

    #this will delete a charging station
    @api_view(['DELETE'])
    def delete_charging_station(request, pk):
        try:
            station = ChargingPoint.objects.get(pk=pk)
        except ChargingPoint.DoesNotExist:
            return Response({"error": "Station Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        station.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    
    def delete(self, request, *args, **kwargs):
        confirmation = request.data.get('confirm', None)
        if confirmation != 'confirm':
            return Response({"error": "Please provide confirmation to delete all charging points."}, status=status.HTTP_400_BAD_REQUEST)
        
        ChargingPoint.objects.all().delete()
        return Response({"message": "All charging points have been deleted"}, status.HTTP_204_NO_CONTENT)
    



class ChargingPointDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingPoint.objects.all()
    serializer_class = ChargingPointSerializer
    pagination_class = PageNumberPagination

    @api_view(['GET', 'PUT', 'DELETE'])
    def charging_points_detail(request, id):

        try:
            chargingpoints = ChargingPoint.objects.get(pk=id)
        except ChargingPoint.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ChargingPointSerializer(chargingpoints)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = ChargingPointSerializer(chargingpoints, data= request.data)
            if serializer.is_valid():
                serializer.save

        elif request.method == 'DELETE':
            chargingpoints.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)





#charging session 
class ChargingSessionListCreateView(generics.ListCreateAPIView):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    pagination_class = PageNumberPagination


    @api_view(['GET'])
    def get_available_slots(request, station_id):
        try:
            station = ChargingPoint.objects.get(id=station_id)
            now_time = now()
            available_sessions = ChargingSession.objects.filter(station=station, start_time__gte=now_time, status='Scheduled')
            serializer = ChargingSessionSerializer(available_sessions, many=True)

            return Response(serializer.data)
        except ChargingPoint.DoesNotExist:
            return Response({"error": "Ohh No! Station Not Found"}, 
            status= status.HTTP_404_NOT_FOUND)


    #calculate cost of charging sessions 
    @api_view(['POST'])
    def book_charging_sessions(request):
        user = request.user
        station_id = request.data.get("station_id")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        try:
            station = ChargingPoint.objects.get(id=station_id)
            cost = calculate_cost(station, start_time, end_time)

            #checking if the slots are available
            overlapping_sessions = ChargingSession.objects.filter(station=station, start_time__lt=end_time, end_time__gt=start_time, status='Scheduled')

            if overlapping_sessions.exists():
                return Response({"error": "Time slot is running out."}, status=status.HTTP_400_BAD_REQUEST)

            session = ChargingSession.objects.create(
                user=user,
                station=station,
                start_time=start_time,
                end_time=end_time,
                cost=cost
            )

            serializer = ChargingSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ChargingPoint.DoesNotExist:
            return Response({"error": "Station Not Found"}, status=status.HTTP_404_NOT_FOUND)
        

    @api_view(['GET'])
    def list_charging_sessions(request):
        sessions = ChargingSession.objects.all()
        serializer = ChargingSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_charging_session(request):
        serializer = ChargingSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # this will update a charging session details
    @api_view(['PUT'])
    def update_charging_session(request, pk):
        try:
            session = ChargingSession.objects.get(pk=pk)
        except ChargingSession.DoesNotExist:
            return Response({"error": "Session Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChargingSessionSerializer(session, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #this will delete a charging session
    @api_view(['DELETE'])
    def delete_charging_session(request, pk):
        try:
            session = ChargingSession.objects.get(pk=pk)
        except ChargingSession.DoesNotExist:
            return Response({"error": "Session Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class ChargingSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChargingSession.objects.all()
    serializer_class = ChargingSessionSerializer
    pagination_class = PageNumberPagination


    @api_view(['DELETE'])
    def cancel_session(request, session_id):
        try:
            session = ChargingSession.objects.get(id=session_id, user=request.user)
            session.status = "Cancelled"
            session.save()
            return Response({"message": "Hey!! The Session Has Been Cancelled Successfully."}, status=status.HTTP_200_OK)

        except ChargingSession.DoesNotExist:
            return Response({"error": "Opps.. Unfortunately Session Not Found Or You Don't Have Permission To Cancel It."}, status=status.HTTP_404_NOT_FOUND)
        


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = PageNumberPagination

    pagination_class = PageNumberPagination

    @api_view(['POST'])
    def booking(request):
         #reserve a charging slot
        serializer = BookingSerializer()
        if request.method == 'POST':
            serializer = BookingSerializer(request.POST)

            if serializer.is_valid():
                serializer.save()

    @api_view(['GET'])
    def list_bookings(request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_booking(request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def update_booking(request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    def delete_booking(request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
     #this will delete all the bookings made
    def delete(self, request, *args, **kwargs):
        Booking.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = PageNumberPagination


    @api_view(['GET', 'PUT', 'DELETE'])
    def booking_detail(request, id):

        try:
            booking = Booking.objects.get(pk=id)
        except Booking.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = BookingSerializer(booking)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = BookingSerializer(booking, data= request.data)
            if serializer.is_valid():
                serializer.save
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        elif request.method == 'DELETE':
            booking.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        


class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    @api_view(['GET'])
    def list_profiles(request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
    
    


class PaymentMethodListCreateView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @api_view(['GET'])
    def list_payment_methods(request):
        payment_methods = PaymentMethod.objects.all()
        serializer= PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data)
    

class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @api_view(['GET'])
    def payment_history(request):
        payment = Payment.objects.all()
        serializer= PaymentMethodSerializer(payment, many=True)
        return Response(serializer.data)



class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    pagination_class = PageNumberPagination

    @api_view(['GET'])
    def list_ratings(request):
        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_rating(request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def update_rating(request, pk):
        try:
            rating = Rating.objects.get(pk=pk)
        except Rating.DoesNotExist:
            return Response({"error": "Rating Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RatingSerializer(rating, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    def delete_rating(request, pk):
        try:
            rating = Rating.objects.get(pk=pk)
        except Rating.DoesNotExist:
            return Response({"error": "Rating Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class IssueReportListCreateView(generics.ListCreateAPIView):
    queryset = IssueReport.objects.all()
    serializer_class = IssueReportSerializer
    pagination_class = PageNumberPagination


    @api_view(['GET'])
    def list_issue_reports(request):
        issue_reports = IssueReport.objects.all()
        serializer = IssueReportSerializer(issue_reports, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_issue_report(request):
        serializer = IssueReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def update_issue_report(request, pk):
        try:
            issue_report = IssueReport.objects.get(pk=pk)
        except IssueReport.DoesNotExist:
            return Response({"error": "Issue Report Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IssueReportSerializer(issue_report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    def delete_issue_report(request, pk):
        try:
            issue_report = IssueReport.objects.get(pk=pk)
        except IssueReport.DoesNotExist:
            return Response({"error": "Issue Report Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        issue_report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination


    @api_view(['GET'])
    def list_comments(request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_comment(request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def update_comment(request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['DELETE'])
    def delete_comment(request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#Subcribtion plan views
class SubscriptionPlanListCreateView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    #this will return list of all subscription plans with their details
    @api_view(['GET'])
    def list_subscription_plans(request):
        subscription_plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(subscription_plans, many=True)
        return Response(serializer.data)

    #this will allow to create a subscription plan
    @api_view(['POST'])
    def create_subscription_plan(request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #update a subscription plan
    @api_view(['PUT'])
    def update_subscription_plan(request, pk):
        try:
            subscription_plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription Plan Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubscriptionPlanSerializer(subscription_plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #this will delete a subscription plan
    @api_view(['DELETE'])
    def delete_subscription_plan(request, pk):
        try:
            subscription_plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Subscription Plan Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        subscription_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    pagination_class = PageNumberPagination

    @api_view(['GET', 'PUT', 'DELETE'])
    def subscription_plan_detail(request, id):

        try:
            subscription_plan = SubscriptionPlan.objects.get(pk=id)
        except SubscriptionPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = SubscriptionPlanSerializer(subscription_plan)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = SubscriptionPlanSerializer(subscription_plan, data= request.data)
            if serializer.is_valid():
                serializer.save
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        elif request.method == 'DELETE':
            subscription_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionCreateListView(generics.ListCreateAPIView):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @api_view(['GET'])
    def list_user_subscriptions(request):
        user_subscriptions = UserSubscription.objects.filter(user=request.user)
        serializer = UserSubscriptionSerializer(user_subscriptions, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_user_subscription(request):
        serializer = UserSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ChargingStationAnaliticsCreateListView(generics.ListCreateAPIView):
    queryset = ChargingStationAnalitics.objects.all()
    serializer_class = ChargingStationAnaliticsSerializer
    permission_classes = [IsAuthenticated]

    @api_view(['GET'])
    def list_station_analytics(request):
        analytics = ChargingStationAnalitics.objects.all()
        serializer = ChargingStationAnaliticsSerializer(analytics, many=True)
        return Response(serializer.data)

    @api_view(['POST'])
    def create_station_analytics(request):
        serializer = ChargingStationAnaliticsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ChargingStationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analytics = ChargingStationAnalitics.objects.all()
        serializer = ChargingStationAnaliticsSerializer(analytics, many=True)
        return Response(serializer.data)




