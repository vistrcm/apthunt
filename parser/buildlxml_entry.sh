#!/usr/bin/env bash

LXML_TO_INSTALL=${LXML_VER:-lxml==4.2.1}

yum update -y
yum install -y gcc libxml2-devel libxslt-devel
pip install --upgrade pip
pip install ${LXML_TO_INSTALL}
cp -r /var/lang/lib/python3.6/site-packages/lxml* /out/