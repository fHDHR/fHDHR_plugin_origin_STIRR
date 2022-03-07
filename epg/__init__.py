import datetime
import json
from simplejson import errors as simplejsonerrors


class Plugin_OBJ():

    def __init__(self, channels, plugin_utils):
        self.plugin_utils = plugin_utils

        self.channels = channels

        self.origin_name = plugin_utils.origin_name

        self.base_epg_url = "https://ott-gateway-stirr.sinclairstoryline.com/api/rest/v3/program/stirr/ott/"

    def update_epg(self):
        programguide = {}

        for fhdhr_channel_id in list(self.channels.list[self.plugin_utils.namespace].keys()):
            chan_obj = self.channels.list[self.plugin_utils.namespace][fhdhr_channel_id]

            if str(chan_obj.number) not in list(programguide.keys()):
                programguide[str(chan_obj.number)] = chan_obj.epgdict

            epg_opn = self.plugin_utils.web.session.get(self.base_epg_url + str(chan_obj.dict["origin_id"]))
            try:
                epg_json = epg_opn.json()
            except json.JSONDecodeError:
                epg_json = None
            except simplejsonerrors.JSONDecodeError:
                epg_json = None

            if epg_json:

                current_channel_id = chan_obj.dict["origin_id"]

                for listing in epg_json["programme"]:

                    if listing["channel"] != current_channel_id:
                        listing_chan_obj = self.channels.get_channel_obj("origin_id", listing["channel"], self.plugin_utils.namespace)
                        if str(listing_chan_obj.number) not in list(programguide.keys()):
                            programguide[str(listing_chan_obj.number)] = listing_chan_obj.epgdict
                    else:
                        listing_chan_obj = chan_obj

                    timestampdict = self.stirr_time_convert(listing["start"], listing["stop"])

                    clean_prog_dict = {
                                        "time_start": timestampdict["start"],
                                        "time_end": timestampdict["end"],
                                        "duration_minutes": timestampdict["duration"],
                                        "title": listing["title"]["value"],
                                        "sub-title": "Unavailable",
                                        "description": listing["desc"]["value"],
                                        "rating": "N/A",
                                        "episodetitle": None,
                                        "releaseyear": None,
                                        "genres": [],
                                        "seasonnumber": None,
                                        "episodenumber": None,
                                        "isnew": False,
                                        "id": "%s_%s" % (chan_obj.dict["origin_id"], timestampdict['start']),
                                        "thumbnail": None
                                        }

                    if not any((d['time_start'] == clean_prog_dict['time_start'] and d['id'] == clean_prog_dict['id']) for d in programguide[listing_chan_obj.number]["listing"]):
                        programguide[str(listing_chan_obj.number)]["listing"].append(clean_prog_dict)

        return programguide

    def stirr_time_convert(self, starttime, endtime):
        starttime = datetime.datetime.strptime(str(starttime), "%Y%m%d%H%M%S").timestamp()
        endtime = datetime.datetime.strptime(str(endtime), "%Y%m%d%H%M%S").timestamp()
        duration = (endtime - starttime) / 60
        return {"start": starttime, "end": endtime, "duration": duration}
