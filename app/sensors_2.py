import json
from logger import logger
import logging

logger = logging.getLogger(__name__)

sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"
sensor_topic = "homeassistant/sensor/tydom/{id}/state"


class Sensor:

    def __init__(self, 
                attr,
                mqtt = None,
                binary = False) :

        self.attr = attr
        self.mqtt = mqtt
        self.is_binary_sensor = binary

        self.sensor_topic = sensor_topic.format(id = self.attr['device_id'])
        self.sensor_config_topic = sensor_config_topic.format(id = self.attr['device_id'])

        self.device = {}
        self.device['manufacturer'] = self.attr['manufacturer']
        self.device['model'] = self.attr['model']
        self.device['name'] = self.attr['name']
        self.device['identifiers'] = self.attr['device_id']


        self.entity = {}
        self.entity['name'] = self.attr['entity_name']
        self.entity['unique_id'] = "sensor.{}_{}.{}".format(self.attr['name'],self.attr['device_id'],self.attr['data_name'])
        self.entity['object_id'] = "sensor.{}_{}.{}".format(self.attr['name'],self.attr['device_id'],self.attr['data_name'])
        self.entity['device_class'] = self.attr['device_class']
        self.entity['state_class'] = self.attr['state_class']
        self.entity['unit_of_measurement'] = self.attr['unit_of_measurement']
        self.entity['device'] = self.device
        self.entity['state_topic'] = self.sensor_topic

    async def setup(self):
        if (self.mqtt is not None) :
            self.mqtt.mqtt_client.publish(
                (self.sensor_config_topic).lower(), 
                json.dumps(self.entity), 
                qos=0, 
                retain=True)  # sensor Config

    async def update(self) :

        if (self.mqtt is not None) :

            await self.setup()  # Publish config

            if self.is_binary_sensor :
                if self.attr['data_value'] == True :
                    self.attr['data_value'] = 'ON'
                elif self.attr['data_value'] == False :
                    self.attr['data_value'] = 'OFF'


            self.mqtt.mqtt_client.publish(
                self.sensor_topic,
                self.attr['data_value'],
                qos=0)  # sensor State
        
            logger.info(
                "Sensor created / updated : %s %s",
                self.entity['unique_id'],
                self.attr['data_value'])
