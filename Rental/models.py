
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


# ==========================================
# TOOLS MODEL
# ==========================================

class Tools(models.Model):
    tool_name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    availability_status = models.BooleanField(default=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_tools"
    )

    rented_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="rented_tools",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.tool_name


# ==========================================
# RENTAL MODEL
# ==========================================

class Rental(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="rentals"
    )

    tool = models.ForeignKey(
        Tools,
        on_delete=models.PROTECT,
        related_name="rentals"
    )

    rental_date = models.DateField()
    return_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    rental_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Completed", "Completed")
        ],
        default="Pending"
    )

    review = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.tool.tool_name}"


# ==========================================
# COMPLAINT MODEL
# ==========================================

class Complaint(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    tool = models.ForeignKey(
        Tools,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    complaint = models.TextField()
    complaint_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tool"],
                name="unique_user_tool_complaint"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tool.tool_name}"


# ==========================================
# PAYMENT MODEL
# ==========================================

class Payment(models.Model):
    rental = models.OneToOneField(
        Rental,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("UPI", "UPI"),
            ("Cash", "Cash"),
            ("Card", "Card")
        ]
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Successful", "Successful"),
            ("Failed", "Failed")
        ],
        default="Pending"
    )

    def __str__(self):
        return f"Payment - Rental {self.rental.id}"
