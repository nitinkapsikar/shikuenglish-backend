import random
from django.utils import timezone
from django.conf import settings



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Lesson, UserProgress

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
class LessonAPIView(APIView):




    def post(self, request):

        day = request.data.get("day")
        step = request.data.get("step")
        email = request.data.get("email")
        user_message = request.data.get("message", "").strip()


        language = request.data.get(
            "language",
            "english"
        )


        try:



            lesson = Lesson.objects.get(
                day=day,
                step=step
            )

            if language == "marathi":
                lesson_message = (
                        lesson.message_marathi
                        or lesson.message
                )
            else:
                lesson_message = lesson.message



            expected = (
                lesson.expected_input or ""
            ).lower().strip()

            user_input = user_message.lower().strip()

            # 🔥 FIRST MESSAGE
            if user_message == "":

                return Response({
                    "message": lesson_message,
                    "next_step": step,
                    "completed": False
                })

            # 🔥 VALIDATION
            is_correct = False

            # exact
            if lesson.validation_type == "exact":

                is_correct = (
                        user_input == expected
                )

            # contains
            elif lesson.validation_type == "contains":

                is_correct = (
                        expected in user_input
                )

            # starts_with
            elif lesson.validation_type == "starts_with":

                if user_input.startswith(expected):

                    words = user_input.split()

                    if len(words) >= lesson.min_words:

                        is_correct = True

            # 🔥 CORRECT ANSWER
            if is_correct:

                # 🔥 LESSON COMPLETED
                if lesson.next_step == 0:

                    progress, created = UserProgress.objects.get_or_create(
                        email= email
                    )

                    progress.completed_day = day
                    progress.unlocked_day = day + 1
                    progress.current_step = 1

                    progress.save()

                    return Response({
                        "message": lesson_message,
                        "next_step": 0,
                        "completed": True,
                        "correct": True
                    })

                # 🔥 NEXT STEP
                next_lesson = Lesson.objects.get(
                    day=day,
                    step=lesson.next_step
                )

                next_message = (
                    next_lesson.message_marathi
                    if language == "marathi" and next_lesson.message_marathi
                    else next_lesson.message
                )

                return Response({
                    "message":  next_message,
                    "next_step": next_lesson.step,
                    "completed": False,
                    "correct": True
                })

            # 🔥 WRONG ANSWER → AI CORRECTION
            else:

                prompt = f"""
                You are a friendly English teacher.
    
                Student question:
                {lesson.message}
    
                Expected answer:
                {lesson.expected_input}
    
                Student answered:
                {user_message}
    
                Rules:
                1. Correct politely
                2. Keep response short
                3. Explain simply
                4. Ask student to try again
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                ai_reply = response.choices[0].message.content

                return Response({
                    "message": ai_reply,
                    "next_step": step,
                    "completed": False,
                    "correct": False
                })

        except Lesson.DoesNotExist:

            return Response(
                {"error": "Lesson not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class UserProgressAPIView(APIView):

    def post(self, request):

        email= request.data.get("email")

        try:

            progress = UserProgress.objects.get(
                email=email
            )

            return Response({

                "completed_day":
                    progress.completed_day,

                "unlocked_day":
                    progress.unlocked_day,

                "current_step":
                    progress.current_step,

                "is_premium":
                    progress.is_premium
            })

        except UserProgress.DoesNotExist:

            return Response({

                "completed_day": 0,

                "unlocked_day": 1,

                "current_step": 1
            })

class ActivatePremiumAPIView(APIView):

    def post(self, request):

        email = request.data.get("email")

        progress = UserProgress.objects.get(
          email=email
        )

        progress.is_premium = True

        progress.save()

        return Response({
            "success": True
        })

class GoogleLoginAPIView(APIView):

    def post(self, request):

        email = request.data.get("email")
        name = request.data.get("name")

        if not email:

            return Response(
                {"error": "Email required"},
                status=400
            )

        progress, created = UserProgress.objects.get_or_create(
            email=email,
            defaults={
                "name": name
            }
        )

        if not created and name:

            progress.name = name
            progress.save()

        return Response({
            "success": True,
            "email": progress.email,
            "name": progress.name,
            "completed_day": progress.completed_day,
            "unlocked_day": progress.unlocked_day,
            "current_step": progress.current_step,
            "is_premium": progress.is_premium
        })