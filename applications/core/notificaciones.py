import json

from django.conf import settings
from django.forms.models import model_to_dict
from webpush import send_user_notification
from pywebpush import WebPushException, webpush
from webpush.models import Group
from threading import Thread


def _process_subscription_info(subscription):
    subscription_data = model_to_dict(subscription, exclude=["browser", "id"])
    endpoint = subscription_data.pop("endpoint")
    p256dh = subscription_data.pop("p256dh")
    auth = subscription_data.pop("auth")
    return {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth}
    }

class UserNotificationThread(Thread):
    def __init__(self, user, payload, ttl=0):
        self.user = user
        self.payload = payload
        self.ttl = ttl
        Thread.__init__(self)

    def run(self):
        try:
            payload = json.dumps(self.payload)
            push_infos = self.user.webpush_info.select_related("subscription")
            vapid_data = {}
            webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
            vapid_private_key = webpush_settings.get('VAPID_PRIVATE_KEY')
            vapid_admin_email = webpush_settings.get('VAPID_ADMIN_EMAIL')
            for push_info in push_infos:
                
                subscription_data = _process_subscription_info(push_info.subscription)
                if vapid_private_key:
                    vapid_data = {
                        'vapid_private_key': vapid_private_key,
                        'vapid_claims': {"sub": "mailto:{}".format(vapid_admin_email)}
                    }
                try:
                    webpush(subscription_info=subscription_data, data=payload, ttl=self.ttl, **vapid_data)
                    print("Notificacion enviada")
                except WebPushException as e:
                    print("Error enviando notificacion")
                    if e.response.status_code == 410:
                        push_info.subscription.delete()
        except Exception as e:
            print(e)
            pass  


# Envia un push notificaction a un grupo
def send_notification_to_group(group_name, payload, ttl=0):

    push_infos = Group.objects.get(name=group_name).webpush_info.select_related("subscription")
    
    for push_info in push_infos:
        try:
            send_user_notification(user=push_info.subscription, payload=payload, ttl=ttl)
        except Exception as e:
            print(push_info.subscription)
            pass

class GroupNotificationThread(Thread):
    def __init__(self, group_name, payload, ttl=0):
        self.group_name = group_name
        self.payload = payload
        self.ttl = ttl
        Thread.__init__(self)
        
    def run(self):
        try:
            send_notification_to_group(self.group_name, self.payload, self.ttl)
        except Exception as e:
            pass


# *********************************************************************************
# Envia un push notificaction a un usuario por un Thread
# *********************************************************************************
def send_notification_to_user(user, payload, ttl=0):
    UserNotificationThread(user, payload, ttl).start()
    return  


# *********************************************************************************
# Envia una notificación push a un grupo 
# *********************************************************************************
def send_notification_to_group_thread(group_name, payload, ttl=0):
    GroupNotificationThread(group_name, payload, ttl).start()
    return

