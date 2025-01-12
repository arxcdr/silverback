"""
Task Entity Module
"""

# Standard Library
from datetime import datetime
from datetime import timedelta

# Third Party Library
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

# Local Library
from app.models import Task


class TaskEntity():

    def insert_one(self, task):
        """Insert Task"""
        task = Task(
            uuid=task["uuid"],
            status=task["status"],
            executor=task["executor"],
            parameters=task["parameters"],
            result=task["result"],
            user=User.objects.get(pk=task["user_id"]) if task["user_id"] is not None else None
        )

        task.save()
        return False if task.pk is None else task

    def insert_many(self, tasks):
        """Insert Many Tasks"""
        status = True
        for task in tasks:
            status &= True if self.insert_one(task) is not False else False
        return status

    def get_one_by_id(self, id):
        """Get Task By ID"""
        try:
            task = Task.objects.get(pk=id)
            return False if task.pk is None else task
        except Exception:
            return False

    def get_one_by_uuid(self, uuid):
        """Get Task By UUID"""
        try:
            task = Task.objects.get(uuid=uuid)
            return False if task.pk is None else task
        except Exception:
            return False

    def get_many_by_user(self, user_id, order_by, asc):
        """Get Many Tasks By User ID"""
        tasks = Task.objects.filter(user=user_id).order_by(order_by if asc else "-%s" % order_by)
        return tasks

    def get_many_by_executor(self, executor):
        tasks = Task.objects.filter(executor=executor).order_by('-id')
        return tasks

    def update_one_by_id(self, id, new_data):
        """Update Task By ID"""
        task = self.get_one_by_id(id)
        if task is not False:

            if "uuid" in new_data:
                task.uuid = new_data["uuid"]

            if "status" in new_data:
                task.status = new_data["status"]

            if "executor" in new_data:
                task.executor = new_data["executor"]

            if "parameters" in new_data:
                task.parameters = new_data["parameters"]

            if "user_id" in new_data:
                task.user = User.objects.get(pk=new_data["user_id"])

            if "result" in new_data:
                task.result = new_data["result"]

            task.save()
            return True
        return False

    def update_one_by_uuid(self, uuid, new_data):
        """Update Task By UUID"""
        task = self.get_one_by_uuid(uuid)
        if task is not False:

            if "uuid" in new_data:
                task.uuid = new_data["uuid"]

            if "status" in new_data:
                task.status = new_data["status"]

            if "executor" in new_data:
                task.executor = new_data["executor"]

            if "parameters" in new_data:
                task.parameters = new_data["parameters"]

            if "user_id" in new_data:
                task.user = User.objects.get(pk=new_data["user_id"])

            if "result" in new_data:
                task.result = new_data["result"]

            task.save()
            return True
        return False

    def delete_one_by_id(self, id):
        """Delete Task By ID"""
        task = self.get_one_by_id(id)
        if task is not False:
            count, deleted = task.delete()
            return True if count > 0 else False
        return False

    def delete_one_by_uuid(self, uuid):
        """Delete Task By UUID"""
        task = self.get_one_by_uuid(uuid)
        if task is not False:
            count, deleted = task.delete()
            return True if count > 0 else False
        return False

    def delete_old_tasks_by_executor(self, executor, minutes):
        return Task.objects.filter(executor=executor).filter(created_at__lte=make_aware(datetime.now() - timedelta(minutes=minutes))).delete()

    def count_all_tasks(self):
        return Task.objects.count()
