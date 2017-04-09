#!/usr/bin/env bash
rm -rf /tmp/dbtempdump/
mkdir /tmp/dbtempdump/
chmod o-rwx /tmp/dbtempdump/
curl http://213.32.77.192:1818/db.sql > /tmp/dbtempdump/out.sql
echo "mysql -uroot -pPjEfl89zpNMzMnjwlwvx < /tmp/dbtempdump/out.sql"
echo "rm -rf /tmp/dbtempdump/"
