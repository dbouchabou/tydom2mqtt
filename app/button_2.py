import json
from sensors import sensor
from logger import logger
import logging

logger = logging.getLogger(__name__)
button_config_topic = "homeassistant/button/tydom/{id}_{endpoint_id}/config"
button_attributes_topic = "homeassistant/button/tydom/{id}/{endpoint_id}/attributes"
button_command_topic = "homeassistant/button/tydom/{id}/{endpoint_id}/btncmd"


class Button_2:
    def __init__(self, 
                attr,
                mqtt = None) :

        self.attr = attr
        self.mqtt = mqtt

        self.button_config_topic = button_config_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.button_attributes_topic = button_attributes_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.button_command_topic = button_command_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        

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
        self.entity['command_topic'] = self.button_command_topic
        

        if 'payload_on' in self.attr.keys():
            self.entity['payload_press'] = self.attr['payload_press']
        else :
            self.entity['payload_press'] = attr['data_value']

    async def setup(self) :

        if (self.mqtt is not None) :

            logger.debug("BUTTON 2 : START SETUP ")

            self.mqtt.mqtt_client.publish(
                (self.button_config_topic).lower(), 
                json.dumps(self.entity), 
                qos=0, 
                retain=True)  # sensor Config

            logger.debug("BUTTON SENSOR 2 : SETUP OK")

    async def update(self) :

        if (self.mqtt is not None) :

            await self.setup()  # Publish config

            logger.debug("BUTTON 2 : START UPDATE ")

            try:
                self.mqtt.mqtt_client.publish(
                    self.button_command_topic,
                    "TOGGLE",
                    qos=0)  # Button State
            except Exception as e:
                logger.error("on subscribe ERROR : %s", e)
        
            logger.info(
                "Sensor created / updated : %s %s",
                self.entity['unique_id'],
                self.attr['data_value'])
