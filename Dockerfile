FROM tmacro/python:3

ADD ./requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

ADD ./s6 /etc
ADD ./docker-entrypoint.sh /
ADD ./ /app
RUN cd ./app && \
	python setup.py develop

ENTRYPOINT [ "sh", "/docker-entrypoint.sh" ]
