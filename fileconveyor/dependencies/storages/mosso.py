"""
Custom storage for fileconveyor.dependencies.django with Mosso Cloud Files backend.
Created by Rich Leland <rich@richleland.com>.
"""
import re

from mimetypes import guess_type

from fileconveyor.dependencies.django.conf import settings
from fileconveyor.dependencies.django.core.files import File
from fileconveyor.dependencies.django.core.files.storage import Storage
from fileconveyor.dependencies.django.core.exceptions import ImproperlyConfigured
from fileconveyor.dependencies.django.utils.text import get_valid_filename


try:
    import cloudfiles
    from cloudfiles.errors import NoSuchObject
except ImportError:
    raise ImproperlyConfigured, "Could not load cloudfiles dependency. See http://www.mosso.com/cloudfiles.jsp."

"""
#Commented this to not assume variables in settings, instead get it from constructor
try:
    CLOUDFILES_USERNAME = settings.CLOUDFILES_USERNAME
    CLOUDFILES_API_KEY = settings.CLOUDFILES_API_KEY
    CLOUDFILES_CONTAINER = settings.CLOUDFILES_CONTAINER
except AttributeError:
    raise ImproperlyConfigured, "CLOUDFILES_USERNAME, CLOUDFILES_API_KEY, and CLOUDFILES_CONTAINER must be supplied in settings.py."
"""

# TODO: implement TTL into cloudfiles methods
CLOUDFILES_TTL = getattr(settings, 'CLOUDFILES_TTL', 600)


def cloudfiles_upload_to(self, filename):
    """
    Simple, custom upload_to because Cloud Files doesn't support
    nested containers (directories).
    
    Actually found this out from @minter:
    @richleland The Cloud Files APIs do support pseudo-subdirectories, by 
    creating zero-byte files with type application/directory.
    
    May implement in a future version.
    """
    return get_valid_filename(filename)


class CloudFilesStorage(Storage):
    """
    Custom storage for Mosso Cloud Files.
    """
    
    def __init__(self, username, api_key, container):
        """
        Here we set up the connection and select the user-supplied container.
        If the container isn't public (available on Limelight CDN), we make
        it a publicly available container.
        """
        self.connection = cloudfiles.get_connection(username,
                                                    api_key)
        self.container = self.connection.get_container(container)
        if not self.container.is_public():
            self.container.make_public()
    
    def _get_cloud_obj(self, name):
        """
        Helper function to get retrieve the requested Cloud Files Object.
        """
        return self.container.get_object(name)

    def _open(self, name, mode='rb'):
        """
        Not sure if this is the proper way to execute this. Would love input.
        """
        return File(self._get_cloud_obj(name).read())

    def _save(self, name, content):
        """
        Here we're opening the content object and saving it to the Cloud Files
        service. We have to set the content_type so it's delivered properly
        when requested via public URI.
        """
        content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        cloud_obj = self.container.create_object(name)
        cloud_obj.content_type = guess_type(name)[0] or "application/x-octet-stream"
        #cloud_obj.content_type = content.content_type
        cloud_obj.send(content_str)
        content.close()
        return name
    
    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        self.container.delete_object(name)

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        try:
            self._get_cloud_obj(name)
            return True
        except NoSuchObject:
            return False
        
    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        return ([], self.container.list_objects(path=path))

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        return self._get_cloud_obj(name).size()

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a web browser.
        """
        return self._get_cloud_obj(name).public_uri()
