import datetime
from dateutil import parser

def predict_location(satellite, prediction_epoch):
    
    # Get & parse epoch of satellite
    orig_rev_at_epoch = getattr(satellite, 'rev_at_epoch')
    epoch = getattr(satellite, 'epoch')
    epoch = parser.parse(epoch)

    if prediction_epoch == 'now':
        prediction_epoch = datetime.datetime.now()
    else:
    # convert to datetime
        prediction_epoch = parser.parse(prediction_epoch)

    # get time delta in seconds
    time_delta_s = (prediction_epoch - epoch).total_seconds()

    
    # calculate degree change per second
    mean_motion = getattr(satellite, 'mean_motion')
    hours_per_rotation = 24/mean_motion
    seconds_per_rotation = hours_per_rotation*60*60
    rotations_per_second = 1/seconds_per_rotation
    degrees_per_second = rotations_per_second * 360

    # multiply rate of change by time delta in seconds
    degree_change = time_delta_s * degrees_per_second
    predicted_mean_anomaly = degree_change % 360
    rev_at_epoch = orig_rev_at_epoch + int(degree_change//360)

    #update epoch and mean_anomaly
    satellite_data = satellite.to_dict()
    satellite_data['epoch'] = prediction_epoch
    satellite_data['mean_anomaly'] = float("{:.4f}".format(predicted_mean_anomaly))
    satellite_data['rev_at_epoch'] = rev_at_epoch
    
    return satellite_data
