

#Azimuth/Distance calculator - by Don Cross</h1>
"""
    Given the latitude, longitude, and elevation of two points on the Earth,
    this calculator determines the azimuth (compass direction) and distance
    of the second point (B) as seen from the first point (A).
   
"""

#GPS PARSE
import json
import math
import time
from mpu9250_i2c import * #from the local file and https://makersportal.com/blog/2019/11/11/raspberry-pi-python-accelerometer-gyroscope-magnetometer

# some packages were renamed in Python 3
import urllib.request as urllib2
import http.cookiejar as cookielib

time.sleep(1)

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

  
def display_APRS(callsign):
	#json_url = "http://api.aprs.fi/api/get?apikey=159399.78M4gSLkxEmFnlwB&name=KBNA,KF4KFQ,AG4FW,WR1Q&what=wx&format=json"
	json_url = "http://api.aprs.fi/api/get?apikey=159399.78M4gSLkxEmFnlwB&name=" + callsign + "&what=loc&format=json"
  #API key is relative to aprs.fi account, name is callsign, what is gps, format is json
	json_item = file_get_contents(json_url)
	json_output = json.loads(json_item)
	decoded = json_output["entries"]
	print(decoded)
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

limit = 90

def EarthRadiusInMeters(latitudeRadians):
	# latitudeRadians is geodetic, i.e. that reported by GPS.
	# http://en.wikipedia.org/wiki/Earth_radius
	a = 6378137.0 #equatorial radius in meters
	b = 6356752.3 #polar radius in meters
	cos = math.cos(latitudeRadians)
	sin = math.sin(latitudeRadians)
	t1 = a * a * cos
	t2 = b * b * sin
	t3 = a * cos
	t4 = b * sin
	return math.sqrt((t1*t1 + t2*t2) / (t3*t3 + t4*t4))

def GeocentricLatitude(lat):
        # Convert geodetic latitude 'lat' to a geocentric latitude 'clat'.
        # Geodetic latitude is the latitude as given by GPS.
        # Geocentric latitude is the angle measured from center of Earth between a point and the equator.
        # https://en.wikipedia.org/wiki/Latitude#Geocentric_latitude
	e2 = 0.00669437999014
	clat = math.atan((1.0 - e2) * math.tan(lat))
	return clat


def LocationToPoint(location): #location is [lat, lon, elv]
        # Convert (lat, lon, elv) to (x, y, z).
	lat = location[0] * math.pi / 180.0
	lon = location[1] * math.pi / 180.0
	radius = EarthRadiusInMeters(lat)
	clat   = GeocentricLatitude(lat)

	cosLon = math.cos(lon)
	sinLon = math.sin(lon)
	cosLat = math.cos(clat)
	sinLat = math.sin(clat)
	x = radius * cosLon * cosLat
	y = radius * sinLon * cosLat
	z = radius * sinLat

        # We used geocentric latitude to calculate (x,y,z) on the Earth's ellipsoid.
        # Now we use geodetic latitude to calculate normal vector from the surface, to correct for elevation.
	cosGlat = math.cos(lat)
	sinGlat = math.sin(lat)

	nx = cosGlat * cosLon
	ny = cosGlat * sinLon
	nz = sinGlat

	x = x + location[2] * nx
	y = y + location[2] * ny
	z = z + location[2] * nz

	xyz = [x, y, z]
	nxyz = [nx, ny, nz]
	return [x, y, z, radius,  nx, ny, nz]



def Distance(c): #figure out what this means
	# [ap[0] ap[1] ap[2] ap[3:7] bp[0] bp[1] bp[2] bp[3]]
	dx = c[0] - c[3] #ap[0]- bp[0]
	dy = c[1] - c[4]
	dz = c[2] - c[5]
	return (math.sqrt(dx*dx + dy*dy + dz*dz)) #some sort of radius

def RotateGlobe(b, a, bradius, aradius): #[blat, blon, bel] [alat, alon, ael], [bradius], [aradius]
	# Get modified coordinates of 'b' by rotating the globe so that 'a' is at lat=0, lon=0.
	br = [b[0], (b[1]-a[1]), b[2]]; #change this
	brp = LocationToPoint(br) #returns [x y z radius nx ny nz]

	# Rotate brp cartesian coordinates around the z-axis by a.lon degrees,
	# then around the y-axis by a.lat degrees.
	# Though we are decreasing by a.lat degrees, as seen above the y-axis,
	# this is a positive (counterclockwise) rotation (if B's longitude is east of A's).
	# However, from this point of view the x-axis is pointing left.
	# So we will look the other way making the x-axis pointing right, the z-axis
	# pointing up, and the rotation treated as negative.

	alat = GeocentricLatitude(-a[0] * math.pi / 180.0)
	acos = math.cos(alat)
	asin = math.sin(alat)
	
	bx = (brp[0] * acos) - (brp[2] * asin)
	by = brp[1]
	bz = (brp[0] * asin) + (brp[2] * acos)
	
	return [bx, by, bz, bradius]

