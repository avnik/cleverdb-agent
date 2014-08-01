from fabric.api import run


def deploy():
    run('reprepro -b /srv/www/apt.cleverdb.io/ includedeb staging '
        '/tmp/latest.deb')
