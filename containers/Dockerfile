FROM ubuntu:16.04

RUN apt-get update -y && apt-get install -y python3 python3-pip default-jre curl mysql-client

RUN pip3 install pipenv

ADD . /app

WORKDIR /app

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# RUN pipenv install --system --python $(which python3)

# RUN pipenv install --system --python $(which python3) -d

# FIXME get pipenv --system to work

# and don't do this:

RUN pip3 install boto3 sh flask flask-restful urllib3 gunicorn psutil awscli ipython hammock

RUN curl -LO https://github.com/broadinstitute/cromwell/releases/download/36/cromwell-36.jar

EXPOSE 80

# TODO use gunicorn instead
CMD ["python3", "app.py"]
