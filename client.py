
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
        ''' when we get an update from the server we update these values from the parsed chunk. '''
        self.name = ''
        self.player = None
        self.chunk = None
        self.map = None
        self.creatures = None
        self.objects = None



        window = pyglet.window.Window(854, 480)
        gui = glooey.Gui(window)
        pyglet.resource.path = ['tiles','tiles/background','tiles/monsters','tiles/terrain']
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
        #TODO: use the last chunk compared to this chunk to lerp.
        
        # blit objects, then items, then creatures, then the player, 
           
        # then blit weather. Weather is the only thing above players and creatures.
        pass
    
    def parse_chunk_data(self):
        self.map = self.chunk.map
        self.creatures = self.chunk.creatures
        self.objects = self.chunk.objects
        self.players = self.chunk.players
        for player in self.players:
            if(player.name == self.name):
                self.player = player




if __name__ == "__main__":
        
        parser = argparse.ArgumentParser(description='Cataclysm LD Client', epilog="Please start the client with a first and last name for your character.")
        parser.add_argument('--host', metavar='Host', help='Server host', default='localhost')
        parser.add_argument('-p', '--port', metavar='Port', type=int, help='Server port', default=6317)
        parser.add_argument('name', help='Player\'s name')
        
        args = parser.parse_args()
        ip = args.host
        port = args.port

        client = Client(args.name)
        _name = input('What is your name?')
        client.connect(ip, port)
       
        command = Command(_name, 'login', ['password'])
        client.send(command)
        command = Command(_name, 'request_chunk')
        client.send(command)
        command = None
        
        def check_messages_from_server(dt):
            next_update = client.receive(False)
            
            if(next_update is not None):
                if(isinstance(next_update, Player)):
                    client.player = next_update # self.player is updated
                    print('updated player')
                elif(isinstance(next_update, dict)): 
                    client.chunk = next_update
                    self.parse_chunk_data()
                    print('updated chunk')
            
            return
        
        def ping(dt):
            command = Command(client.player.name, 'ping')
            client.send(command)

        clock.schedule_interval(check_messages_from_server, 0.25)
        clock.schedule_interval(ping, 30.0)
        
        
        pyglet.app.event_loop.run() # main event loop starts here.
        
