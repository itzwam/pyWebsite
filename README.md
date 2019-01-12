# pyWebSite

Private website's repository

## Requirements

- flask
- mysql-connector

## Example of runscript

```bash
#!/bin/bash
export BARCODE_HTTP_HOST="127.0.0.1"
export BARCODE_HTTP_PORT="5000"
export BARCODE_HTTP_LOG="/var/log/barcode-server.log"

export BARCODE_MYSQL_HOST="127.0.0.1"
export BARCODE_MYSQL_USER="username"
export BARCODE_MYSQL_PASS="p4ssw0rd"
export BARCODE_MYSQL_DBNAME="barcode"

python main.py
```