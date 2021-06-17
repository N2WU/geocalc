import json

# some packages were renamed in Python 3
import urllib.request as urllib2
import http.cookiejar as cookielib

def file_get_contents(url):
    url = str(url).replace(" ", "+") # just in case, no space in url
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    try:
        page = urllib2.urlopen(req)
        return page.read()
    except urllib2.HTTPError as e:
        print(e.fp.read())
    return ''

"""
function display_APRS() {
	$json_url = "http://api.aprs.fi/api/get?apikey=159399.78M4gSLkxEmFnlwB&name=KBNA,KF4KFQ,AG4FW,WR1Q&what=wx&format=json";
	$json = file_get_contents( $json_url, 0, null, null );
	$json_output = json_decode( $json, true);
	$station_array = $json_output[ 'entries' ];
	foreach ( $station_array as $station ) {
		$name = $station[ 'name' ];
		$temp = $station[ 'temp' ];
		$temp = ( ( 9 / 5 ) * $temp ) + 32; // Convert celsius to fahrenheit.
		echo "Temperature is ".$temp."°F at ".$name."\n";



import json
 
json_input = '{"persons": [{"name": "Brian", "city": "Seattle"}, {"name": "David", "city": "Amsterdam"} ] }'

try:
    decoded = json.loads(json_input)
 
    # Access data
    for x in decoded['persons']:
        print x['name']
 
except (ValueError, KeyError, TypeError):
    print "JSON format error"
"""


def display_APRS():
	#json_url = "http://api.aprs.fi/api/get?apikey=159399.78M4gSLkxEmFnlwB&name=KBNA,KF4KFQ,AG4FW,WR1Q&what=wx&format=json"
	json_url = "http://api.aprs.fi/api/get?apikey=159399.78M4gSLkxEmFnlwB&name=N2WU&what=loc&format=json"
	json_item = file_get_contents(json_url)
	json_output = json.loads(json_item)
	#print(json_output)
	decoded = json_output["entries"]
	#print(station_array)
	#staton_array_py = json.loads(station_array)
	#print(station_array)
	#try:
	#decoded = json.loads(station_array)
	print(decoded)

	#decoded[0].encode('ascii','ignore').decode()
		# Access data
	for station in decoded:
		lat = station['lat']
		print(lat)
		lng = station['lng']
		#temp = ((9/5) * float(temp)) + 32 #convert C to F
		print(lng)
		try:
			elv = station['altitude']
		except:
			elv = 0	
		print(elv)
		info = [lat, lng, elv]
 
	#except (ValueError, KeyError, TypeError):
		#print("JSON format error")

    
display_APRS()
