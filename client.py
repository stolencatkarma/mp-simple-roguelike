
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
from pyglet.window import key as KEY
from pyglet import clock


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
        self.player = Player(9999,9999, str(name)) # recieves updates from server. the player and all it's stats.
        self.chunk = None

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

        

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == KEY.RETURN:
                print('return')
     
        

    def draw_map(self):
        #TODO: lerp the positions of creatures from one frame to the next.


        for i, x in self.chunk.items():
            for j, terrain in x.items():
                (j, i, terrain.symbol)
      
        # blit the map
      
        # blit objects, then items, then creatures, then the player, 
           
        # then blit weather. Weather is the only thing above players and creatures.



if __name__ == "__main__":
        
        parser = argparse.ArgumentParser(description='Cataclysm LD Client', epilog="Please start the client with a first and last name for your character.")
        parser.add_argument('--host', metavar='Host', help='Server host', default='localhost')
        parser.add_argument('-p', '--port', metavar='Port', type=int, help='Server port', default=6317)
        parser.add_argument('name', help='Player\'s name')
        
        args = parser.parse_args()
        ip = args.host
        port = args.port

        

        client = Client(args.name)
        client.connect(ip, port)

        

        command = Command(client.player.name, 'login', ['password'])
        client.send(command)
        command = Command(client.player.name, 'request_map')
        client.send(command)
        command = None
        
        def check_messages_from_server(dt, client):
            next_update = client.receive(False)
            
            if(next_update is not None):
                if(isinstance(next_update, Player)):
                    client.player = next_update # self.player is updated
                    print('updated player')
                elif(isinstance(next_update, dict)): 
                    client.chunk = next_update
                    print('updated map')

        clock.schedule(check_messages_from_server, client)
        
        
        pyglet.app.event_loop.run() # main event loop starts here.
        
