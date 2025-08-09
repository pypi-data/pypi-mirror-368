
"""
   Copyright 2021 Dustin Roeder (dmroeder@gmail.com)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

"""
TODO:
* better error handling
* figure out how to better close connections
* test with other adapter data types and configurations
* implement other features like reply to module properties
* check sequence counter to make sure it changed
* test processor slot
"""
import random
import socket
import sys
import threading
import time

from .lgx_response import Response
from .lgx_type import CIPTypes
from struct import pack, unpack_from

# CommFormat = {0:"Data - DINT",
#               1:"Data - DINT - With Status",
#               2:"Data - INT",
#               3:"Data - INT - With Status",
#               4:"Data - REAL",
#               5:"Data - REAL - With Status",
#               6:"Data - SINT",
#               7:"Data - SINT - With Status",
#               8:"Input Data - DINT",
#               9:"Input Data - DINT - Run/Program",
#               10:"Input Data - DINT - With Status",
#               11:"Input Data - INT",
#               12:"Input Data - INT - Run/Program",
#               13:"Input Data - INT - With Status",
#               14:"Input Data - REAL",
#               15:"Input Data - REAL - With Status",
#               16:"Input Data - SINT",
#               17:"Input Data - SINT - Run/Program",
#               18:"Input Data - SINT - With Status",
#               19:"None"}

class Adapter(object):

    def __init__(self, plc_ip="", local_ip="", callback=None):
        super(Adapter, self).__init__()
        """
        Initialize our parameters
        """
        self.PLCIPAddress = plc_ip
        self.LocalIPAddress = local_ip
        self.ProcessorSlot = 0

        self.CommFormat = 0
        self.DataType = 0x00
        self.InputSize = 0
        self.OutputSize = 0
        self.InputStatusSize = 0
        self.Callback = callback
        self.RunMode = None

        self.InputData = []
        self.OutputData = []
        self.InputStatusData = []
        self.OutputStatusData = 0

        self._rpi = 0
        self._server = None
        self._listener = None
        self._runnable = True
        self._responders = {}

        self._connections = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clean up on exit
        """
        print("exiting")
        self.Stop()
        return self

    def Start(self):
        self.InputData = [0 for i in range(self.InputSize)]
        self.OutputData = [0 for i in range(self.OutputSize)]
        self.InputStatusData = [0 for i in range(self.InputStatusSize)]
        self._server = CommunicationServer(self)
        self._listener = Listener(self)

    def Stop(self):
        """
        Shut down
        Do something better here
        """
        self._runnable = False
        sys.exit(0)
