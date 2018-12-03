FROM tmacro/python:3

ADD ./requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

ADD ./s6 /etc
ADD ./docker-entrypoint.sh /
ADD ./ /app

CMD [ "sh", "/docker-entrypoint.sh" ]
