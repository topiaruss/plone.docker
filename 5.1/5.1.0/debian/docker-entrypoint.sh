#!/bin/bash
set -ex

COMMANDS="debug help logtail show stop adduser fg kill quit run wait console foreground logreopen reload shell status"
START="start restart zeoserver"
CMD="bin/instance"

gosu plone python /docker-initialize.py

echo '######## PATCH THE UPGRADE ##################'
echo 'plone.app.upgrade-2.0.11-py2-none-any.ovo/plone/app/upgrade/v50/final.py'

sed -i.bak '/def_smaxage:/i \
    if not hasattr(registry.records[maxage].field, "recordName"):\
        return\
' /plone/buildout-cache/eggs/plone.app.upgrade-2.0.11-py2-none-any.ovo/plone/app/upgrade/v50/final.py

grep -B5 -A2 'def_smaxage:' /plone/buildout-cache/eggs/plone.app.upgrade-2.0.11-py2-none-any.ovo/plone/app/upgrade/v50/final.py

echo '######## PATCHED THE UPGRADE ##################'

if [ -e "custom.cfg" ]; then
  if [ ! -e "bin/develop" ]; then
    gosu plone bin/buildout -c custom.cfg
    gosu plone python /docker-initialize.py
  fi
fi

if [[ "$1" == "zeo"* ]]; then
  CMD="bin/$1"
fi

if [ -z "$HEALTH_CHECK_TIMEOUT" ]; then
  HEALTH_CHECK_TIMEOUT=1
fi

if [ -z "$HEALTH_CHECK_INTERVAL" ]; then
  HEALTH_CHECK_INTERVAL=1
fi

if [[ $START == *"$1"* ]]; then
  _stop() {
    gosu plone $CMD stop
    kill -TERM $child 2>/dev/null
  }

  trap _stop SIGTERM SIGINT
  gosu plone $CMD start
  gosu plone $CMD logtail &
  child=$!

  pid=`$CMD status | sed 's/[^0-9]*//g'`
  if [ ! -z "$pid" ]; then
    echo "Application running on pid=$pid"
    sleep "$HEALTH_CHECK_TIMEOUT"
    while kill -0 "$pid" 2> /dev/null; do
      sleep "$HEALTH_CHECK_INTERVAL"
    done
  else
    echo "Application didn't start normally. Shutting down!"
    _stop
  fi
else
  if [[ $COMMANDS == *"$1"* ]]; then
    exec gosu plone bin/instance "$@"
  fi
  exec "$@"
fi
