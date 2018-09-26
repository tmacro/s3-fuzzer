FROM tmacro/python:3

ADD ./requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

ADD ./s6 /etc
ADD ./ /app
