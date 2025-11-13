web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
webhook_worker: celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h
upload_worker: celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h