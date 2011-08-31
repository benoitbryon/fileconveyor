import os, sys, time, traceback
import smtplib
from fileconveyor.dependencies.boto.utils import ShellCommand, get_ts
import boto
import fileconveyor.dependencies.boto.utils as fileconveyor.dependencies.boto.utils

class ScriptBase:

    def __init__(self, config_file=None):
        self.instance_id = boto.config.get('Instance', 'instance-id', 'default')
        self.name = self.__class__.__name__
        self.ts = get_ts()
        if config_file:
            boto.config.read(config_file)

    def notify(self, subject, body=''):
        fileconveyor.dependencies.boto.utils.notify(subject, body)

    def mkdir(self, path):
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except:
                boto.log.error('Error creating directory: %s' % path)

    def umount(self, path):
        if os.path.ismount(path):
            self.run('umount %s' % path)

    def run(self, command, notify=True, exit_on_error=False):
        self.last_command = ShellCommand(command)
        if self.last_command.status != 0:
            boto.log.error(self.last_command.output)
            if notify:
                self.notify('Error encountered', self.last_command.output)
            if exit_on_error:
                sys.exit(-1)
        return self.last_command.status

    def main(self):
        pass
        
