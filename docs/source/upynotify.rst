Upynotify
=========

A module to notify events with beeps (buzzer needed) and blinks. This is useful for *physical debugging*



Class:

**NOTIFYER** (buzz_pin, led_pin, fq=4000, on_time=150, n_times=2, off_time=150, timer=None, period=5000)

    * *buzz_pin*\: the pin number to drive the buzzer
    * *led_pin*\: the pin number to drive the led
    * *fq*\: Frequency of the PWM to drive the buzzer
    * *on_time*\: time in ms that the buzzer or led is on when calling the methods ``buzzer_call(1)`` or ``blink_call(1)``
    * *off_time*\:  time in ms that the buzzer or led is off when calling the methods ``buzzer_call(1)`` or ``blink_call(1)``
    * *n_times*\: number of times a cycle of on-off is repeated when calling the methods ``buzzer_call(1)`` or ``blink_call(1)``
    * *timer*\: the number of the Timer to use, if using **notify** method. (This allows to schedule notifications and repeat it every *period* milliseconds)
    * *period*\: time in milliseconds to pass to the Timer.



Methods of **NOTIFYER** class:

* **buzz_beep** (beep_on_time, n_times, beep_off_time, fq, led=True)

  * To make the buzz beep with the indicated parameters

* **led_blink** (led_on_time, n_times, led_off_time)

  * To make the buzz blink with the indicated parameters

* **notify** (use='buzz', mode='SHOT', timeout=5000, on_init=None)

  * To make a notification using ``buzz`` or ``led`` indicated by use, in the mode ``SHOT`` (one time after timeout in ms) or ``PERIODIC`` (each time after timeout in ms, until stopped). Allows to execute a function *on_init*, for example , print or log a message.
