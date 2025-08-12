import datetime as dt

import sorunlib as run

from sorunlib.commands import _timestamp_to_utc_datetime
from sorunlib._internal import check_response


def move_to(az, el):
    """Move telescope to specified coordinates.

    Args:
        az (float): destination angle for the azimuthal axis
        el (float): destination angle for the elevation axis

    """
    acu = run.CLIENTS['acu']
    resp = acu.go_to(az=az, el=el)
    check_response(acu, resp)


def move_to_target(az, el, start_time, stop_time, drift):
    """Move telescope to a given drifting target.

    Args:
        az (float): Destination angle for the azimuthal axis.
        el (float): Destination angle for the elevation axis.
        start_time (str): Time in ISO format that target is at the given
            coordinates, i.e. "2024-09-22T07:13:34.416664+00:00".
        stop_time (str): Time in ISO format that the target is no longer
            available to scan, i.e. "2024-09-22T08:42:16.343049+00:00".
        drift (float): Azimuthal drift rate of the target in degrees per
            second. Used to adjust ``az`` if the move occurs after
            ``start_time`` but before ``stop_time``.

    """
    start = _timestamp_to_utc_datetime(start_time)
    stop = _timestamp_to_utc_datetime(stop_time)
    now = dt.datetime.now(dt.timezone.utc)

    if now > start and now < stop:
        az = az + drift * (now - start).total_seconds()
        print(f"Target has drifted since {start_time}. Moving to ({az}, {el}).")

    if now > stop:
        return

    move_to(az, el)


def set_boresight(target):
    """Move the third axis to a specific target angle.

    Args:
        target (float): destination angle for boresight rotation

    """
    acu = run.CLIENTS['acu']
    resp = acu.set_boresight(target=target)
    check_response(acu, resp)


def set_scan_params(az_speed, az_accel, reset=False):
    """Update the default scan parameters, used during :func:`sorunlib.seq.scan`.

    Args:
        az_speed (float, optional): The azimuth scan speed.
        az_accel (float, optional): The (average) azimuth acceleration at
            turn-around.
        reset (bool, optional): If True, reset all params to default values
            before applying any updates passed explicitly here.

    """
    acu = run.CLIENTS['acu']
    resp = acu.set_scan_params(az_speed=az_speed,
                               az_accel=az_accel,
                               reset=reset)
    check_response(acu, resp)


def set_shutter(action):
    """Control the LAT shutter.

    Args:
        action (str): Shutter action, either 'open' or 'close'.

    """
    acu = run.CLIENTS['acu']
    resp = acu.set_shutter(action=action)
    check_response(acu, resp)
