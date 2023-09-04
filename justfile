alias r := runserver
alias run := runserver
alias m := migrate
alias mm := makemigrations

docker:
  docker compose -f docker-compose.test.yml up -d postgres

test:
  pytest pear2pay

runserver:
  python manage.py runserver localhost:8000

migrate:
  python manage.py migrate

makemigrations +ARGS:
  python manage.py makemigrations {{ARGS}}

ruff:
  ruff check pear2pay
