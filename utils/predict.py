

''' SWAP THESE'''
from utils.models import Satellite
#from models import Satellite
'''     '''

from sgp4 import exporter
from sgp4.api import Satrec, jday
from sgp4.conveniences import dump_satrec
from pprint import pprint
from skyfield.api import load, wgs84, EarthSatellite

from decimal import Decimal
import datetime
from dateutil import parser
import json

''' FOR TESTING '''

# sat_dict = {
#             "satellite_name": "STARLINK-5171",
#             "satellite_id": "2022-136AC",
#             "epoch": "2022-10-30T00:00:00.999648",
#             "mean_motion": 15.7892089,
#             "eccentricity": 0.0001163,
#             "inclination": 53.2173,
#             "ra_of_asc_node": 101.4613,
#             "arg_of_pericenter": 62.8253,
#             "mean_anomaly": 58.4356,
#             "ephemeris_type": 0,
#             "classification_type": "U",
#             "norad_cat_id": 54077,
#             "element_set_no": 999,
#             "rev_at_epoch": 198,
#             "bstar": -0.0075201,
#             "mean_motion_dot": -0.0120544,
#             "source": "STARLINK"
# }
#sat = Satellite(**sat_dict)

'''    '''
def convert_day_percentage(epoch):

    total_mins = (epoch.hour * 60) + epoch.minute
    total_seconds = (total_mins * 60) + epoch.second
    total_mcs = total_seconds * 1_000_000 + epoch.microsecond

    return float(total_mcs/86_400_000_000)

def convert_bstar(bstar):
    ''' Abominable conversion to tle_bstr. Assumes bstar will never be > 1 '''

    b_str = str('{:.12f}'.format(bstar))
    #print(b_str)

    decimal_i = None
    sig_i = None
    i = 0
    sig_figs =[]
    for char in b_str:
        # Found decimal location
        if (b_str[i] == '.'):
            decimal_i = i
        # Found sig figure
        elif(decimal_i != None):
            # If first sig fig, record location
            if (sig_i == None and char != '0'):
                sig_i = i
            if (char != '0' or (char=='0' and sig_i != None)):
                sig_figs.append(char)
        i+=1

    sig_figs = sig_figs[0:5]
    tle_b_str = f"{'-' if bstar < 0 else ' '}{''.join(sig_figs) + str(decimal_i - (sig_i-1))}"
    #print(tle_b_str)
    return tle_b_str


def compute_checksum(tle_line):
    sum = 0
    for char in tle_line:
        if char.isdigit():
            sum += int(char)
        elif char == '-':
            sum +=1

    return sum % 10


''' Get Satellite attributes from Satrec object'''
def get_attributes(sat):
    attr_str = dump_satrec(sat)
    attr_dict = {}

    for line in attr_str:
        line = line.replace(' ', '').replace('\n', '') # strip whitespace
        if '=' in line:
            attr = line.split('=')
            attr_dict[attr[0]] = attr[1]

    return attr_dict


