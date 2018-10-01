
import json
import math
import os
import sys
import time
import argparse

from Mastermind._mm_client import MastermindClientTCP
from src.action import Action
from src.command import Command
from src.item import Item, ItemManager
from src.position import Position
from src.worldmap import Worldmap, Chunk
from src.player import Player

import pyglet
import glooey


class MapUtils:
    def lerp(self, start, end, t):
        return start + t * (end-start)

    def lerp_point(self, p0, p1, t):
        return (int(self.lerp(p0[0], p1[0], t)), int(self.lerp(p0[1], p1[1], t)))

    def diagonal_distance(self, p0, p1):
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        return max(abs(dx), abs(dy))

    def line(self, p0, p1):
        points = []
        diagonal_distance = self.diagonal_distance(p0, p1)
        for step in range(diagonal_distance):
            points.append(self.lerp_point(p0, p1, step/diagonal_distance))
        return points # so now we have a set of points along a line.

class Client(MastermindClientTCP): # extends MastermindClientTCP
    def __init__(self, name):
        MastermindClientTCP.__init__(self)
        self.player = Player(str(name)) # recieves updates from server. the player and all it's stats.
        self.chunk = None


    def draw_map(self, stdscr):
        #TODO: lerp the positions of creatures from one frame to the next.


        for i, x in self.chunk.items():
            for j, terrain in x.items():
                (j, i, terrain.symbol)
      
        stdscr.refresh()
        #stdscr.getkey()
        # blit the map
      
        # blit objects, then items, then creatures, then the player, 
           
            # then blit weather. Weather is the only thing above players and creatures.
            #TODO: blit weather


if __name__ == "__main__":
        
        '''parser = argparse.ArgumentParser(description='Cataclysm LD Client', epilog="Please start the client with a first and last name for your character.")
        parser.add_argument('--host', metavar='Host', help='Server host', default='localhost')
        parser.add_argument('-p', '--port', metavar='Port', type=int, help='Server port', default=6317)
        parser.add_argument('name', help='Player\'s name')
        
        args = parser.parse_args()
        ip = args.host
        port = args.port'''

        window = pyglet.window.Window(854, 480)
        gui = glooey.Gui(window)
        pyglet.resource.path = ['tiles','tiles/background']
        pyglet.resource.reindex()
        bg = glooey.Background()
        bg.set_appearance(
            center=pyglet.resource.texture('center.png'),
            top=pyglet.resource.texture('top.png'),
            bottom=pyglet.resource.texture('bottom.png'),
            left=pyglet.resource.texture('left.png'),
            right=pyglet.resource.texture('right.png'),
            top_left=pyglet.resource.texture('top_left.png'),
            top_right=pyglet.resource.texture('top_right.png'),
            bottom_left=pyglet.resource.texture('bottom_left.png'),
            bottom_right=pyglet.resource.texture('bottom_right.png')
            )
        gui.add(bg)
        pyglet.app.run() 

        client = Client(args.name)
        client.connect(ip, port)
        command = Command(client.player.name, 'login', ['password'])
        client.send(command)
        command = Command(client.player.name, 'request_map')
        client.send(command)
        command = None
        last_time = time.time()
        while True:
            try:
                # if we recieve an update from the server process it. do this first.
                next_update = client.receive(False)
                if(next_update is not None):
                    print('--next_update--') # we recieved a message from the server. let's process it.
                    print(type(next_update))
                    if(isinstance(next_update, Player)):
                        #print('got playerupdate')
                        client.player = next_update # client.player is updated
                    elif(isinstance(next_update, dict)): 
                        last_time = time.time() # save the last time we got a localmap update
                        client.chunk = next_update
                        client.draw_map() # update after everything is complete.
                else:
                    command = Command(client.player.name, 'request_map')
                    client.send(command)
                
                

            except KeyboardInterrupt:
                print('cleaning up before exiting.')
                print('done cleaning up.')
                sys.exit()
            except Exception as e:
                print('!! Emergency Exit due to Server Exception. !!')
                print(e)
                print()
                sys.exit()
