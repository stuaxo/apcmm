# config to forward messages over OSC
#
# apcmm --config config.py
#

OSC_TARGET=":1234"  # OSC Messages will be sent to local port :1234
RECV_MIDI="APC MINI MIDI 1"
SEND_MIDI="APC MINI MIDI 1"

from . import ClipButton

def on_button_press(button):
    osc.send("%s/press_%s" % (button.type, button.name))

def on_button_release(button):
    osc.send("%s/release_%s" % (button.type, button.name))

def on_slide(slider):
    osc.send("/slide/%d" % (slider.id, slider.value))

def on_clip_press(clip_button):
    clip_button.color = ClipButton.YELLOW

def on_clip_release(clip_button):
    clip_button.color = ClipButton.OFF

