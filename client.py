
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
        pyglet.resource.path = ['tiles','tiles/background','tiles/monsters','tiles/terrain']
        pyglet.resource.reindex()
        ######################################################################################
        ## when we get an update from the server we update these values from the parsed chunk.
        self.name = name
        self.chunk_size = (51,27)
        self.player = None
        self.chunk = None
        self.map = None
        self.creatures = None
        self.objects = None
        self.map_grid = glooey.Grid(self.chunk_size[1], self.chunk_size[0], 16, 16) # chunk_size + tilemap size
        self.map_grid.set_left_padding(16) # for the border.
        self.map_grid.set_top_padding(16)
                
        for i in range(self.chunk_size[1]): # glooey uses y,x for grids from the top left.
            for j in range(self.chunk_size[0]):
                self.map_grid.add(i, j, glooey.images.Image(pyglet.resource.texture('t_grass.png'))) # before we get an update we need to init the map with grass.

        ######################################################################################

        window = pyglet.window.Window(854, 480)
        gui = glooey.Gui(window)
        
     
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
        gui.add(self.map_grid)
        

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == KEY.RETURN:
                print('return')
            if symbol == KEY.W:
                command = Command(args.name, 'move', ['north'])
                client.send(command)

    def convert_position_to_local_coords(self, position):
        x = position.x
        y = position.y

        while x >= self.chunk_size[0]:
            x = x - self.chunk_size[0]
        while y >= self.chunk_size[1]:
            y = y - self.chunk_size[1]
        
        return (x,y)

    def update_map(self):
        if(self.map is not None):
            for i in range(self.chunk_size[0]):
                for j in range(self.chunk_size[1]):
                    self.map_grid[j,i].set_image(pyglet.resource.texture(self.map[i][j].ident + '.png'))

            for furniture in self.furnitures:
                self.map_grid[j,i].Image = pyglet.resource.texture(furniture.ident)

            for creature in self.creatures:
                self.map_grid[j,i].Image = pyglet.resource.texture(creature.ident)
            for player in self.players:
                print('printing player')
                i, j = self.convert_position_to_local_coords(player.position)
                self.map_grid[j,i].set_image(pyglet.resource.texture(player.ident))
            
            print(pyglet.clock.get_fps())


                    
        else:
            print('had no map to draw')

            #TODO: lerp the positions of creatures from one frame to the next.
            #TODO: use the last ch_gridmpared to this chunk to lerp.
            
            # blit then items, then creatures, then the player, 
            
            # then blit weather. Weather is the only thing above players and creatures.
            
    
    def parse_chunk_data(self):
        self.map = self.chunk.map
        self.creatures = self.chunk.creatures
        self.furnitures = self.chunk.furnitures
        self.players = self.chunk.players
        for player in self.players:
            #print(player.name)
            if(player.name == self.name):
                self.player = player
                return
        else:
            print('couldn\'t find player in self.map')




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
       
        command = Command(args.name, 'login', ['password'])
        client.send(command)
        command = Command(args.name, 'request_chunk')
        client.send(command)
        command = None
        
        def check_messages_from_server(dt):
            next_update = client.receive(False)
            
            if(next_update is not None):
                if(isinstance(next_update, Player)):
                    client.player = next_update # self.player is updated
                    print('updated player')
                elif(isinstance(next_update, Chunk)): 
                    client.chunk = next_update
                    client.parse_chunk_data()
                    client.update_map()
                    print('updated chunk')
           
        
        def ping(dt):
            command = Command(client.player.name, 'ping')
            client.send(command)

        clock.schedule_interval(check_messages_from_server, 0.25)
        clock.schedule_interval(ping, 30.0) # our keep-alive event. without this the server would disconnect if we don't send data within the timeout for the server.
        
        
        pyglet.app.event_loop.run() # main event loop starts here.
        
