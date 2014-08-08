from fabric.api import run


def deploy(repo_env="stable"):
    run('reprepro -b /srv/www/apt.cleverdb.io/ --ignore=wrongdistribution '
        'includedeb {} '
        '/tmp/latest.deb'.format(repo_env))
