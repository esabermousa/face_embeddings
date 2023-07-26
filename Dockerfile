# syntax=docker/dockerfile:experimental
FROM python:3.10.11-slim

# create and copy app into container
RUN mkdir /app

# set working directory
WORKDIR /app

# copy dependencies files
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# set default environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev musl-dev libpq-dev git openssh-client procps build-essential cmake && \
    pip3 install --upgrade pip && \
    pip3 install pipenv && pipenv requirements --dev > requirements.txt && \
    pip3 uninstall --yes pipenv && \
    pip3 install --no-cache-dir -r requirements.txt

# copy source code to container
COPY . .

# packages upgrades should be after any change in the code
# to make sure that new security upgrades are always installed
RUN apt-get update -y && apt-get upgrade -y

EXPOSE 8000

ENTRYPOINT ["sh", "./cmd/entrypoint.sh"]
