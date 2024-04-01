#!/bin/sh

# Install package
mkdir assets
mkdir media
mkdir logs

echo "DB Connection --- Establishing . . ."

# fast-api-postgresql this name of db, if the database name is called differently,set another name
while ! nc -z diwaiter-postgresql 5432; do

    echo "DB Connection -- Failed!"

    sleep 1

    echo "DB Connection -- Retrying . . ."

done

echo "DB Connection --- Successfully Established!"

until python manage.py check --database default
do
    echo "Check django db connection ..."
    sleep 5
done

echo "Django db connection -- Successfully!"

until python manage.py makemigrations --check --dry-run
do
    echo "Check django makemigrations ..."
    sleep 5
done

echo "Django makemigration -- Successfully!"

until python manage.py migrate
do
    echo "Check django migrations ..."
    sleep 5
done

echo "Django migration -- Successfully!"

python manage.py collectstatic --no-input

# Start Uvicorn
# uvicorn main:backend_app --host 0.0.0.0 --port 8000 --workers 4 --reload
python manage.py runserver 0.0.0.0:8000

exec "$@"
