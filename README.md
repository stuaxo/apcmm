APCMM
=====

APC Mini API and emulator.

(Fairly unfinished and experimental).

Install
=======

Update setuptools and friends
-----------------------------

```
$ python -mpip install -U pip setuptools wheel
```

Install
-------

```
$ pip install -r requirements.txt

$ python setup.py install
```


Run Emulator
------------
```
$ apcmm
```



What works?
===========

This works well enough to drive the smilies osc demo in the demos folder.

The OSC example works and you can set led colours.



What doesn't work ?
===================

Most things (see the TODO).   When I made this I had never used a midi mapper, also
I have never used Ableton (which the APC is made for), so this was kind of an 
experiment.

The main thing I found missing for visual performance is optional smoothing for
the sliders, as they faithfully reproduce every jank you make as you move them.
