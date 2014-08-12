# cleverdb-agent [![Build Status](https://travis-ci.org/sendgridlabs/cleverdb-agent.svg)](https://travis-ci.org/sendgridlabs/cleverdb-agent)

This user agent will be installed on customer's machine.

## Requirements and Support ##

This agent support the following:

	Python 2.6 and up
	Ubuntu
	CentOS

## Install packages for development ##
	bin/install
	
## Testing ##
	bin/test
	
## Bulding Debian (.deb) Package ##
	# turn on Ubuntu vagrant box and go inside it
	vagrant up ubuntu && vagrant ssh ubuntu
	
	# modify changelog
	debchange -i 
	
	# bump up version inside Python script as well
	cleverdb/version.py
	
	# go inside the cleverdb-agent directory and build
	cd cleverdb-agent && bin/build	

## Bulding RedHat (.rpm) Package ##
	# turn on CentOS vagrant box and go inside it
	vagrant up centos && vagrant ssh ubuntu
	
	# bump up version inside Python script
	cleverdb/version.py
	
	# go inside the cleverdb-agent directory and build
	cd cleverdb-agent && bin/build

## Deploy Packages ##
	# deploy package to staging (unstable) repo
	bin/deploy
	
	# deploy package to production (stable) repo
	bin/deploy stable
	
## One Step Installation ##

	CD_ENV=stable CD_CONNECT_HOST=https://connect.cleverdb.io CD_API_KEY=sample_api_key CD_DB_ID=sample_db_id bash -c "$(curl -L https://raw.githubusercontent.com/sendgridlabs/cleverdb-agent/master/bin/install_agent.sh)"
