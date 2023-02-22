#!/usr/bin/env python3
import asyncio
import json
import os
import socket

from logger import _LOGGER
from mqtt_client import MQTT_Hassio
from tydomConnector import TydomWebSocketClient
from tydomMessagehandler import TydomMessageHandler

### DEFAULT VALUES
TYDOM_IP = "mediation.tydom.com"
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_SSL = False
TYDOM_ALARM_PIN = ""
TYDOM_ALARM_HOME_ZONE = 1
TYDOM_ALARM_NIGHT_ZONE = 2
TYDOM_ALARM_PIN = ""
TYDOM_MAC = ""
TYDOM_PASSWORD = ""
###

DATA_OPTIONS_PATH = "/data/options.json"

### GLOBALS
tydom_client = None
hassio = None


def load_config():
    config = {}
    try:
        with open(DATA_OPTIONS_PATH) as f:
            _LOGGER.info(
                f"{DATA_OPTIONS_PATH} detected ! Hassio Addons Environnement : parsing options.json...."
            )
            try:
                data = json.load(f)
                _LOGGER.debug(data)

                # CREDENTIALS TYDOM
                if "TYDOM_MAC" in data.keys():
                    config["TYDOM_MAC"] = data["TYDOM_MAC"]  # MAC Address of Tydom Box
                else:
                    _LOGGER.error("No Tydom MAC set")
                    exit()

                if "TYDOM_IP" in data.keys():
                    config["TYDOM_IP"] = data["TYDOM_IP"]

                if "TYDOM_PASSWORD" in data.keys():
                    config["TYDOM_PASSWORD"] = data["TYDOM_PASSWORD"]  # Tydom password
                else:
                    _LOGGER.error("No Tydom password set")
                    exit()

                if "TYDOM_ALARM_PIN" in data.keys():
                    config["TYDOM_ALARM_PIN"] = data["TYDOM_ALARM_PIN"]

                if "TYDOM_ALARM_HOME_ZONE" in data.keys():
                    config["TYDOM_ALARM_HOME_ZONE"] = data["TYDOM_ALARM_HOME_ZONE"]

                if "TYDOM_ALARM_NIGHT_ZONE" in data.keys():
                    config["TYDOM_ALARM_NIGHT_ZONE"] = data["TYDOM_ALARM_NIGHT_ZONE"]

                # CREDENTIALS MQTT
                if "MQTT_HOST" in data.keys():
                    config["MQTT_HOST"] = data["MQTT_HOST"]

                if "MQTT_USER" in data.keys():
                    config["MQTT_USER"] = data["MQTT_USER"]

                if "MQTT_PASSWORD" in data.keys():
                    config["MQTT_PASSWORD"] = data["MQTT_PASSWORD"]

                if "MQTT_PORT" in data.keys():
                    config["MQTT_PORT"] = data["MQTT_PORT"]

                if "MQTT_SSL" in data.keys():
                    if "MQTT_SSL" == "true":
                        config["MQTT_SSL"] = True
                    else:
                        config["MQTT_SSL"] = False

                if "log_level" in data.keys():
                    log_level = str(data["log_level"]).upper()

                    if log_level in [
                        "NOTSET",
                        "DEBUG",
                        "INFO",
                        "WARNING",
                        "ERROR",
                        "CRITICAL",
                    ]:
                        _LOGGER.setLevel(log_level)

                return config

            except Exception as e:
                _LOGGER.error("Parsing error %s", e)

    except FileNotFoundError:
        _LOGGER.info(f"No {DATA_OPTIONS_PATH}, seems we are not in hassio addon mode.")
        # CREDENTIALS TYDOM
        config["TYDOM_MAC"] = os.getenv("TYDOM_MAC")  # MAC Address of Tydom Box
        # Local ip address, default to mediation.tydom.com for remote connexion if
        # not specified
        config["TYDOM_IP"] = os.getenv("TYDOM_IP", "mediation.tydom.com")
        config["TYDOM_PASSWORD"] = os.getenv("TYDOM_PASSWORD")  # Tydom password
        config["TYDOM_ALARM_PIN"] = os.getenv("TYDOM_ALARM_PIN")
        config["TYDOM_ALARM_HOME_ZONE"] = os.getenv("TYDOM_ALARM_HOME_ZONE", 1)
        config["TYDOM_ALARM_NIGHT_ZONE"] = os.getenv("TYDOM_ALARM_NIGHT_ZONE", 2)

        # CREDENTIALS MQTT
        config["MQTT_HOST"] = os.getenv("MQTT_HOST", "localhost")
        config["MQTT_USER"] = os.getenv("MQTT_USER", "")
        config["MQTT_PASSWORD"] = os.getenv("MQTT_PASSWORD", "")

        # 1883 #1884 for websocket without SSL
        config["MQTT_PORT"] = os.getenv("MQTT_PORT", 1883)
        config["MQTT_SSL"] = os.getenv("MQTT_SSL", False)