def NormalizeVectorDiff(bp, ap):
	# Calculate norm(b-a), where norm divides a vector by its length to produce a unit vector. 
	# except, we have lat and lon coordinates, not xyz
	##now it's [x, y, z, radius, nx, ny, nz]
	dx = bp[0] - ap[0]
	dy = bp[1] - ap[1]
	dz = bp[2] - ap[2]
	dist2 = dx*dx + dy*dy + dz*dz
	if (dist2 == 0):
		return null
	dist = math.sqrt(dist2)
	return [(dx/dist), (dy/dist), (dz/dist), 1.0] #[x y z radius]


def Calculate(locations):
	a = [locations[0], locations[1], locations[2]]
	b = [locations[3], locations[4], locations[5]]
	ap = LocationToPoint(a) #now it's [x, y, z, radius, nx, ny, nz]
	bp = LocationToPoint(b)
	concantentate = [ap[0], ap[1], ap[2], bp[0], bp[1], bp[2]]

	distanceM = Distance(concantentate)
	distKm = 0.001 * distanceM

# Let's use a trick to calculate azimuth:
# Rotate the globe so that point A looks like latitude 0, longitude 0.
# We keep the actual radii calculated based on the oblate geoid,
# but use angles based on subtraction.
# Point A will be at x=radius, y=0, z=0.
# Vector difference B-A will have dz = N/S component, dy = E/W component.
	br = RotateGlobe(b, a, bp[3], ap[3]) #radius is 4th element, gives [bx by bz bradius]
	if (br[2]*br[2] + br[1]*br[1] > 1.0e-6): #fix
		theta = math.atan2(br[2], br[1]) * 180.0 / math.pi
		azimuth = 90.0 - theta
		if (azimuth < 0.0):
			azimuth = azimuth + 360.0
		if (azimuth > 360.0):
			azimuth = azimuth - 360.0
		bma = NormalizeVectorDiff(bp, ap) #gives [x y z radius]
            # Calculate altitude, which is the angle above the horizon of B as seen from A.
            # Almost always, B will actually be below the horizon, so the altitude will be negative.
            # The dot product of bma and norm = cos(zenith_angle), and zenith_angle = (90 deg) - altitude.
            # So altitude = 90 - acos(dotprod).
		altitude = 90.0 - (180.0 / math.pi)*math.acos(bma[0]*ap[4] + bma[1]*ap[5] + bma[2]*ap[6]) #fix
	return [altitude, azimuth, distKm]

def FixAzimuth(old_azimuth):
	ax,ay,az,wx,wy,wz = mpu6050_conv() # read and convert mpu6050 data, you need wx, wy, wz. 
	#Assumes no x- or y-axis rotation (gyro stays flat entire time and starts pointing magnetic north) IDENTIFY IF GRID OR MAGNETIC
	#so really we need wz
	angular_accel = wz #units is degrees per second, so how do we find total degree change? integrate / multiply by time
	time_tot = 10 #number of seconds, total, that you should sample for
	aggregate = 0
	for i in range(1000)
		start = time.perf_counter()
		ax,ay,az,wx,wy,wz = mpu6050_conv()
		inst_w = wz
		time.sleep(time_tot/1000) #ten-second sample
		stop = time.perf_counter()
		dt = stop - start
		rotation = inst_w * dt #deviation is from north, counter-clockwise
		aggregate = aggregate + rotation
	azimuth = aggregate + old_azimuth
	if (azimuth < 0.0):
		azimuth = azimuth + 360.0
	if (azimuth > 360.0):
		azimuth = azimuth - 360.0
	return azimuth
	
callsign = input("Please enter the callsign to track.")
while True==True:
	
	a = [41.3535187, -74.02831, 30] #station coordinates for west point, ny at 30m asl
	# pull in Rpi coordinates here
	# input('Please enter ground station coordinates in format [lat,lon,el]') #[lat, lon]
	b = display_APRS(callsign) #parsed from APRS website, default elv = 0
	locations = [a[0], a[1],  a[2], b[1], b[2], b[3]]
	outputs = Calculate(locations)
	
	altitude = outputs[0]
	
	old_azimuth = ouputs[1]
	new_azimuth = FixAzimuth(old_azimuth)
	
	distKm = outputs[2]
	print("Altitude is: ", altitude)
	print("Azimuth is: ", new_azimuth)
	print("Distace is: ", distKm)
	#time.sleep(10) #can the api handle requests every 10 seconds?
	#port this over to antenna rotator commands



