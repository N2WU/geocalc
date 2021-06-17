import json

def display_APRS():
	json_url = "http://api.aprs.fi/api/get?apikey=0000&name=KBNA,KF4KFQ,AG4FW,WR1Q&what=wx&format=json"
	#json = file_get_contents(url, 0, null, null)
	json_outut = json.JSONDecoder(json, True)
	station_array = json_output["entries"]
	for station in range(1, len(station_array)):
		name = station["name"]
		temp = station["temp"]
		temp = ((9/5) * temp) + 32 #convert C to F
    
display_APRS()
