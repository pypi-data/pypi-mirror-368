from django.utils.timezone import datetime
from .models import Session
import user_agents


class TakeUserSessionMiddlaware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip = self.get_client_ip(request)

            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key

            session, created = Session.objects.get_or_create(
                user = request.user,
                session_key = session_key,
                defaults = {
                    'user_agent': user_agent,
                    'ip_address': ip,
                    'device': user_agents.parse(user_agent).device.family,
                    'browser': user_agents.parse(user_agent).browser.family,
                }
            )

            session.user_agent = user_agent
            session.ip_address = ip
            session.last_seen = datetime.now()
            session.save()
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')