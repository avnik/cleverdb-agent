# cleverdb-agent [![Build Status](https://magnum.travis-ci.com/sendgridlabs/cleverdb-agent.svg?token=Aq5pNsW6rH3CDcNzg2ik)](https://magnum.travis-ci.com/sendgridlabs/cleverdb-agent)

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

	CD_API_KEY=sample_api_key CD_DB_ID=sample_db_id bash -c "$(curl -L https://raw.githubusercontent.com/sendgridlabs/cleverdb-agent/master/bin/install_agent.sh?token=22681__eyJzY29wZSI6IlJhd0Jsb2I6c2VuZGdyaWRsYWJzL2NsZXZlcmRiLWFnZW50L21hc3Rlci9iaW4vaW5zdGFsbF9hZ2VudC5zaCIsImV4cGlyZXMiOjE0MDY4Mzk5MDZ9--afefcfa6da0d3adec37db06fd9395e66db087130)"
