FROM python:3.8-buster

ARG REQUIREMENTS_FILE
ENV REQUIREMENTS_FILE $REQUIREMENTS_FILE
RUN echo REQUIREMENTS_FILE $REQUIREMENTS_FILE

RUN apt-get update \
  && apt-get install -y --no-install-recommends libpq-dev \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
CMD ls
#COPY . .
COPY requirements*.txt ./

RUN useradd -m -r user \
  && chown -R user:user /app

COPY requirements*.txt ./

RUN pip install --upgrade pip
RUN pip install -r $REQUIREMENTS_FILE
#CMD python manage.py fmt
COPY . .
USER user


#
#FROM python:3.8.6-buster
#
#ARG REQUIREMENTS_FILE=requirements.txt
#
#RUN apt-get update \
#  && apt-get install -y --no-install-recommends libpq-dev \
#  && rm -rf /var/lib/apt/lists/*
#
#WORKDIR /app
#RUN useradd -m -r user \
#  && chown -R user:user /app
#
#COPY requirements*.txt ./
#RUN pip install -r $REQUIREMENTS_FILE
#
#COPY . .
#
#USER user