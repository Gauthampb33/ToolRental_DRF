
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from Rental.models import Tools, Rental, Complaint, Payment
from Rental.serializers import (
    UserSerializers,
    ToolsSerializer,
    RentalSerializer,
    RentalUpdateSerializer,
    ComplaintSerializer,
    ComplaintUpdateSerializer,
    PaymentSerializer
)

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        form_data = request.data
        serializer_instance = UserSerializers(data=form_data)

        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(
                {"Message": "User Created Successfully"},
                status=201
            )

        return Response(serializer_instance.errors, status=400)


class UserListView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer_instance = UserSerializers(users, many=True)

        return Response(serializer_instance.data, status=200)
    
class ToolsListCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tools = Tools.objects.filter(owner=request.user)
        serializer_instance = ToolsSerializer(tools, many=True)

        return Response(serializer_instance.data, status=200)

    def post(self, request):
        form_data = request.data
        serializer_instance = ToolsSerializer(data=form_data)

        if serializer_instance.is_valid():
            serializer_instance.save(owner=request.user)

            return Response(
                {"Message": "Tool Added Successfully"},
                status=201
            )

        return Response(serializer_instance.errors, status=400)


class ToolsRetrieveUpdateDeleteView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        tool = get_object_or_404(
            Tools, id=pk, owner=request.user
        )

        serializer_instance = ToolsSerializer(tool)

        return Response(serializer_instance.data, status=200)

    def put(self, request, pk):
        tool = get_object_or_404(
            Tools, id=pk, owner=request.user
        )

        form_data = request.data
        serializer_instance = ToolsSerializer(
            tool, data=form_data
        )

        if serializer_instance.is_valid():
            serializer_instance.save()

            return Response(
                {"Message": "Tool Updated Successfully"},
                status=200
            )

        return Response(serializer_instance.errors, status=400)

    def delete(self, request, pk):
        tool = get_object_or_404(
            Tools, id=pk, owner=request.user
        )

        if not tool.availability_status:
            return Response(
                {"Message": "Tool is Currently Rented"},
                status=400
            )

        if Rental.objects.filter(tool=tool).exists():
            return Response(
                {"Message": "Cannot Delete Tool With Rental History"},
                status=400
            )

        tool.delete()

        return Response(
            {"Message": "Tool Deleted Successfully"},
            status=200
        )

class RentalListCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rentals = Rental.objects.filter(user=request.user)

        serializer_instance = RentalSerializer(
            rentals, many=True
        )

        return Response(serializer_instance.data, status=200)

    def post(self, request):
        form_data = request.data

        serializer_instance = RentalSerializer(
            data=form_data,
            context={"request": request}
        )

        if serializer_instance.is_valid():
            serializer_instance.save(user=request.user)

            return Response(
                {"Message": "Tool Rented Successfully"},
                status=201
            )

        return Response(serializer_instance.errors, status=400)


class RentalRetrieveUpdateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        rental = get_object_or_404(
            Rental, id=pk, user=request.user
        )

        serializer_instance = RentalSerializer(rental)

        return Response(serializer_instance.data, status=200)

    def put(self, request, pk):
        rental = get_object_or_404(
            Rental, id=pk, user=request.user
        )

        form_data = request.data

        serializer_instance = RentalUpdateSerializer(
            rental, data=form_data
        )

        if serializer_instance.is_valid():
            serializer_instance.save()

            return Response(
                {"Message": "Rental Updated Successfully"},
                status=200
            )

        return Response(serializer_instance.errors, status=400)

class ComplaintListCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        complaints = Complaint.objects.filter(
            user=request.user
        )

        serializer_instance = ComplaintSerializer(
            complaints, many=True
        )

        return Response(serializer_instance.data, status=200)

    def post(self, request):
        form_data = request.data

        serializer_instance = ComplaintSerializer(
            data=form_data,
            context={"request": request}
        )

        if serializer_instance.is_valid():
            serializer_instance.save(user=request.user)

            return Response(
                {"Message": "Complaint Added Successfully"},
                status=201
            )

        return Response(serializer_instance.errors, status=400)


class ComplaintRetrieveUpdateDeleteView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        complaint = get_object_or_404(Complaint, id=pk)

        if (
            request.user != complaint.user
            and request.user != complaint.tool.owner
        ):
            return Response(
                {"Message": "Permission Denied"},
                status=403
            )

        serializer_instance = ComplaintSerializer(complaint)

        return Response(serializer_instance.data, status=200)

    def put(self, request, pk):
        complaint = get_object_or_404(
            Complaint, id=pk, user=request.user
        )

        form_data = request.data

        serializer_instance = ComplaintUpdateSerializer(
            complaint, data=form_data
        )

        if serializer_instance.is_valid():
            serializer_instance.save()

            return Response(
                {"Message": "Complaint Updated Successfully"},
                status=200
            )

        return Response(serializer_instance.errors, status=400)

    def delete(self, request, pk):
        complaint = get_object_or_404(
            Complaint, id=pk, user=request.user
        )

        complaint.delete()

        return Response(
            {"Message": "Complaint Deleted Successfully"},
            status=200
        )


class PaymentListCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(
            rental__user=request.user
        )

        serializer_instance = PaymentSerializer(
            payments, many=True
        )

        return Response(serializer_instance.data, status=200)

    def post(self, request):
        form_data = request.data

        serializer_instance = PaymentSerializer(
            data=form_data,
            context={"request": request}
        )

        if serializer_instance.is_valid():
            serializer_instance.save()

            return Response(
                {"Message": "Payment Record Created Successfully"},
                status=201
            )

        return Response(serializer_instance.errors, status=400)


class PaymentRetrieveView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(
            Payment,
            id=pk,
            rental__user=request.user
        )

        serializer_instance = PaymentSerializer(payment)

        return Response(serializer_instance.data, status=200)
