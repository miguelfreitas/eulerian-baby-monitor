#!/bin/bash
#exit
SERVICE="xeyes"
ARGS="+shape"
SERVICE="mplayer"
ARGS="/usr/share/sounds/Kopete_Event.ogg"
if pgrep -x "$SERVICE" >/dev/null
then
    #echo "$SERVICE is running"
    :
else
    #echo "$SERVICE stopped"
    ALARM_ACTION_FILE="/srv/www/tmp/alarm-action"
    ALARM_ACTION=$(cat $ALARM_ACTION_FILE)
    #echo "$ALARM_ACTION"
    if [ "$ALARM_ACTION" == "on" ]; then
        $SERVICE $ARGS &
    fi
    if [ "$ALARM_ACTION" == "snooze" ]; then
        TIMEOUT=$(((`date +%s` - `stat -L --format %Y $ALARM_ACTION_FILE`) > (10*60)))
        if [ $TIMEOUT == "1" ]; then
            $SERVICE $ARGS &
        fi
    fi
fi
