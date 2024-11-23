mig:
	python3 manage.py makemigrations
	python3 manage.py migrate
user:
	python3 manage.py createsuperuser
celery:
	celery -A root worker -l INFO
celery_test:
	 celery -A root worker --loglevel=INFO --concurrency=2 --prefetch-multiplier=1
