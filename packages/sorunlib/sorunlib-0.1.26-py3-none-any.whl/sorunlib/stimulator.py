import time
import sorunlib as run
from sorunlib._internal import check_response

ID_SHUTTER = 1


def _open_shutter():
    """Open the shutter of the stimulator"""
    ds = run.CLIENTS['stimulator']['ds378']
    resp = ds.set_relay(relay_number=ID_SHUTTER, on_off=1)
    check_response(ds, resp)

    time.sleep(1)


def _close_shutter():
    """Close the shutter of the stimulator"""
    ds = run.CLIENTS['stimulator']['ds378']
    resp = ds.set_relay(relay_number=ID_SHUTTER, on_off=0)
    check_response(ds, resp)

    time.sleep(1)


def _setup():
    # Open shutter
    _open_shutter()

    # Acceleration / Decceleration configuration
    blh = run.CLIENTS['stimulator']['blh']
    resp = blh.set_value(accl_time=10, decl_time=10)
    check_response(blh, resp)


def _stop():
    blh = run.CLIENTS['stimulator']['blh']

    # Stop rotation
    resp = blh.stop_rotation()
    check_response(blh, resp)
    time.sleep(10)

    # Close shutter
    _close_shutter()


def calibrate_tau(duration_step=10,
                  speeds_rpm=[225, 495, 945, 1395, 1845, 2205],
                  forward=True, do_setup=True, stop=True,
                  downsample_factor=8, filter_order=4, filter_cutoff=300):
    """Time constant calibration using the stimulator.

    Parameters
    ----------
    duration_step : float, optional
        Duration of each step of time constant measurement in sec, default to 10 sec.
    speeds_rpm : list of float, optional
        List of chopper rotation speed in RPM for each step. Defaults to [225, 495, 945, 1395, 1845, 2205].
    forward : bool, optional
        Chopper rotation direction. If True, the chopper rotates clockwise
        when viewed from the receiver toward the stimulator. Defaults to True.
    do_setup : bool, optional
        Do initial setup (i.e. open shutter, set acceleration, start rotation) if True. Defaults to True.
    stop : bool, optional
        Stop the rotation and close the shutter if True. Defaults to True.
    downsample_factor : int, optional
        Downsample factor for SMuRF. Defaults to 8.
    filter_order : int, optional
        Order of the downsample filter for SMuRF. Defaults to 4.
    filter_cutoff : float, optional
        The cutoff frequency in Hz for the downsample filter for SMuRF. Defaults to 300.
    """

    blh = run.CLIENTS['stimulator']['blh']

    try:
        run.smurf.stream('on', tag='stimulator, time_constant', subtype='cal',
                         filter_order=filter_order, filter_cutoff=filter_cutoff,
                         downsample_factor=downsample_factor)

        if do_setup:
            _setup()
            # Rotation setting
            resp = blh.set_value(speed=speeds_rpm[0])
            check_response(blh, resp)

            resp = blh.start_rotation(forward=forward)
            check_response(blh, resp)

            speeds_rpm = speeds_rpm[1:]

            # First data point
            time.sleep(duration_step)

        for speed_rpm in speeds_rpm:
            resp = blh.set_value(speed=speed_rpm)
            check_response(blh, resp)

            time.sleep(duration_step)
    finally:
        try:
            run.smurf.stream('off')
        except RuntimeError as e:
            print(f"Caught error while shutting down SMuRF streams: {e}")

        if stop:
            _stop()


def calibrate_gain(duration=60, speed_rpm=90,
                   forward=True, do_setup=True, stop=True):
    """Gain calibration with the stimulator

    Parameters
    ----------
    duration : float, optional
        Duration of the gain calibration in sec, default to 60 sec.
    speed_rpm : float, optional
        Rotation speed of the chopper wheel in RPM, default to 90 RPM.
    forward : bool, optional
        Chopper rotation direction. If True, the chopper rotates clockwise
        when viewed from the receiver toward the stimulator. Defaults to True.
    do_setup : bool, optional
        Do initial setup (i.e. open shutter, set acceleration, start rotation) if True.
        Defaults to True.
    stop : bool, optional
        Stop the rotation and close the shutter if True. Defaults to True.
    """
    blh = run.CLIENTS['stimulator']['blh']

    try:
        resp = blh.set_value(speed=speed_rpm)
        check_response(blh, resp)

        if do_setup:
            _setup()
            # Rotation setting
            resp = blh.start_rotation(forward=forward)
            check_response(blh, resp)

        # Sleep for rotation stabilization
        time.sleep(10)

        run.smurf.stream('on', tag='stimulator, gain', subtype='cal')

        # Data taking
        time.sleep(duration)
    finally:
        try:
            run.smurf.stream('off')
        except RuntimeError as e:
            print(f"Caught error while shutting down SMuRF streams: {e}")

        if stop:
            _stop()
