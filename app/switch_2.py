import json
from sensors import sensor
from logger import logger
import logging

logger = logging.getLogger(__name__)
switch_config_topic = "homeassistant/switch/tydom/{id}/config"
switch_state_topic = "homeassistant/switch/tydom/{id}/state"
switch_attributes_topic = "homeassistant/switch/tydom/{id}/attributes"
switch_command_topic = "homeassistant/switch/tydom/{id}/{cmd}"


class Switch_2:
    def __init__(self, 
                attr,
                mqtt = None) :

        self.attr = attr
        self.mqtt = mqtt

        self.switch_config_topic = switch_config_topic.format(id = self.attr['device_id'])
        self.switch_state_topic = switch_state_topic.format(id = self.attr['device_id'])
        self.switch_attributes_topic = switch_attributes_topic.format(id = self.attr['device_id'])
        self.switch_command_topic = switch_command_topic.format(id = self.attr['device_id'], cmd = self.attr['data_name'])
        

        self.device = {}
        self.device['manufacturer'] = self.attr['manufacturer']
        self.device['model'] = self.attr['model']
        self.device['name'] = self.attr['name']
        self.device['identifiers'] = self.attr['device_id']


        self.entity = {}
        self.entity['name'] = self.attr['entity_name']
        self.entity['object_id'] = "{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['entity_name'])
        self.entity['unique_id'] = "{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['entity_name'])
        self.entity['device'] = self.device
        self.entity['state_topic'] = self.switch_state_topic
        self.entity['command_topic'] = self.switch_command_topic

    async def setup(self) :

        if (self.mqtt is not None) :
            self.mqtt.mqtt_client.publish(
                (self.switch_config_topic).lower(), 
                json.dumps(self.entity), 
                qos=0, 
                retain=True)  # sensor Config

    async def update(self) :

        if (self.mqtt is not None) :

            await self.setup()  # Publish config


            self.mqtt.mqtt_client.publish(
                self.switch_state_topic,
                self.attr['data_value'],
                qos=0,
                retain=True)  # Switch State
        
            logger.info(
                "Sensor created / updated : %s %s",
                self.entity['unique_id'],
                self.attr['data_value'])
    
    @staticmethod
    async def send(tydom_client, device_id, endpoint_id, name, value) :
        logger.info("%s %s %s", device_id, name, value)
        if not (value == '') :
            await tydom_client.put_devices_data(device_id, endpoint_id, name, value)
