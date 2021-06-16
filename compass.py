
#Azimuth/Distance calculator - by Don Cross</h1>
'''
    Given the latitude, longitude, and elevation of two points on the Earth,
    this calculator determines the azimuth (compass direction) and distance
    of the second point (B) as seen from the first point (A).
'''
a = [41.3535187, -74.02831, 30]# input('Please enter ground station coordinates in format [lat,lon,el]') #[lat, lon]
b = input('please enter target coordinates in format [lat,lon,el].') #change to parse from APRS website

import math

limit = 90
def ParseAngle(id, limit):
  angle = float(id)
  if (isNaN(angle) || (angle < -limit) || (angle > limit)): ## check if this is valid
    printf("Invalid angle value.")
      return null
  else:
      return angle

def ParseElevation(id):
  angle = float(id)
  if (isNaN (angle)):
    print("Invalid elevation value.")
    return null
  else:
    return angle

    #latIN, lonIN, elvIN
def ParseLocation(prefix):
  lat = ParseAngle(latIN, 90.0) #(prefix + '_lat', 90.0)
  location = null
  if (lat != null):
    lon = ParseAngle(lonIN, 180.0) #(prefix + '_lon', 180.0)
    if (lon != null):
      elv = ParseElevation(elevationIN);
        if (elv != null):
           location = [lat, lon, elv]
  return location

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
  return [xyz, radius, nxyz]

def Distance(ap, bp): #figure out what this means
  dx = ap[0]- bp[0]
  dy = ap[1] - bp[1]
  dz = ap[2] - bp[2]
  return math.sqrt(dx*dx + dy*dy + dz*dz) #some sort of radius

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



#a = ParseLocation(a) #not sure what this does
if (a != null):
#b = ParseLocation(b) #not sure what this does - within limits?
if (b != null):
  ap = LocationToPoint(a) #now it's [x, y, z, radius, nx, ny, nz]
  bp = LocationToPoint(b)
  distKm = 0.001 * Distance(ap,bp)
                #$('div_Distance').innerHTML = distKm.toFixed(3) + '&nbsp;km';

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
        if (bma != null):
            # Calculate altitude, which is the angle above the horizon of B as seen from A.
            # Almost always, B will actually be below the horizon, so the altitude will be negative.
            # The dot product of bma and norm = cos(zenith_angle), and zenith_angle = (90 deg) - altitude.
            # So altitude = 90 - acos(dotprod).
          altitude = 90.0 - (180.0 / math.pi)*math.acos(bma[0]*ap[4] + bma[1]*ap[5] + bma[2]*ap[6]); #fix
    save_b_lat = ''    # holds point B latitude  from non-geostationary mode
    save_b_elv = ''    # holds point B elevation from non-geostationary mode
print("Altitude is: ", altitude)
print("Azimuth is: ", azimuth)
print("Distace is: ", distKm)

'''
def OnGeoCheck()
        # The geostationary checkbox was clicked.
        if (geomode == 'True')
            # Save values so user doesn't lose them on accidental/curiosity click.
            save_b_lat = $('b_lat').value;
            save_b_elv = $('b_elv').value;

            // Fill in the values for geostationary orbit.
            $('b_lat').value = '0';         // assume satellite is directly above equator.
            $('b_elv').value = '35786000';  // 35,786 km above equator.

            // Disable editing of point B latitude and elevation while box is checked.
            $('b_lat').disabled = true;
            $('b_elv').disabled = true;
        } else {
            // Restore saved values to edit boxes, so user doesn't lose them.
            $('b_lat').value = save_b_lat;
            $('b_elv').value = save_b_elv;

            // Enable editing of point B latitude and elevation while box is checked.
            $('b_lat').disabled = false;
            $('b_elv').disabled = false;
        }
    }
'''


