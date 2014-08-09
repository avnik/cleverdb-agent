from fabric.api import run


def deploy_staging():
    run('reprepro -b /srv/www/apt.cleverdb.io/ --ignore=wrongdistribution '
        'includedeb {} '
        '/tmp/latest.deb'.format('staging'))


def deploy_production():
    run('reprepro -b /srv/www/apt.cleverdb.io/ copy stable staging '
        'cleverdb-agent')
