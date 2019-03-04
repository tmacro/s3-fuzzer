#!/bin/sh

if [ -z "$NO_SERVICES" ]; then
    exec /init
else
    if [ -n "$ANTITIMEOUT" ]; then
        sh /etc/services.d/anti-timeout/run &
    fi
    ANTI_PID=$!
    cd /app
	s3fuzz -v
    RET_CODE=$?
    if [ -n "$ANTITIMEOUT" ]; then
        kill -9 $ANTI_PID
    fi
    exit $RET_CODE
fi
