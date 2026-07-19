## Celery + RabbitMQ – local startup

```shell
celery --app src.celery.celery_app worker --pool threads --loglevel INFO
```

```shell
celery --app src.celery.celery_app beat
```

## Импортировать данные в PostgreSQL

Пока в проекте нет синхронизации городов и доступны только АЗС города Алатырь.

```shell
psql -U $POSTGRES_USER -d $POSTGRES_DB -h $POSTGRES_HOST -p $POSTGRES_HOST_PORT < src/sql/alatyr-stations.sql
```

```shell
docker compose exec -T postgres psql -U denis -d fuel_hunter < src/sql/alatyr-stations.sql
```