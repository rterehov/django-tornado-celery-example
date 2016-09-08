# coding: utf-8

from celery.task.control import revoke

def cancel_tasks(tasks):
    for task in tasks:
        if task.celery_id:
            revoke(task.celery_id, terminate=True)
            task.completed = True
            task.save()
