FROM python:3.11

ENV PIP_NO_CACHE_DIR=false\
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

ENTRYPOINT ["/bin/bash"]
CMD ["-c", "./manage.py run"]

RUN pip install -U poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Set Git SHA environment variable
ARG git_sha="development"
ENV GIT_SHA=$git_sha

COPY . .
