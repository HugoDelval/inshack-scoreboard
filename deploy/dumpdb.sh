#!/usr/bin/env bash
rm -rf /tmp/dbtempdump/
mkdir /tmp/dbtempdump/
chmod o-rwx /tmp/dbtempdump/
mysqldump --all-databases --single-transaction --user=root -pPjEfl89zpNMzMnjwlwvx > /tmp/dbtempdump/db.sql
curl -v -F db=@/tmp/dbtempdump/db.sql http://hoho:CHANGE_ME@213.32.77.192:8080/save
rm -rf /tmp/dbtempdump/
