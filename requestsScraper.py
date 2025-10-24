from datetime import datetime, timedelta
NOW_DATE = datetime.now()

getTTViewDataURL = "https://finki.edupage.org/timetable/server/ttviewer.js?__func=getTTViewerData"
getTTViewDataPayload  = {"__args": [None, NOW_DATE.year],"__gsh": "00000000"}

DATEFROM = ( NOW_DATE - timedelta(days = NOW_DATE.weekday()) )
DATETO   = ( DATEFROM + timedelta(days = 6                 ) ).strftime("%Y-%m-%d")
DATEFROM = DATEFROM.strftime("%Y-%m-%d")

mainDBAccessorURL = "https://finki.edupage.org/rpr/server/maindbi.js?__func=mainDBIAccessor"
mainDBAccessorPayload = {"__args": [None,2025,{"vt_filter": {"datefrom": DATEFROM, "dateto": DATETO}},{"op": "fetch","needed_part": {"teachers": ["short","name","firstname","lastname","callname","subname","code","cb_hidden","expired"],"classes": ["short","name","firstname","lastname","callname","subname","code","classroomid"],"classrooms": ["short","name","firstname","lastname","callname","subname","code"],"igroups": ["short","name","firstname","lastname","callname","subname","code"],"students": ["short","name","firstname","lastname","callname","subname","code","classid"],"subjects": ["short","name","firstname","lastname","callname","subname","code"],"events": ["typ","name"],"event_types": ["name","icon"],"subst_absents": ["date","absent_typeid","groupname"],"periods": ["short","name","firstname","lastname","callname","subname","code","period","starttime","endtime"],"dayparts": ["starttime","endtime"],"dates": ["tt_num","tt_day"]},"needed_combos": {}}],"__gsh": "00000000"}

regularGetDataURL = "https://finki.edupage.org/timetable/server/regulartt.js?__func=regularttGetData"
regularGetDataPayload = {"__args": [None,"26"],"__gsh": "00000000"}

import requests
import json

def scrape():
	with requests.Session() as s:
		s.get("https://finki.edupage.org/timetable/")
		
		gtvd = s.post(getTTViewDataURL,json = getTTViewDataPayload ).json()
		default_num = gtvd["r"]["regular"]["default_num"]	

		regularGetDataPayload["__args"][1] = default_num 

		rgd = s.post(regularGetDataURL, json = regularGetDataPayload).json()

		s.post(mainDBAccessorURL, json = mainDBAccessorPayload) # just in case
		return rgd

from storage import storeData
import json

if __name__ == "__main__":
	jsonBlob = json.dumps( scrape() )
	storeData(jsonBlob)

	print("Scraping DONE!")