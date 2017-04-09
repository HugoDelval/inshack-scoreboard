#!/bin/bash
let nbcpu=$(lscpu | grep --perl-regexp "^CPU\(s\):\s*\d+$" | grep --perl-regexp -o "\d+")
trigger=`echo "$nbcpu*0.85"|bc`
load=`cat /proc/loadavg | awk '{print $1}'`
response=`echo | awk -v T=$trigger -v L=$load 'BEGIN{if ( L > T){ print "greater"}}'`
if [[ $response = "greater" ]]
then
curl -s --user 'api:key-CHANGE_ME' \
    https://api.mailgun.net/v3/123.mailgun.org/messages \
    -F from='scoreboard instance <me@gmail.com>' \
    -F to="me@gmail.com" \
    -F subject="High load on server - [ $load ]" \
    -F text="$(sar -q)" -vvv
fi
