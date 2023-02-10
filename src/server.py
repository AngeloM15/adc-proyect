import thingspeak

from tools.config import Api


class ThingSpeak:
    def __init__(self):
        self.channel = self.set_channel()

    def set_channel(self):
        channel = thingspeak.Channel(id=Api.channel, api_key=Api.k_write)
        return channel

    def write_data(self, adc, dac):

        try:
            # write
            response = self.channel.update({"field1": adc, "field2": dac})
            # log.info(f"Send ---> field1: {adc}, field2: {dac}")
            # read
            read = self.channel.get({})
            # log.debug(f"Read: {read}")

        except Exception as e:
            pass
            # log.info(e)
            # log.info("connection failed")
