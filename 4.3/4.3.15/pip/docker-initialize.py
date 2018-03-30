#!/usr/local/bin/python

import re
import os
import warnings
warnings.simplefilter('always', DeprecationWarning)

class Environment(object):
    """ Configure container via environment variables
    """
    def __init__(self, env=os.environ,
                 zope_conf="/plone/instance/etc/zope.conf",
                 zeopack_conf="/plone/instance/bin/zeopack",
                 zeoserver_conf="/plone/instance/etc/zeo.conf"
                 ):
        self.env = env
        self.zope_conf = zope_conf
        self.zeopack_conf = zeopack_conf
        self.zeoserver_conf = zeoserver_conf

    def effective_user(self):
        with open(self.zope_conf, 'r') as cfile:
            config = cfile.read()

        pattern = re.compile(r"^#\s+effective-user.+$")
        config = re.sub(pattern, EFFECTIVEUSER_TEMPLATE, config)

        with open(self.zope_conf, "w") as cfile:
            cfile.write(config)

    def auto_include(self):
        with open(self.zope_conf, 'r') as cfile:
            config = cfile.read()

        pattern = re.compile(r"#    <environment>.*</environment>", re.DOTALL)
        config = re.sub(pattern, AUTOINCLUDE_TEMPLATE, config)

        with open(self.zope_conf, "w") as cfile:
            cfile.write(config)

    def blob_storage(self):
        with open(self.zope_conf, 'r') as cfile:
            config = cfile.read()

        pattern = re.compile(r"<zodb_db main>.*</zodb_db>", re.DOTALL)
        config = re.sub(pattern, BLOBSTORAGE_TEMPLATE, config)

        with open(self.zope_conf, "w") as cfile:
            cfile.write(config)

    def setup(self, **kwargs):
        self.effective_user()
        self.auto_include()
        self.blob_storage()

    __call__ = setup


EFFECTIVEUSER_TEMPLATE="""
effective-user = plone
"""

AUTOINCLUDE_TEMPLATE="""
<environment>
  Z3C_AUTOINCLUDE_DEPENDENCIES_DISABLED on
</environment>
"""

BLOBSTORAGE_TEMPLATE="""
<zodb_db main>
  cache-size 40000
  mount-point /

  <blobstorage>
    blob-dir /data/blobstorage

    <filestorage>
      path /data/filestorage/Data.fs
    </filestorage>
  </blobstorage>
</zodb_db>
"""

def initialize():
    """ Configure Plone instance as ZEO Client
    """
    environment = Environment()
    environment.setup()

if __name__ == "__main__":
    initialize()
