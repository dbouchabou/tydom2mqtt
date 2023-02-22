import json

from logger import _LOGGER
from sensors import sensor

cover_command_topic = "cover/tydom/{id}/set_positionCmd"
cover_config_topic = "homeassistant/cover/tydom/{id}/config"
cover_position_topic = "cover/tydom/{id}/current_position"
cover_tilt_topic = "cover/tydom/{id}/current_tilt"
cover_set_position_topic = "cover/tydom/{id}/set_position"
cover_set_tilt_topic = "cover/tydom/{id}/set_tilt"
cover_attributes_topic = "cover/tydom/{id}/attributes"


class Cover:
    def __init__(self, tydom_attributes, set_position=None, mqtt=None):
        self.attributes = tydom_attributes
        self.device_id = self.attributes["device_id"]
        self.endpoint_id = self.attributes["endpoint_id"]
        self.id = self.attributes["id"]
        self.name = self.attributes["cover_name"]
        self.set_position = set_position

        if "position" in tydom_attributes:
            self.current_position = self.attributes["position"]

        if "tilt" in tydom_attributes:
            self.current_tilt = self.attributes["tilt"]

        self.mqtt = mqtt

    # def id(self):
    #     return self.id

    # def name(self):
    #     return self.name

    # def current_position(self):
    #     return self.current_position

    # def set_position(self):
    #     return self.set_position

    # def attributes(self):
    #     return self.attributes

    async def setup(self):
        self.device = {}
        self.device["manufacturer"] = "Delta Dore"
        self.device["model"] = "Volet"
        self.device["name"] = self.name
        self.device["identifiers"] = self.id

        self.config_topic = cover_config_topic.format(id=self.id)
        self.config = {}
        self.config["name"] = self.name
        self.config["unique_id"] = self.id
        self.config["command_topic"] = cover_command_topic.format(id=self.id)
        self.config["set_position_topic"] = cover_set_position_topic.format(id=self.id)
        self.config["position_topic"] = cover_position_topic.format(id=self.id)

        if "tilt" in self.attributes:
            self.config["tilt_command_topic"] = cover_set_tilt_topic.format(id=self.id)
            self.config["tilt_status_topic"] = cover_tilt_topic.format(id=self.id)

        self.config["json_attributes_topic"] = cover_attributes_topic.format(id=self.id)

        self.config["payload_open"] = "UP"
        self.config["payload_close"] = "DOWN"
        self.config["payload_stop"] = "STOP"
        self.config["retain"] = "false"
        self.config["device"] = self.device
        self.config["device_class"] = "shutter"

        if self.mqtt is not None:
            self.mqtt.mqtt_client.publish(
                self.config_topic, json.dumps(self.config), qos=0
            )
        # setup_pub = '(self.config_topic, json.dumps(self.config), qos=0)'
        # return(setup_pub)

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            _LOGGER.error("Cover sensors Error :")
            _LOGGER.error(e)

        if self.mqtt is not None and "position" in self.attributes:
            self.mqtt.mqtt_client.publish(
                self.config["position_topic"], self.current_position, qos=0
            )

        if self.mqtt is not None and "tilt" in self.attributes:
            self.mqtt.mqtt_client.publish(
                self.config["tilt_status_topic"], self.current_tilt, qos=0
            )

        if self.mqtt is not None:
            # self.mqtt.mqtt_client.publish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
            self.mqtt.mqtt_client.publish(
                self.config["json_attributes_topic"], self.attributes, qos=0
            )

        _LOGGER.info("Cover created / updated : %s %s", self.name, self.id)

        # update_pub = '(self.position_topic, self.current_position, qos=0, retain=True)'
        # return(update_pub)

    async def update_sensors(self):
        # _LOGGER.debug('test sensors !')
        for i, j in self.attributes.items():
            # sensor_name = "tydom_alarm_sensor_"+i
            # _LOGGER.debug("name %s elem_name %s attributes_topic_from_device %s mqtt %s"+sensor_name, i, self.config['json_attributes_topic'], self.mqtt)
            if not i == "device_type" or not i == "id":
                new_sensor = None
                new_sensor = sensor(
                    elem_name=i,
                    tydom_attributes_payload=self.attributes,
                    attributes_topic_from_device=self.config["json_attributes_topic"],
                    mqtt=self.mqtt,
                )
                await new_sensor.update()

    # def __init__(self, name, elem_name, tydom_attributes_payload,
    # attributes_topic_from_device, mqtt=None):

    async def put_position(tydom_client, device_id, cover_id, position):
        _LOGGER.info("%s %s %s", cover_id, "position", position)
        if not (position == ""):
            await tydom_client.put_devices_data(
                device_id, cover_id, "position", position
            )

    async def put_tilt(tydom_client, device_id, cover_id, tilt):
        _LOGGER.info("%s %s %s", cover_id, "tilt", tilt)
        if not (tilt == ""):
            await tydom_client.put_devices_data(device_id, cover_id, "slope", tilt)

    async def put_positionCmd(tydom_client, device_id, cover_id, positionCmd):
        _LOGGER.info("%s %s %s", cover_id, "positionCmd", positionCmd)
        if not (positionCmd == ""):
            await tydom_client.put_devices_data(
                device_id, cover_id, "positionCmd", positionCmd
            )
