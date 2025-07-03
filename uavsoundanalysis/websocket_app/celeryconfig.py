CELERY_BEAT_SCHEDULE = {
    'my-task': {
        'task': 'tasks.my_task',
        'schedule': 120.0,  # Run every 2 minutes (120 seconds)
    },
}