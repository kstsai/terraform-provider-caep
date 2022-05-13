#!/bin/bash

#pytest --html=1.html --self-contained-html
#curl -X PUT http://applcmctrl:10286/apidocs/test-report.html --data-binary @1.html

exec /usr/bin/python3 pytestd_main.py
