"""
Incident Update Notification Module
"""

# Local Library
from app.modules.entity.incident_update_notification_entity import IncidentUpdateNotificationEntity


class IncidentUpdateNotification():

    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"

    __incident_update_notification_entity = None

    def __init__(self):
        self.__incident_update_notification_entity = IncidentUpdateNotificationEntity()

    def get_one_by_id(self, id):
        item = self.__incident_update_notification_entity.get_one_by_id(id)

        if not item:
            return False

        return {
            "id": item.id,
            "incident_update": item.incident_update,
            "subscriber": item.subscriber,
            "status": item.status
        }

    def count_by_update_status(self, update_id, status):
        return self.__incident_update_notification_entity.count_by_update_status(update_id, status)

    def insert_one(self, item):
        return self.__incident_update_notification_entity.insert_one(item)

    def update_one_by_id(self, id, data):
        return self.__incident_update_notification_entity.update_one_by_id(id, data)

    def is_subscriber_notified(self, incident_update_id, subscriber_id):
        return self.__incident_update_notification_entity.is_subscriber_notified(incident_update_id, subscriber_id)

    def delete_one_by_id(self, id):
        return self.__incident_update_notification_entity.delete_one_by_id(id)
