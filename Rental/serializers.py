
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from Rental.models import Tools, Rental, Complaint, Payment


# User Serializer

class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "email": {
                "required": True,
                "allow_blank": False
            }
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# Tools Serializer

class ToolsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tools
        fields = "__all__"
        read_only_fields = [
            "owner",
            "rented_by",
            "availability_status"
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero"
            )
        return value


# Rental Serializer

class RentalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rental
        fields = "__all__"
        read_only_fields = [
            "user",
            "total_amount",
            "rental_status",
            "review"
        ]

    def validate(self, data):
        tool = data["tool"]
        rental_date = data["rental_date"]
        return_date = data["return_date"]
        user = self.context["request"].user

        if not tool.availability_status:
            raise serializers.ValidationError(
                "Tool is currently unavailable"
            )

        if tool.owner == user:
            raise serializers.ValidationError(
                "You cannot rent your own tool"
            )

        if return_date <= rental_date:
            raise serializers.ValidationError(
                "Return date must be after rental date"
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        tool = validated_data["tool"]
        user = validated_data["user"]

        rental_date = validated_data["rental_date"]
        return_date = validated_data["return_date"]

        days = (return_date - rental_date).days

        updated = Tools.objects.filter(
            id=tool.id,
            availability_status=True
        ).update(
            availability_status=False,
            rented_by=user
        )

        if not updated:
            raise serializers.ValidationError(
                "Tool is no longer available"
            )

        tool.refresh_from_db()

        validated_data["total_amount"] = days * tool.price

        return Rental.objects.create(**validated_data)


# Rental Update Serializer

class RentalUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rental
        fields = ["return_date"]

    def validate_return_date(self, value):

        if value <= self.instance.rental_date:
            raise serializers.ValidationError(
                "Return date must be after rental date"
            )

        if self.instance.rental_status in [
            "Completed", "Rejected"
        ]:
            raise serializers.ValidationError(
                "This rental cannot be updated"
            )

        if Payment.objects.filter(
            rental=self.instance
        ).exists():
            raise serializers.ValidationError(
                "Rental cannot be updated after payment record creation"
            )

        return value

    def update(self, instance, validated_data):
        instance.return_date = validated_data["return_date"]

        days = (
            instance.return_date - instance.rental_date
        ).days

        instance.total_amount = days * instance.tool.price

        instance.save(
            update_fields=["return_date", "total_amount"]
        )

        return instance


# Complaint Serializer

class ComplaintSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = "__all__"
        read_only_fields = ["user", "complaint_date"]

    def validate(self, data):
        tool = data["tool"]
        user = self.context["request"].user

        if not Rental.objects.filter(
            user=user,
            tool=tool
        ).exists():
            raise serializers.ValidationError(
                "You have not rented this tool"
            )

        if Complaint.objects.filter(
            user=user,
            tool=tool
        ).exists():
            raise serializers.ValidationError(
                "You have already complained about this tool"
            )

        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return Complaint.objects.create(
                    **validated_data
                )
        except IntegrityError:
            raise serializers.ValidationError(
                "Unable to create complaint. Check for duplicate complaints."
            )


# Complaint Update Serializer

class ComplaintUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = ["complaint"]


# Payment Serializer

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "amount",
            "payment_date",
            "payment_status"
        ]

    def validate(self, data):
        rental = data["rental"]
        user = self.context["request"].user

        if rental.user != user:
            raise serializers.ValidationError(
                "You cannot pay for another user's rental"
            )

        if rental.rental_status == "Rejected":
            raise serializers.ValidationError(
                "Cannot pay for a rejected rental"
            )

        if Payment.objects.filter(
            rental=rental
        ).exists():
            raise serializers.ValidationError(
                "Payment record already exists"
            )

        return data

    def create(self, validated_data):
        rental = validated_data["rental"]
        validated_data["amount"] = rental.total_amount

        try:
            with transaction.atomic():
                return Payment.objects.create(
                    **validated_data
                )
        except IntegrityError:
            raise serializers.ValidationError(
                "Unable to create payment. Check for duplicate payments."
            )
