import json
from sensors import sensor
from logger import logger
import logging

logger = logging.getLogger(__name__)
light_config_topic = "homeassistant/light/tydom/{id}_{endpoint_id}/config"
light_state_topic = "homeassistant/light/tydom/{id}/{endpoint_id}/state"
light_attributes_topic = "homeassistant/light/tydom/{id}/{endpoint_id}/attributes"
light_command_topic = "homeassistant/light/tydom/{id}/{endpoint_id}/command/{cmd}"

#light_config_topic = "homeassistant/light/tydom/{id}/config"
#light_state_topic = "homeassistant/light/tydom/{id}/state"
#light_attributes_topic = "homeassistant/light/tydom/{id}/attributes"
#light_command_topic = "homeassistant/light/tydom/{id}/{cmd}"


class Light_2:
    def __init__(self, 
                attr,
                mqtt = None) :

        self.attr = attr
        self.mqtt = mqtt

        # Define The command
        if 'cmd_label' in self.attr.keys():
            cmd_label = self.attr['cmd_label']
        else:
            cmd_label = self.attr['data_name']

        self.light_config_topic = light_config_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.light_state_topic = light_state_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.light_attributes_topic = light_attributes_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'])
        self.light_command_topic = light_command_topic.format(id = self.attr['device_id'], endpoint_id = self.attr['endpoint_id'], cmd = cmd_label)

        #self.light_config_topic = light_config_topic.format(id = self.attr['device_id'])
        #self.light_state_topic = light_state_topic.format(id = self.attr['device_id'])
        #self.light_attributes_topic = light_attributes_topic.format(id = self.attr['device_id'])
        #self.light_command_topic = light_command_topic.format(id = self.attr['device_id'], cmd = self.attr['data_name'])
        

        self.device = {}
        self.device['manufacturer'] = self.attr['manufacturer']
        self.device['model'] = self.attr['model']
        self.device['name'] = self.attr['name']
        self.device['identifiers'] = self.attr['device_id']


        self.entity = {}
        self.entity['name'] = self.attr['entity_name']
        self.entity['object_id'] = "{}_{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['endpoint_id'],self.attr['entity_name'])
        self.entity['unique_id'] = "{}_{}_{}_{}".format(self.attr['name'],self.attr['device_id'],self.attr['endpoint_id'],self.attr['entity_name'])
        self.entity['device'] = self.device
        self.entity['state_topic'] = self.light_state_topic
        self.entity['command_topic'] = self.light_command_topic
        self.entity['brightness_scale'] = 100

    async def setup(self) :

        if (self.mqtt is not None) :
            logger.debug("LIGHT 2 : START SETUP ")
            self.mqtt.mqtt_client.publish(
                (self.light_config_topic).lower(), 
                json.dumps(self.entity), 
                qos=0, 
                retain=True)  # sensor Config
            
            logger.debug("LIGHT 2 : SETUP OK")

    async def update(self) :

        if (self.mqtt is not None) :

            await self.setup()  # Publish config

            logger.debug("LIGHT 2 : START UPDATE ")

            self.mqtt.mqtt_client.publish(
                self.light_state_topic,
                self.attr['data_value'],
                qos=0,
                retain=True)  # light State
        
            logger.info(
                "Sensor created / updated : %s %s",
                self.entity['unique_id'],
                self.attr['data_value'])
    
    @staticmethod
    async def send(tydom_client, device_id, endpoint_id, name, value) :
        logger.info("%s %s %s", device_id, name, value)
        if not (value == '') :
            await tydom_client.put_devices_data(device_id, endpoint_id, name, value)
