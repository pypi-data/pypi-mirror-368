from os import makedirs
from os.path import join, exists

from cubicweb.server import hook
from cubicweb.server.sources import storages


class ServerStartupHook(hook.Hook):
    __regid__ = "drh.serverstartup"
    events = ("server_startup", "server_maintenance")

    def __call__(self):
        bfssdir = join(self.repo.config.appdatahome, "bfss")
        if not exists(bfssdir):
            makedirs(bfssdir)
            print("created", bfssdir)
        storage = storages.BytesFileSystemStorage(bfssdir)
        storages.set_attribute_storage(self.repo, "File", "data", storage)
