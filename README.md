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
	
## Bulding Packages ##
	bin/build	
	
## One Step Installation ##

	CD_API_KEY=sample_api_key CD_DB_ID=sample_db_id bash -c "$(curl -L https://raw.githubusercontent.com/sendgridlabs/cleverdb-agent/master/bin/install_agent.sh)"
