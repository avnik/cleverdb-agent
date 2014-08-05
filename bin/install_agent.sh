#!/bin/bash
# CleverDb agent install script.
set -e
gist_request=/tmp/agent-gist-request.tmp
gist_response=/tmp/agent-gist-response.tmp
yum_repo="https://yum.cleverdb.io"
apt_repo="https://apt.cleverdb.io"
apt_key_repo="hkp://apt.cleverdb.io:80"
app_name=cleverdb-agent
app_path=/opt/sendgridlabs/cleverdb-agent
app_config=/etc/$app_name/config
app_url="https://cleverdb.io"
repo_url="https://github.com/sendgridlabs/cleverdb-agent"
install_log="$app_name-install.log"

# SSH detection
has_ssh=$(which ssh || echo "no")
if [ $has_ssh == "no" ]; then
    printf "\033[31mSSH is required to install $app_name.\033[0m\n"
    exit 1;
fi

# OS/Distro detection
if [ -f /etc/debian_version ]; then
    OS=Debian
elif [ -f /etc/redhat-release ]; then
    # Just mark as RedHat and we'll use Python version detection
    # to know what to install
    OS=RedHat
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
else
    OS=$(uname -s)
fi

if [ $OS == "Darwin" ]; then
    printf "\033[31mMac OS is currently not supported.\033[0m\n"
    exit 1;
fi

# Python detection
has_python=$(which python || echo "no")
if [ $has_python == "no" ]; then
    printf "\033[31mPython is required to install $app_name.\033[0m\n"
    exit 1;
else
	# Make sure Python is at least 2.6
	PY_VERSION=$(python -c 'import sys; print "%d.%d" % (sys.version_info[0], sys.version_info[1])')

	if [[ "$PY_VERSION" < "2.6" ]]; then
		echo $PY_VERSION
		printf "\033[31mPython 2.6 or higher is required to install $app_name.\033[0m\n"
    	exit 1;
	fi
fi

# Root user detection
if [ $(echo "$UID") == "0" ]; then
    sudo_cmd=''
else
    sudo_cmd="sudo "
fi

if [ $(which curl) ]; then
    dl_cmd="curl -f"
else
    dl_cmd="wget --quiet"
fi

# Set up a named pipe for logging
npipe=/tmp/$$.tmp
mknod $npipe p

# Log all output to a log for error checking
tee <$npipe $install_log &
exec 1>&-
exec 1>$npipe 2>&1
trap "rm -f $npipe" EXIT

function on_error() {
    printf "\033[31m
It looks like you hit an issue when trying to install $app_name.

Troubleshooting and basic usage information for $app_name are available at:

    $app_url

If you're still having problems, please send an email to support@cleverdb.io
with the contents of $install_log and we'll do our very best to help you
solve your problem.\n\033[0m\n"
}
trap on_error ERR

print_missing_key_error() {
	printf "\033[31m
	Required environment variable does not exist. Example usage:

	CD_CONNECT_HOST=https://connect.cleverdb.io CD_API_KEY=sample_api_key CD_DB_ID=sample_db_id ${BASH_SOURCE[0]}\n\033[0m\n"
    exit 1;
}

if [ -n "$CD_API_KEY" ]; then
    apikey=$CD_API_KEY
else
	print_missing_key_error
fi

if [ -n "$CD_DB_ID" ]; then
    dbid=$CD_DB_ID
else
	print_missing_key_error
fi

if [ -n "$CD_CONNECT_HOST" ]; then
    connect_host=$CD_CONNECT_HOST
else
   print_missing_key_error
fi

# Install the necessary package sources
if [ $OS == "RedHat" ]; then
    echo -e "\033[34m\n* Installing YUM sources\n\033[0m"
    $sudo_cmd sh -c "echo -e '[sendgrid]\nname = SendGrid.\nbaseurl = $yum_repo/rpm/\nenabled=1\ngpgcheck=0\npriority=1' > /etc/yum.repos.d/$app_name.repo"

    printf "\033[34m* Installing the $app_name package\n\033[0m\n"

	$sudo_cmd yum -y install $app_name

elif [ $OS == "Debian" -o $OS == "Ubuntu" ]; then
    printf "\033[34m\n* Installing APT package sources\n\033[0m\n"

    $sudo_cmd sh -c "echo 'deb $apt_repo staging main' > /etc/apt/sources.list.d/$app_name.list"
    $sudo_cmd wget -O - $apt_repo/key.asc | $sudo_cmd apt-key add -

    printf "\033[34m\n* Installing the $app_name package\n\033[0m\n"
    $sudo_cmd apt-get update
	$sudo_cmd apt-get install -y --force-yes $app_name
else
    printf "\033[31m
Your OS or distribution is not supported by this install script.
Please follow the instructions on $app_name setup page:

    $app_url\n\033[0m\n"
    exit;
fi

printf "\033[34m\n* Adding your API key to $app_name configuration: $app_config\n\033[0m\n"

# Write db_id and api_key to config file
create_config_file() {
	# create config dir:
	printf "\033[34m\n* Creating config directory /etc/$app_name\n\033[0m\n"
	$sudo_cmd mkdir -p /etc/$app_name

	local file="$app_config"

	if [ ! -f "$app_config" ] ; then
		$sudo_cmd touch "$app_config"
	fi

	$sudo_cmd sh -c "echo '[agent]\napi_key=$apikey\ndb_id=$dbid\nconnect_host=$connect_host' > $app_config"
}
create_config_file

printf "\033[34m* Starting the $app_name...\n\033[0m\n"
$sudo_cmd /etc/init.d/cleverdb-agent start
printf "\033[34m* $app_name started.\n\033[0m\n"

mysql_dump(){
	echo "What is your MySQL database name?"
	read db_name

	echo "What is your MySQL database username? [root]"
	read db_username

	if [ "$db_username" == "" ]; then
		db_username="root"
	fi

	echo "What is your MySQL database password?"
	read -s db_password

	printf "\033[34m* Dumping your database to file...\n\033[0m\n"
	mysqldump -u $db_username --password=$db_password --opt --master-data $db_name > $db_name.sql
	printf "\033[34m* MySQL database dump completed.\n\033[0m\n"
}

upload_dump(){
	printf "\033[34m* Uploading your database dump...\n\033[0m\n"
	$sudo_cmd cleverdb-upload $db_name.sql
	printf "\033[34m* Upload finished.\n\033[0m\n"
}

echo "Do you want to do a MySQL dump of your database now? (Note: it will lock your tables)"
echo "Please select 1 or 2"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) mysql_dump; upload_dump; break;;
        No ) printf "\033[34m* Skipping MySQL dump...\n\033[0m\n"; break;;
    esac
done

# Metrics are submitted, echo some instructions and exit
printf "\033[32m
$app_name is running and functioning properly. It will continue to run in the
background.

If you ever want to stop the $app_name, run:

    sudo /etc/init.d/$app_name stop

And to run it again run:

    sudo /etc/init.d/$app_name start

\033[0m"
