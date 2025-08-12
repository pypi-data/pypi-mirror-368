import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import unittest
import random
from siem_hkm_ai_smartcore.interfaces.bacnet_comm.BACnet_device import BAC0DeviceManager 

class Test_BACnet_device_local(unittest.TestCase):

    def test_BACnet_device_local(self):
        
        async def run_init():
            test_device = BAC0DeviceManager()
            await test_device.add_local_numeric_point("ana_point",123)
            value = await test_device.get_local_point_value("ana_point")
            self.assertEqual(value,123)
            
            await test_device.add_local_bool_point("bool_point",True)
            value = await test_device.get_local_point_value("bool_point")
            self.assertEqual(value,True)
            
            
            await test_device.close_all()
        asyncio.run(run_init())
    



        
unittest.main()