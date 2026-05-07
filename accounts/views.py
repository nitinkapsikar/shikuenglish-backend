import random
from django.utils import timezone
from django.conf import settings



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Lesson

from openai import OpenAI

from .models import OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer


# ======================================
# 🔥 OpenAI Client
# ======================================
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ======================================
# 📱 SEND OTP (FAKE OTP MODE)
# ======================================
class SendOTPView(APIView):

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data["phone"]

        otp = str(random.randint(100000, 999999))

        OTP.objects.update_or_create(
            phone=phone,
            defaults={
                "otp": otp,
                "created_at": timezone.now()
            }
        )

        print(f"OTP for {phone}: {otp}")

        return Response(
            {
                "message": "OTP sent successfully",
                "otp": otp   # 🔥 IMPORTANT (fake OTP for testing)
            },
            status=status.HTTP_200_OK
        )


# ======================================
# 🔐 VERIFY OTP
# ======================================
class VerifyOTPView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        try:
            record = OTP.objects.get(phone=phone)

        except OTP.DoesNotExist:
            return Response(
                {"error": "OTP not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if record.is_expired():
            record.delete()
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if record.otp != otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.delete()

        return Response(
            {
                "message": "Login successful",
                "token": "dummy_token_123"
            },
            status=status.HTTP_200_OK
        )


# ======================================
# 🤖 REAL AI CHAT
# ======================================
class ChatAPIView(APIView):

    def post(self, request):

        user_message = request.data.get("message", "")
        topic = request.data.get("topic", "greetings")

        if not user_message:
            return Response(
                {"error": "Message required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            prompt = f"""
            You are Anvi, a friendly English teacher.

            Teach beginner students spoken English.

            Topic: {topic}

            Student said: {user_message}

            Rules:
            1. Reply like teacher
            2. Correct grammar
            3. Keep short
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            ai_reply = response.choices[0].message.content

            return Response(
                {"reply": ai_reply},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ======================================
# 🎯 LESSON CHAT
# ======================================
class LessonChatAPIView(APIView):

    def post(self, request):

        day = request.data.get("day")
        step = request.data.get("step")

        try:

            lesson = Lesson.objects.get(
                day=day,
                step=step
            )

            return Response({
                "reply": lesson.message,
                "next_step": lesson.next_step,
                "completed": lesson.next_step == 0
            })

        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )
class LessonAPIView(APIView):

    def post(self, request):
        day = request.data.get("day")
        step = request.data.get("step")

        try:
            lesson = Lesson.objects.get(day=day, step=step)

            return Response({
                "message": lesson.message,
                "next_step": lesson.next_step
            })

        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )