from src.celery.celery_app import app
from celery.schedules import crontab


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.0, add.s(2, 2), name="add every 30 seconds")
    sender.add_periodic_task( 
        crontab(minute="*"),
        add.s(2, 2),
        name="add every minute",
    )


@app.task
def add(x: int, y: int) -> int:
    result = x + y
    print(result)
    return result
