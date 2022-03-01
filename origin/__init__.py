import json
from simplejson import errors as simplejsonerrors


class Plugin_OBJ():

    def __init__(self, plugin_utils):
        self.plugin_utils = plugin_utils

        self.base_api_url = "https://ott-gateway-stirr.sinclairstoryline.com/api/rest/v3"
        self.base_station_url = "https://ott-stationselection.sinclairstoryline.com/stationSelectionByAllStates"

    def get_channels(self):

        channel_list = []

        channel_ids = []

        station_locations = ["national", "abc3340"]

        station_by_state_opn = self.plugin_utils.web.session.get(self.base_station_url)
        try:
            states_list = station_by_state_opn.json()
        except json.JSONDecodeError as err:
            self.plugin_utils.logger.error("Channel Gathering Failed" % err)
            return []
        except simplejsonerrors.JSONDecodeError as err:
            self.plugin_utils.logger.error("Channel Gathering Failed" % err)
            return []

        for state_uuid in states_list['page']:
            if state_uuid["pageComponentUuid"].startswith("nearyou-"):
                state_url = state_uuid["content"]

                state_url_req = self.plugin_utils.web.session.get(state_url)
                state_url_json = state_url_req.json()
                for item in state_url_json["rss"]["channel"]["pagecomponent"]["component"]:
                    stationitem = item["item"]["media:content"]['sinclair:action_value']
                    if stationitem not in station_locations:
                        station_locations.append(stationitem)

        for station_item in station_locations:

            chan_list_url = "%s/channels/stirr?station=%s" % (self.base_api_url, station_item)
            chan_list_urlopn = self.plugin_utils.web.session.get(chan_list_url)

            try:
                stirr_chan_list = chan_list_urlopn.json()
            except json.JSONDecodeError as err:
                stirr_chan_list = None
                self.plugin_utils.logger.error("Channel Gathering Failed: %s" % err)
            except simplejsonerrors.JSONDecodeError as err:
                stirr_chan_list = None
                self.plugin_utils.logger.error("Channel Gathering Failed: %s" % err)

            if stirr_chan_list:

                for channel_dict in stirr_chan_list["channel"]:

                    if str(channel_dict["id"]) not in channel_ids:

                        chan_item_url = "%s/status/%s" % (self.base_api_url, str(channel_dict["id"]))
                        chan_item_urlopn = self.plugin_utils.web.session.get(chan_item_url)
                        try:
                            stirr_chan_item = chan_item_urlopn.json()
                        except json.JSONDecodeError:
                            stirr_chan_item = None
                        except simplejsonerrors.JSONDecodeError:
                            stirr_chan_item = None

                        if stirr_chan_item:

                            channel_ids.append(str(channel_dict["id"]))

                            try:
                                thumbnail = channel_dict["icon"]["src"].split("?")[0]
                            except TypeError:
                                thumbnail = None

                            clean_station_item = {
                                                 "name": stirr_chan_item['rss']["channel"]["title"],
                                                 "callsign": channel_dict["display-name"],
                                                 "id": str(channel_dict["id"]),
                                                 "thumbnail": thumbnail
                                                 }
                            channel_list.append(clean_station_item)

        return channel_list

    def get_channel_stream(self, chandict, stream_args):
        chan_item_url = "%s/status/%s" % (self.base_api_url, str(chandict["origin_id"]))
        chan_item_urlopn = self.plugin_utils.web.session.get(chan_item_url)
        stirr_chan_item = chan_item_urlopn.json()
        streamurl = stirr_chan_item['rss']["channel"]["item"]["link"]

        stream_info = {"url": streamurl}

        return stream_info
