import logging

import thingspeak

module_logger = logging.getLogger("main.libutils")
log = logging.getLogger("main.libutils.Libutils")


class Libutils:
    def __init__(self):
        pass

    def set_channel(self, channel_id, write_key):
        self.channel = thingspeak.Channel(id=channel_id, api_key=write_key)

    def write_data(self, adc, dac):

        try:
            # write
            response = self.channel.update({"field1": adc, "field2": dac})
            log.info(f"Send ---> field1: {adc}, field2: {dac}")
            # read
            read = self.channel.get({})
            log.debug(f"Read: {read}")

        except Exception as e:
            log.info(e)
            log.info("connection failed")
