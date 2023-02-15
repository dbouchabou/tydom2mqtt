import json
from logger import logger
import logging


logger = logging.getLogger(__name__)

sensor_topic = "sensor/tydom/#"
sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"
sensor_json_attributes_topic = "sensor/tydom/{id}/state"

binary_sensor_topic = "binary_sensor/tydom/#"
binary_sensor_config_topic = "homeassistant/binary_sensor/tydom/{id}/config"
binary_sensor_json_attributes_topic = "binary_sensor/tydom/{id}/state"


class Plug:

    def __init__(self, tydom_attributes_payload, mqtt=None):

        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'EASY PLUG E16EM'
        self.device['name'] = tydom_attributes_payload['name']
        self.device['identifiers'] = tydom_attributes_payload['unique_id']

        self.config_sensor_topic = sensor_config_topic.format(id=self.id)

        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        try:
            self.config['device_class'] = self.device_class
        except AttributeError:
            pass
        try:
            self.config['state_class'] = self.state_class
        except AttributeError:
            pass
        try:
            self.config['unit_of_measurement'] = self.unit_of_measurement
        except AttributeError:
            pass
    
    async def setup(self):

        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'EASY PLUG E16EM'
        self.device['name'] = self.name
        self.device['identifiers'] = self.parent_device_id + '_sensors'

        self.config_sensor_topic = sensor_config_topic.format(id=self.id)

        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        try:
            self.config['device_class'] = self.device_class
        except AttributeError:
            pass
        try:
            self.config['state_class'] = self.state_class
        except AttributeError:
            pass
        try:
            self.config['unit_of_measurement'] = self.unit_of_measurement
        except AttributeError:
            pass


        if (self.mqtt is not None):
            self.mqtt.mqtt_client.publish(
                (self.config_topic).lower(), json.dumps(
                    self.config), qos=0, retain=True)

    async def update(self):

        # 3 items are necessary :
        # config to config config_sensor_topic + config payload is the schema
        # state payload to state topic in config with all attributes

        await self.setup()  # Publish config

        # Publish state json to state topic
        if (self.mqtt is not None):
            # logger.debug("%s %s", self.json_attributes_topic, self.attributes)
            # self.mqtt.mqtt_client.publish(self.json_attributes_topic,
            # self.attributes, qos=0) #sensor json State
            self.mqtt.mqtt_client.publish(
                self.json_attributes_topic,
                self.elem_value,
                qos=0)  # sensor State

        
            logger.info(
                "Sensor created / updated : %s %s",
                self.name,
                self.elem_value)
        