def convert_to_tle(
    norad_cat_id, 
    classification_type,
    satellite_id,
    epoch_str,
    mean_motion_dot, 
    bstar,
    element_set_no,
    inclination,
    ra_of_asc_node,
    eccentricity,
    arg_of_pericenter,
    mean_anomaly,
    mean_motion,
    rev_at_epoch
):
    # Launch data from object id
    l_yr = satellite_id[2:4]
    l_num = satellite_id[5:]

    # Epoch data
    epoch = parser.parse(epoch_str)
    epoch_yr = str(epoch.year)[-2:]
    doy = epoch.timetuple().tm_yday
    day_pct = convert_day_percentage(epoch)

    # Constants
    mean_motion_ddot = "00000+0"
    ephemeris_type = '0'


    ''' Compute 's' string '''

    # Calculate classification details and following spaces
    cat_class = f'1 {norad_cat_id}{classification_type}'
    cat_space = ''.join([' ' for i in range(9 - len(cat_class))])
    cat = f"{cat_class}{cat_space}"

    # Calculate launch details and following spaces
    launch_data = f'{cat}{l_yr}{l_num}'
    launch_space = ''.join([' ' for i in range(18 - len(launch_data))])
    launch =f"{launch_data}{launch_space}"

    # Calculate epoch details and following spaces
    day_data = float(doy + day_pct)
    day_data_f = format(day_data, '.8f')
    epoch_data = f'{launch}{epoch_yr}{day_data_f}'
    epoch_space = ''.join([' ' for i in range(33 - len(epoch_data))])
    epoch = f'{epoch_data}{epoch_space}'

    # Calculate mean motion details and following spaces
    #format mean motion dot
    if mean_motion_dot > 0:
        mean_motion_dot = ' ' + str(format(mean_motion_dot, '.8f')).replace('0.','.')
    else:
        mean_motion_dot = str(format(mean_motion_dot, '.8f')).replace('0.','.')
    
    mean_motion_dot_data = f'{epoch}{mean_motion_dot}'
    #print("mean_motion_dot_data len", len(mean_motion_dot_data))
    mean_motion_dot_space = ''.join([' ' for i in range(45 - len(mean_motion_dot_data))])
    mean_motion_dot_all = f'{mean_motion_dot_data}{mean_motion_dot_space}'

    # Calculate mean motion dot details and following spaces
    mean_motion_ddot_data = f'{mean_motion_dot_all}{mean_motion_ddot}'
    mean_motion_ddot_space = ''.join([' ' for i in range(53 - len(mean_motion_ddot_data))])
    mean_motion_ddot = f'{mean_motion_ddot_data}{mean_motion_ddot_space}'

    # Calculate bstar (drag) details and following spaces AND Ephemeris (always one space)
    
    bstar_data = f'{mean_motion_ddot}{convert_bstar(bstar)} {ephemeris_type}'
    bstar_space = ''.join([' ' for i in range(65 - len(bstar_data))])
    bstar_all = f'{bstar_data}{bstar_space}'

    ephemeris = f'{bstar_all}'

    s_unchecked = f'{ephemeris}{element_set_no}'

    checksum = compute_checksum(s_unchecked)
    
    s = f'{s_unchecked}{checksum}'



    ''' Compute 't' string '''

    # Always assuming 2 spaces after catalog id
    catalog = f'2 {norad_cat_id}  '

    # Format inclination data
    inclination_formatted = format(inclination, '.4f')

    inclination_data = f'{catalog}{inclination_formatted}'
    inclination_spaces = ''.join([' ' for i in range(17 - len(inclination_data))])
    #print(f'inclination_data len: {len(inclination_data)}')
    inclination_all = f'{inclination_data}{inclination_spaces}'
    

    #format ra data

    # Format ra_of_asc_node (add starting space if < 100)
    if (ra_of_asc_node < 10):
        ra = '  ' + format(ra_of_asc_node, '.4f')
    elif (ra_of_asc_node < 100):
        ra = ' ' + format(ra_of_asc_node, '.4f')
    else:
        ra = format(ra_of_asc_node, '.4f')

    ra_data = f'{inclination_all}{ra}'
    ra_spaces = ''.join([' ' for i in range(26 - len(ra_data))])
    #print(f'ra_data len: {len(ra_data)}')
    ra_all = f'{ra_data}{ra_spaces}'


    # Format eccentricity
    eccentricity_formatted = format(eccentricity, '.7f').replace('0.','')

    eccentricity_data = f'{ra_all}{eccentricity_formatted}'
    eccentricity_spaces = ''.join([' ' for i in range(34 - len(eccentricity_data))])
    #print(f'eccentricity len {len(eccentricity_data)}')
    #print(f'eccentricity spaces {len(eccentricity_spaces)}')
    eccentricity_all = f'{eccentricity_data}{eccentricity_spaces}'


    # Format arg_of_pericenter
    if arg_of_pericenter < 10:
        arg_of_pericenter = '  ' + format(arg_of_pericenter, '.4f')
    elif arg_of_pericenter < 100:
        arg_of_pericenter = ' ' + format(arg_of_pericenter, '.4f')
    else:
        arg_of_pericenter = format(arg_of_pericenter, '.4f')

    arg_of_pericenter_data = f'{eccentricity_all}{arg_of_pericenter}'
    #print(f'aop len {len(arg_of_pericenter_data)}')
    arg_of_pericenter_spaces = ''.join([' ' for i in range(43 - len(arg_of_pericenter_data))])
    arg_of_pericenter_all = f'{arg_of_pericenter_data}{arg_of_pericenter_spaces}'


    # Format mean_anomaly
    if mean_anomaly < 10:
        mean_anomaly = '  ' + format(mean_anomaly, '.4f')
    elif mean_anomaly < 100:
        mean_anomaly = ' ' + format(mean_anomaly, '.4f')
    else:
        mean_anomaly = format(mean_anomaly, '.4f')

    mean_anomaly_data = f'{arg_of_pericenter_all}{mean_anomaly}'
    #print(f'mean_anomaly_data len {len(mean_anomaly_data)}')
    mean_anomaly_spaces = ''.join([' ' for i in range(52 - len(mean_anomaly_data))])
    mean_anomaly_all = f'{mean_anomaly_data}{mean_anomaly_spaces}'


    #format mean_motion (10 < mean_motion < 100)
    mean_motion = format(mean_motion, '.8f')
    mean_motion_data = f'{mean_anomaly_all}{mean_motion}'
    #print(f'mean_motion_data len {len(mean_motion_data)}')
    mean_motion_spaces = ''.join([' ' for i in range(63 - len(mean_motion_data))])
    mean_motion_all = f'{mean_motion_data}{mean_motion_spaces}'

    #format rev_at_epoch
    if rev_at_epoch < 10:
        rev_at_epoch = '    ' + str(rev_at_epoch)
    elif rev_at_epoch < 100:
        rev_at_epoch = '   ' + str(rev_at_epoch)
    elif rev_at_epoch < 1000:
        rev_at_epoch = '  ' + str(rev_at_epoch)
    elif rev_at_epoch < 10000:
        rev_at_epoch = ' ' + str(rev_at_epoch)
    else:
        rev_at_epoch = str(rev_at_epoch)

    t_unchecked = f'{mean_motion_all}{rev_at_epoch}'
    t = f'{t_unchecked}{compute_checksum(t_unchecked)}'


    return s, t


