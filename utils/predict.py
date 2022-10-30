import datetime
from dateutil import parser
from utils.models import Satellite

def predict_location(satellite: Satellite, prediction_epoch: str) -> dict:
    
    # Get & parse epoch of satellite
    orig_rev_at_epoch = getattr(satellite, 'rev_at_epoch')
    print(f'orig_rev_at_epoch = {orig_rev_at_epoch}')
    mean_motion = getattr(satellite, 'mean_motion')
    accel = getattr(satellite, 'mean_motion_dot')
    epoch = getattr(satellite, 'epoch')
    epoch = parser.parse(epoch)

    if prediction_epoch == 'now':
        prediction_epoch = datetime.datetime.now()
    else:
    # convert to datetime
        prediction_epoch = parser.parse(prediction_epoch)

    # get time delta in seconds
    time_delta_s = (prediction_epoch - epoch).total_seconds()

    degrees_per_second = (1/((24/mean_motion)*60*60))*360
    accel_pss = 0
    if (accel != 0):
        accel_pss = ((1/((24/accel)*60*60))*360)/86400
        print(f"accel_pss {accel_pss}")
    '''
    mean_motion = rotations/day  (360 degrees/1 rotation) (1 day^2/86400^2 seconds) ->
    x degrees/second = 
    mean_motion ((rotations/day^2)

    360
    --
    (24/accel)*60*60
    '''
    # x = v0(t) + 1/2a(t^2)
    #print(f"accel {accel}")
    #degree_change = (time_delta_s * degrees_per_second) + (accel_pss) * (time_delta_s * time_delta_s)

    degree_change = (time_delta_s * degrees_per_second)

    predicted_mean_anomaly = degree_change % 360
    rev_at_epoch = orig_rev_at_epoch + int(degree_change//360)

    #update epoch and mean_anomaly
    satellite_data = satellite.to_dict()
    satellite_data['epoch'] = prediction_epoch
    satellite_data['mean_anomaly'] = float("{:.4f}".format(predicted_mean_anomaly))
    satellite_data['rev_at_epoch'] = rev_at_epoch
    
    return satellite_data
