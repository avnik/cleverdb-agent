"Releasing the package" HOWTO
=============================

This process consist from two parts.
First part is required, and should be completed on developer machine,
second one should be done on repository host, and in near future will be
replaced by automatic tool.

## Adding changelog entry

First, you should set your name and email:

    export DEBEMAIL="Your Name  <email@host.com>"

I suggest use same email/name which you use at github for commits.
Next action:

    debchange -i

Then you should edit top entry, correcting version number if needed, and
fill entry with release information. For description of entry format, refer to
"Debian Packaging Manual" reference.

Then commit updated ``debian/changelog``.
(I suggest commit changelog separately from other changes, and use text
``Changelog updated`` as commit message.)

Then tag commit as  ``debian/version-in-changelog``.
(I suggest use ``git-buildpackage`` tool for tagging, but ordinary ``git tag``
would work as well).

## Upload package

NOTE: This part will be replaced with automated tool.

Build package, using  ``debuild binary`` command
(You can use local ubuntu machine, or vagrant, or docker). After that, you 
should transfer resulting ``*.deb`` file to repository host). Then issue 
following command:

    reprepro -b /srv/www/apt.cleverdb.io/  includedeb staging ~/cleverdb-agent_0.1_all.deb

(Substitute proper path and version).

NOTE: uploading user should be member of ``reprepro`` group.

Thats it.
