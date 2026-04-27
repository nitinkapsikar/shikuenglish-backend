from rest_framework import serializers
import re


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        value = value.strip()

        # Accept only international format: +XXXXXXXXXX
        if not re.fullmatch(r'\+\d{10,15}', value):
            raise serializers.ValidationError(
                "Phone must include country code (e.g. +919876543210)"
            )

        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate_phone(self, value):
        value = value.strip()

        if not re.fullmatch(r'\+\d{10,15}', value):
            raise serializers.ValidationError(
                "Invalid phone number format"
            )

        return value

    def validate_otp(self, value):
        value = value.strip()

        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Invalid OTP")

        return value