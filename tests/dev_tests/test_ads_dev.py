import time

def test_3v_measure():
    v = 0
    n = 0
    print('\nMeasure 3V DC source now...')
    while v < 3.0:
        v = sensor.raw_to_v(sensor.read())
        time.sleep(0.5)
        n += 1
        if n > 10:
            break
    return v

def test_ground_measure():
    v = 3
    n = 0
    print('\nMeasure GND source now...')
    while v > 0.3:
        v = sensor.raw_to_v(sensor.read())
        time.sleep(0.5)
        n += 1
        if n > 10:
            break
    return v
