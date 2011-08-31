# Copyright (c) 2006-2008 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Represents an EC2 Elastic IP Address
"""

from fileconveyor.dependencies.boto.ec2.ec2object import EC2Object

class Address(EC2Object):
    
    def __init__(self, connection=None, public_ip=None, instance_id=None):
        EC2Object.__init__(self, connection)
        self.connection = connection
        self.public_ip = public_ip
        self.instance_id = instance_id

    def __repr__(self):
        return 'Address:%s' % self.public_ip

    def endElement(self, name, value, connection):
        if name == 'publicIp':
            self.public_ip = value
        elif name == 'instanceId':
            self.instance_id = value
        else:
            setattr(self, name, value)

    def delete(self):
        return self.connection.delete_address(self.public_ip)



