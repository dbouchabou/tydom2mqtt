import json
from logger import logger
import logging

logger = logging.getLogger(__name__)

sensor_config_topic = "homeassistant/sensor/tydom/{id}/{endpoint_id}/config"
sensor_topic = "homeassistant/sensor/tydom/{id}/{endpoint_id}/state"

#sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"
#sensor_topic = "homeassistant/sensor/tydom/{id}/state"


class Sensor_2:

    def __init__(self, 
                attr,
                mqtt = None) :

        self.attr = attr
        self.mqtt = mqtt

        self.sensor_topic = sensor_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.sensor_config_topic = sensor_config_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])

        #self.sensor_topic = sensor_topic.format(id = self.attr['device_id'])
        #self.sensor_config_topic = sensor_config_topic.format(id = self.attr['device_id'])

        self.device = {}
        self.device['manufacturer'] = self.attr['manufacturer']
        self.device['model'] = self.attr['model']
        self.device['name'] = self.attr['name']
        self.device['identifiers'] = self.attr['device_id']


        self.entity = {}
        self.entity['name'] = self.attr['entity_name']
        self.entity['object_id'] = "{}_{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['endpoint_id'],self.attr['entity_name'])
        self.entity['unique_id'] = "{}_{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['endpoint_id'],self.attr['entity_name'])

        if 'device_class' in self.attr.keys():
            self.entity['device_class'] = self.attr['device_class']

        if 'state_class' in self.attr.keys():
            self.entity['state_class'] = self.attr['state_class']
        
        if 'unit_of_measurement' in self.attr.keys():
            self.entity['unit_of_measurement'] = self.attr['unit_of_measurement']
        
        self.entity['device'] = self.device
        self.entity['state_topic'] = self.sensor_topic

    async def setup(self) :

        if (self.mqtt is not None) :

            logger.debug("SENSOR 2 : START SETUP ")

            self.mqtt.mqtt_client.publish(
                (self.sensor_config_topic).lower(), 
                json.dumps(self.entity), 
                qos=0, 
                retain=True)  # sensor Config

            logger.debug("SENSOR 2 : SETUP OK")

    async def update(self) :

        if (self.mqtt is not None) :

            await self.setup()  # Publish config

            logger.debug("SENSOR 2 : START UPDATE ")

            #if self.attr['is_binary'] :
            #    if self.attr['data_value'] == True :
            #        self.attr['data_value'] = 'ON'
            #    elif self.attr['data_value'] == False :
            #        self.attr['data_value'] = 'OFF'


            self.mqtt.mqtt_client.publish(
                self.sensor_topic,
                self.attr['data_value'],
                qos=0)  # sensor State
        
            logger.info(
                "Sensor created / updated : %s %s",
                self.entity['unique_id'],
                self.attr['data_value'])