def loop_task():
    _LOGGER.info("Starting main loop_task")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hassio.connect())
    loop.run_until_complete(listen_tydom_forever())


async def message_handler(message):
    try:
        handler = TydomMessageHandler(
            incoming_bytes=message,
            tydom_client=tydom_client,
            mqtt_client=hassio,
        )
        await handler.incomingTriage()
    except Exception as e:
        _LOGGER.error("Tydom Message Handler exception : %s", e)


async def tydom_listener():
    # listener loop
    while True:
        _LOGGER.info("Start Listen TYDOM Data")
        # Wainting for income message from the websocket
        message = await tydom_client.connection.recv()
        _LOGGER.debug("<<<<<<<<<< Receiving from tydom_client...")
        _LOGGER.debug(message)

        _LOGGER.debug("Server said > %s".format(message))

        await message_handler(message)

        # await asyncio.sleep(0)


async def listen_tydom_forever():
    """
    Connect, then receive all server messages and pipe them to the handler, and reconnects if needed
    """

    while True:
        # # outer loop restarted every time the connection fails
        try:
            await tydom_client.connect()
            _LOGGER.info("Tydom Client is connected to websocket and ready !")
            await tydom_client.setup()

            await tydom_listener()

        except socket.gaierror:
            _LOGGER.info(
                "Socket error - retrying connection in %s sec (Ctrl-C to quit)".format(
                    tydom_client.sleep_time
                )
            )
            await asyncio.sleep(tydom_client.sleep_time)
            continue
        except ConnectionRefusedError:
            _LOGGER.error(
                "Nobody seems to listen to this endpoint. Please check the URL."
            )
            _LOGGER.error(
                "Retrying connection in %s sec (Ctrl-C to quit)".format(
                    tydom_client.sleep_time
                )
            )
            await asyncio.sleep(tydom_client.sleep_time)
            continue

        await asyncio.sleep(0)


if __name__ == "__main__":
    _LOGGER.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    _LOGGER.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    _LOGGER.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    _LOGGER.info("STARTING TYDOM2MQTT")

    _LOGGER.info("Detecting environnement......")

    config = load_config()

    tydom_client = TydomWebSocketClient(
        mac=config["TYDOM_MAC"],
        host=config["TYDOM_IP"],
        password=config["TYDOM_PASSWORD"],
        alarm_pin=config["TYDOM_ALARM_PIN"],
    )

    hassio = MQTT_Hassio(
        broker_host=config["MQTT_HOST"],
        port=config["MQTT_PORT"],
        user=config["MQTT_USER"],
        password=config["MQTT_PASSWORD"],
        mqtt_ssl=config["MQTT_SSL"],
        home_zone=config["TYDOM_ALARM_HOME_ZONE"],
        night_zone=config["TYDOM_ALARM_NIGHT_ZONE"],
        tydom=tydom_client,
    )

    loop_task()
