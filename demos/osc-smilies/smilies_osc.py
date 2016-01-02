from __future__ import print_function

import argparse
import sys
from time import sleep


import liblo, sys

# create server, listening on port 1234
try:
    server = liblo.Server(1234)
except liblo.ServerError, err:
    print(str(err))
    sys.exit()


import pyglet, random
from ctypes import *
from pyglet import clock

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

WINDOWWIDTH, WINDOWHEIGHT = 1920, 1080
FPS = 60.0

batch = pyglet.graphics.Batch()

class VisWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        self.enable_esc = kwargs.pop("enable_esc", True)
        enable_fps = kwargs.pop("enable-fps", False)
        pyglet.window.Window.__init__(self, *args, **kwargs)

        if enable_fps:
            self.fps_display = pyglet.clock.ClockDisplay()
        else:
            self.fps_display = None

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE and not self.enable_esc:
            # eat esc key
            return pyglet.event.EVENT_HANDLED
        if symbol == pyglet.window.key.F:
            self.set_fullscreen(not self.fullscreen)
        return super(VisWindow, self).on_key_press(symbol, modifiers)

    def on_draw(self):
        self.clear()
        batch.draw()
        if self.fps_display is not None:
            self.fps_display.draw()


image = pyglet.resource.image("smiley-512x512.png")

SMILIES_AMT = 10

smilies_wanted = 10

class Square(pyglet.sprite.Sprite):
    def __init__(self,x,y):
        pyglet.sprite.Sprite.__init__(self,img = image,batch=batch)
        self.x = x
        self.y = y
        w = random.random() - 0.5
        self.v_x = random.random() * 400. - 200.
        self.v_y = random.random() * 400. - 200.
	self.scale = .3 + random.random()
	#self.scale = 0.2

    def update(self,dt):
        if self.x > WINDOWWIDTH:
            self.v_x *= -1
        elif self.x < -image.width * .5:
            self.v_x *= -1
            self.x = -image.width * .5 + self.v_x * dt
        if self.y > WINDOWHEIGHT:
            self.v_y *= -1
        elif self.y < -image.height * .5:
            self.v_y *= -1
            self.y = -image.height * .5 + self.v_y * dt
        self.x += self.v_x * dt
        self.y += self.v_y * dt 

sqrs = []
for _ in range(SMILIES_AMT):
    sqrs.append( Square(random.randint(0,WINDOWWIDTH-1),random.randint(0,WINDOWHEIGHT-1)) )

def add_smiley():
    sqrs.append( Square(random.randint(0,WINDOWWIDTH-1),random.randint(0,WINDOWHEIGHT-1)) )



def update_smilies_amt(amt):
    #print("set_smilies ", amt)
    global sqrs
    if amt == len(sqrs):
        return
    try:

        #print("set_smilies")
        #print len(sqrs), amt
        #print  type(amt)
        if len(sqrs) < amt:
            #print "add - ", (amt - len(sqrs))
            for i in xrange(len(sqrs), amt):
                sqrs.append( Square(random.randint(0,WINDOWWIDTH-1),random.randint(0,WINDOWHEIGHT-1)) )
        else:
            #print "chop down to ", amt
            sqrs = sqrs[0:amt]
    except Exception as e:
        print(e)

    #print("len:  ", len(sqrs))


#def smilies_amount(path, args, types, src, data):
#    global smilies_wanted

#    smilies_wanted = int(args[0])

#    print("received message '%s'" % path)
#    #print(type(args), args, data)


def smilies_amount(path, args, types, src, data):
    global smilies_wanted

    smilies_wanted = int(args[0])

    #print("received message '%s'" % path)
    #print smilies_wanted
    #print(type(args), args, data)


for i in xrange(0, 8):
    # cludge !
    server.add_method("/vis/entities/{}/amount".format(i), 'f', smilies_amount)



def update(dt):
    global smilies_wanted

    if server.recv(0):
        while server.recv(0):
            pass
    
    if smilies_wanted != len(sqrs):
        print("update: ", smilies_wanted)
        update_smilies_amt(smilies_wanted)
    
    for s in sqrs:
        s.update(dt)


clock.schedule_interval(update, 1.0/FPS)


def main():
    parser = argparse.ArgumentParser(description='Graphics experiment with OSC.')
    parser.add_argument('-disable-esc', action="store_true",
                       help='Disable escape to quit')

    args = parser.parse_args()
    window = VisWindow(WINDOWWIDTH, WINDOWHEIGHT, enable_esc=not args.disable_esc)


    pyglet.app.run()
    server.close()
    

if __name__ == '__main__':
    main()

