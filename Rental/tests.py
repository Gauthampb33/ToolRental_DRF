from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from Rental.models import Complaint, Payment, Rental, Tools
from Rental.serializers import (
    ComplaintSerializer,
    PaymentSerializer,
    RentalSerializer,
)


class RentalSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="renter",
            email="renter@example.com",
            password="test-password",
        )
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )
        self.tool = Tools.objects.create(
            tool_name="Drill",
            description="Cordless drill",
            category="Power tools",
            price="25.00",
            owner=self.owner,
        )
        self.factory = APIRequestFactory()

    def test_create_rental_marks_tool_unavailable(self):
        request = self.factory.post("/rentals/")
        request.user = self.user
        serializer = RentalSerializer(
            data={
                "tool": self.tool.pk,
                "rental_date": "2026-11-25",
                "return_date": "2026-11-28",
            },
            context={"request": request},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        rental = serializer.save()
        self.tool.refresh_from_db()

        self.assertEqual(rental.user, self.user)
        self.assertEqual(rental.total_amount, 75)
        self.assertFalse(self.tool.availability_status)
        self.assertEqual(self.tool.rented_by, self.user)

    def test_rejects_return_date_before_rental_date(self):
        serializer = RentalSerializer(
            data={
                "tool": self.tool.pk,
                "rental_date": "2026-11-25",
                "return_date": "2026-11-24",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("return_date", serializer.errors)


class ComplaintAndPaymentSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            password="test-password",
        )
        self.owner = User.objects.create_user(
            username="tool-owner",
            password="test-password",
        )
        self.tool = Tools.objects.create(
            tool_name="Saw",
            description="Table saw",
            category="Power tools",
            price="40.00",
            owner=self.owner,
            availability_status=False,
            rented_by=self.user,
        )
        self.rental = Rental.objects.create(
            user=self.user,
            tool=self.tool,
            rental_date="2026-11-20",
            return_date="2026-11-22",
            total_amount="80.00",
        )
        self.factory = APIRequestFactory()

    def test_complaint_requires_rental(self):
        request = self.factory.post("/complaints/")
        request.user = self.user
        serializer = ComplaintSerializer(
            data={"tool": self.tool.pk, "complaint": "It stopped working"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_payment_uses_rental_total_and_rejects_duplicate(self):
        request = self.factory.post("/payments/")
        request.user = self.user
        serializer = PaymentSerializer(
            data={"rental": self.rental.pk, "payment_method": "UPI"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        payment = serializer.save()
        self.assertEqual(payment.amount, 80)

        duplicate = PaymentSerializer(
            data={"rental": self.rental.pk, "payment_method": "Cash"},
            context={"request": request},
        )
        self.assertFalse(duplicate.is_valid())
