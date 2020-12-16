import datetime
import json


class OriginEPG():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.base_epg_url = "https://ott-gateway-stirr.sinclairstoryline.com/api/rest/v3/program/stirr/ott/"

    def update_epg(self, fhdhr_channels):
        programguide = {}

        for fhdhr_id in list(fhdhr_channels.list.keys()):
            chan_obj = fhdhr_channels.list[fhdhr_id]

            if str(chan_obj.number) not in list(programguide.keys()):
                programguide[str(chan_obj.number)] = chan_obj.epgdict

            epg_opn = self.fhdhr.web.session.get(self.base_epg_url + str(chan_obj.dict["origin_id"]))
            try:
                epg_json = epg_opn.json()
            except json.JSONDecodeError:
                epg_json = None

            if epg_json:

                current_channel_id = chan_obj.dict["origin_id"]

                for listing in epg_json["programme"]:

                    if listing["channel"] != current_channel_id:
                        listing_chan_obj = fhdhr_channels.get_channel_obj("origin_id", listing["channel"])
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
