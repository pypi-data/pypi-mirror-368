from dataclasses import dataclass, field
from typing import Optional
import socket
import asyncio
import pandas as pd
import BAC0
import socket
from bacpypes3.basetypes import BinaryPV
from BAC0.core.devices.local.factory import (
    ObjectFactory,
    analog_input,
    analog_value,
    binary_input,
    binary_output,
    binary_value,
    character_string,
    date_value,
    datetime_value,
    make_state_text,
    multistate_input,
    multistate_output,
    multistate_value,
)
from BAC0.scripts.script_runner import run
class BAC0DeviceManager:
    def __init__(self, local_ip="192.168.56.1/24", local_device_id=102, 
                 local_port=47809, local_obj_name="App1"):
        self.local_ip = local_ip
        self.local_device_id = local_device_id
        self.local_port = local_port
        self.local_obj_name = local_obj_name
        self.test_device_dict = {}
        self.device_app = None
        self.device_app = BAC0.start(
            ip=self.local_ip,
            deviceId=self.local_device_id,
            port=self.local_port,
            localObjName=self.local_obj_name
        )
    
    async def add_local_numeric_point(self, point_name, value): 
        ObjectFactory.clear_objects() 
        analog_obj1 = analog_value(name=point_name, presentValue=value)
        analog_obj1.add_objects_to_application(self.device_app)

    async def add_local_bool_point(self, point_name, value): 
        ObjectFactory.clear_objects() 
        bool_obj1 = binary_value(name=point_name, presentValue=value)
        bool_obj1.add_objects_to_application(self.device_app)
    
    async def remove_local_point(self, point_name):
        if not self.device_app:
            raise RuntimeError("please connect first")

        obj = self.device_app.get_object_by_name(point_name)
        if obj:
            self.device_app.remove_object(obj)
            return True
        return False

    async def add_remote_numeric_point(self, device_id, point_name, value):
        ObjectFactory.clear_objects()
        analog_obj1 = analog_value(name=point_name, presentValue=value)
        analog_obj1.add_objects_to_application(self.test_device_dict[device_id])

    async def connect(self, remote_ip="192.168.1.1:47808", remote_device_id=7100, poll_interval=10): 
        test_device_dict = await BAC0.device(
            remote_ip, 
            remote_device_id, 
            self.device_app, 
            poll=poll_interval
        )
        self.test_devic[remote_device_id] = test_device_dict
    async def set_local_point_value(self,pointname, value):
        if not self.device_app:
            raise RuntimeError("please connect first")
            
        await self.device_app[f"{pointname}"].write_property('presentValue', value)
        return await self.device_app[f"{pointname}"].read_property("presentValue")  
    async def get_local_point_value(self,pointname):
        if not self.device_app:
            raise RuntimeError("please connect first")
        return await self.device_app[f"{pointname}"].read_property("presentValue")    
    async def get_remote_point_value(self,device_id,pointname):
        
        if not self.test_device_dict:
            raise RuntimeError("please connect first")
            
        return await self.test_device_dict[device_id][f"{pointname}"].read_property("presentValue")
    
    async def set_remote_update_value(self,device_id,pointname, value):
        
        if not self.test_device_dict:
            raise RuntimeError("please connect first")
            
        self.test_device_dict[device_id][f"{pointname}"] = value
        return value
    
    async def close(self,device_id):
        if self.device_app[device_id]:
            await self.device_app[device_id].stop()
            self.device_app[device_id] = None
            self.test_device_dict = None
    
    async def close_all(self):
        for device_id in self.test_device_dict.keys():
            self.close(device_id)
        if self.device_app is not None:
            self.device_app.disconnect()
            self.device_app = None
        await asyncio.sleep(0.1)
            

    