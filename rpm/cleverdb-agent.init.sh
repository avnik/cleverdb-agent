#!/bin/sh
#
# Cleverdb agent
###################################

# LSB header

### BEGIN INIT INFO
# Provides:          cleverdb-agent
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Cleverdb agent daemon
# Description:       This is a daemon that open tunnels for cleverdb
### END INIT INFO


# chkconfig header

# chkconfig: 345 96 05
# description:  This is a daemon that open tunnels for cleverdb
#
# processname: /usr/bin/cleverdb-agent


DEBIAN_VERSION=/etc/debian_version
SUSE_RELEASE=/etc/SuSE-release
# Source function library.
if [ -f $DEBIAN_VERSION ]; then
   exit 1
elif [ -f $SUSE_RELEASE -a -r /etc/rc.status ]; then
    . /etc/rc.status
else
    . /etc/rc.d/init.d/functions
fi

# Default values (can be overridden below)
CLEVERDB_AGENT=/usr/bin/cleverdb-agent
PYTHON=/usr/bin/python
AGENT_ARGS=""

if [ -f /etc/default/cleverdb-agent ]; then
    . /etc/default/cleverdb-agent
fi

SERVICE=cleverdb-agent
PROCESS=cleverdb-agent

RETVAL=0

start() {
    echo -n $"Starting salt-master daemon: "
    if [ -f $SUSE_RELEASE ]; then
        startproc -f -p /var/run/$SERVICE.pid $CLEVERDB_AGENT -d $AGENT_ARGS
        rc_status -v
    else
        daemon --check $SERVICE $CLEVERDB_AGENT -d $AGENT_ARGS
    fi
    RETVAL=$?
    echo
    return $RETVAL
}

stop() {
    echo -n $"Stopping salt-master daemon: "
    if [ -f $SUSE_RELEASE ]; then
        killproc -TERM $CLEVERDB_AGENT
        rc_status -v
    else
        killproc $PROCESS
    fi
    RETVAL=$?
    echo
}

restart() {
   stop
   start
}

# See how we were called.
case "$1" in
    start|stop|restart)
        $1
        ;;
    status)
        if [ -f $SUSE_RELEASE ]; then
            echo -n "Checking for service $SERVICE "
            checkproc $CLEVERDB_AGENT
            rc_status -v
        else
            status $PROCESS
            RETVAL=$?
        fi
        ;;
    condrestart)
        [ -f $LOCKFILE ] && restart || :
        ;;
    reload)
        echo "can't reload configuration, you have to restart it"
        RETVAL=$?
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|condrestart|reload}"
        exit 1
        ;;
esac
exit $RETVAL
