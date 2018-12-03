#!/bin/sh

if [ -z "$NO_SERVICES" ]; then
    exec /init
else
    if [ -n "$ANTITIMEOUT" ]; then
        sh /etc/services.d/anti-timeout/run &
    fi
    ANTI_PID=$!
    cd /app

    if [ -z "$SEED" ]; then
        SEED='12345567890'
    fi

    if [ -z "$COUNT" ]; then
        COUNT='-1'
    fi

    if [ -z "$STEP" ]; then
        STEP='0'
    fi

    python run.py "$SEED" "$COUNT" "$STEP"
    RET_CODE=$?
    if [ -n "$ANTITIMEOUT" ]; then
        kill -9 $ANTI_PID
    fi
    exit $RET_CODE
fi