def unpack_to_tle(**kwargs):
    s, t = convert_to_tle(
        norad_cat_id = kwargs['norad_cat_id'],
        classification_type = kwargs['classification_type'],
        satellite_id = kwargs['satellite_id'],
        epoch_str = kwargs['epoch'],
        mean_motion_dot = kwargs['mean_motion_dot'], 
        bstar = kwargs['bstar'],
        element_set_no = kwargs['element_set_no'],
        inclination = kwargs['inclination'],
        ra_of_asc_node = kwargs['ra_of_asc_node'],
        eccentricity = kwargs['eccentricity'],
        arg_of_pericenter = kwargs['arg_of_pericenter'],
        mean_anomaly = kwargs['mean_anomaly'],
        mean_motion = kwargs['mean_motion'],
        rev_at_epoch = kwargs['rev_at_epoch']
    )
    # print(kwargs['satellite_name'])
    # print(s)
    # print(t)
    return s, t
    


''' Generate Satellite Object and Predict Location '''

def predict_location(satellite: Satellite, prediction_epoch: str) -> dict:
    # Get TLE of Satellite object
    s, t = unpack_to_tle(**satellite.to_dict())

    # Generate skyfield satellite object
    ts = load.timescale()
    sky_sat =  EarthSatellite(s, t, satellite.satellite_name, ts)

    #satrec_obj = Satrec.twoline2rv(s, t)

    # Replace epoch
    if (prediction_epoch == "now"):
        #epoch = datetime.datetime.now()
        t = ts.now()

        # Generate now() timestamp
        now_dt = datetime.datetime.now()
        prediction_epoch = now_dt.isoformat()

    else:
        epoch = parser.parse(prediction_epoch)
        t = ts.utc(int(epoch.year), int(epoch.month), int(epoch.day), int(epoch.hour), int(epoch.minute), int(epoch.second))

    # Get coords (Geocentric, stationary)
    geocentric_coords = sky_sat.at(t)

    # Convert to lat/long
    lat, lon = wgs84.latlon_of(geocentric_coords)

    prediction = {
        "epoch" : prediction_epoch,
        "latitude" : str(lat),
        "longitude": str(lon),
    }

    sat_dict = satellite.to_dict()
    sat_dict['prediction'] = prediction

    return sat_dict
    
# sd = predict_location(sat, "now")
# print(sd)
