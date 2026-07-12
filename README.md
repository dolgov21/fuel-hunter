## Celery + RabbitMQ – local startup

```shell
celery --app src.celery.celery_app worker --pool threads --loglevel INFO
```

```shell
celery --app src.celery.celery_app beat
```