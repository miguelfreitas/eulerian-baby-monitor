#!/bin/bash
#SERVICE="xeyes"
SERVICE="mplayer"
if pgrep -x "$SERVICE" >/dev/null
then
    #echo "$SERVICE is running"
    killall $SERVICE
else
    :
    #echo "$SERVICE stopped"
    # uncomment to start nginx if stopped
    # systemctl start nginx
    # mail  
fi
