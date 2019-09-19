# Copyright 2019 Silverbackhq
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Local Library
from app.modules.entity.subscriber_entity import SubscriberEntity


class Subscriber():

    PENDING = "pending"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    EMAIL = "email"
    PHONE = "phone"
    ENDPOINT = "endpoint"

    __subscriber_entity = None

    def __init__(self):
        self.__subscriber_entity = SubscriberEntity()

    def get_one_by_id(self, id):
        subscriber = self.__subscriber_entity.get_one_by_id(id)

        if not subscriber:
            return False

        return {
            "id": subscriber.id,
            "email": subscriber.email,
            "phone": subscriber.phone,
            "endpoint": subscriber.endpoint,
            "auth_token": subscriber.auth_token,
            "type": subscriber.type,
            "status": subscriber.status,
            "external_id": subscriber.external_id
        }

    def get_one_by_external_id(self, external_id):
        return self.__subscriber_entity.get_one_by_external_id(external_id)

    def insert_one(self, subscriber):
        return self.__subscriber_entity.insert_one(subscriber)

    def update_one_by_id(self, id, subscriber_data):
        return self.__subscriber_entity.update_one_by_id(id, subscriber_data)

    def count_all(self):
        return self.__subscriber_entity.count_all()

    def count_by_status(self, status):
        return self.__subscriber_entity.count_by_status(status)

    def get_iterator(self, status="verified"):
        return self.__subscriber_entity.get_iterator(status)

    def get_all(self, offset=None, limit=None):
        return self.__subscriber_entity.get_all(offset, limit)

    def delete_one_by_id(self, id):
        return self.__subscriber_entity.delete_one_by_id(id)
