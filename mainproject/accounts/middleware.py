from django.utils import timezone
from django.contrib.sessions.models import Session
from .models import UserActivity, User

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only proceed if it's a real user session
        user_id = request.session.get("last_user_id")
        activity_id = request.session.get("activity_id")

        if user_id and activity_id:
            session_key = request.session.session_key
            try:
                session = Session.objects.get(session_key=session_key)
                expire_time = session.expire_date
                if timezone.now() > expire_time:
                    # session expired — mark UserActivity as ended
                    UserActivity.objects.filter(pk=activity_id, end_time__isnull=True).update(
                        end_time=expire_time,
                        logout_date=expire_time.date()
                    )
            except Session.DoesNotExist:
                pass 

        return response
