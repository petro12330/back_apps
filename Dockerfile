FROM python:3.8-buster

ARG REQUIREMENTS_FILE
ARG COPY
ENV COPY $COPY
ENV REQUIREMENTS_FILE $REQUIREMENTS_FILE
RUN echo REQUIREMENTS_FILE $REQUIREMENTS_FILE

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq-dev \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
CMD ls


RUN useradd -m -r user \
  && chown -R user:user /app
COPY requirements*.txt ./
RUN pip install --upgrade pip
RUN pip install -r $REQUIREMENTS_FILE
COPY $COPY .
USER user
