FROM python:3.11.2-bullseye

WORKDIR /app

RUN pip install poetry && poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

RUN cd docs && make apidocs && make html


FROM nginx:1.14-alpine

WORKDIR /app

RUN rm -rf /etc/nginx/conf.d
COPY docs/nginx.conf /etc/nginx/nginx.conf

# Copy build dist files to NGINX image
COPY --from=0 /app/docs/_build/html /app
