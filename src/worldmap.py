import json
import os
import pickle
import random
import time

from .terrain import Terrain
from .creature import Creature
from .item import Item
from .position import Position


class Chunk:
    def __init__(self, x, y, chunk_size): # x, y relate to it's position on the world map.
        self.is_dirty = True # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self.was_loaded = 'no'
        self.map = dict()
        for i in range(chunk_size): # 0-13
            self.map[i] = dict()
            for j in range(chunk_size): # 0-13
                self.map[i][j] = Terrain(i*x, j*y)
        self.creatures = list() # individual x, y
        self.items = list() # grabable items individual x, y
        self.objects = list() # doors, altars, etc. individual x, y
        self.players = list() # current active players on this chunk individual x, y
       

class Worldmap:
    # let's make the world map and fill it with rooms!

    def __init__(self, WORLD_SIZE): # size in chunks along one axis.
        self.WORLDMAP = dict() # dict of dicts for chunks
        self.chunk_size = 24 # size of the chunk, leave it hardcoded here. 
        self.WORLD_SIZE = WORLD_SIZE
        start = time.time()
        #TODO: only need to load the chunks where there are actual players present in memory after generation.
        print('creating/loading world chunks')
        for i in range(self.WORLD_SIZE):
            self.WORLDMAP[i] = dict()
            for j in range(self.WORLD_SIZE):
                self.WORLDMAP[i][j] = dict()
                path = str('./worlds/default/' + str(i) + '_' + str(j) + '.chunk') #TODO: allow other folders.

                if(os.path.isfile(path)): # if the chunk already exists on disk just load it.
                    with open(path, 'rb') as fp:
                        self.WORLDMAP[i][j] = pickle.load(fp)
                        self.WORLDMAP[i][j].was_loaded = 'yes'
                else:
                    self.WORLDMAP[i][j] = Chunk(i, j, self.chunk_size)
                    with open(path, 'wb') as fp:
                        pickle.dump(self.WORLDMAP[i][j], fp)

        end = time.time()
        duration = end - start
        print()
        print('---------------------------------------------')
        print('World generation took: ' + str(duration) + ' seconds.')

    def update_chunks_on_disk(self): # after our map in memory changes we need to update the chunk file on disk.
       for i, x in self.WORLDMAP.items():
            for j, chunk in x.items(): 
                path = str('./worlds/default/' + str(i) + '_' + str(j) + '.chunk')
                if(os.path.isfile(path)):
                    if(chunk.is_dirty):
                        with open(path, 'wb') as fp:
                            #print(str(i) + '_' + str(j) + '.chunk is_dirty. Saving changes to disk.')
                            self.WORLDMAP[i][j].is_dirty = False
                            pickle.dump(self.WORLDMAP[i][j], fp)
    
    def get_all_chunks(self):
        chunks = list()
        for i, x in self.WORLDMAP.items():
            for j, chunk in x.items(): 
                chunks.append(chunk)
        return chunks

    def get_player(self, player):
        for chunk in self.get_all_chunks():
            for player2 in chunk.players:
                if(player2.name == player):
                    return player
        else:
            return None

    def get_chunk_by_player(self, player):
        for chunk in self.get_all_chunks():
             for player2 in chunk.players:
                if(player2.name == player):
                    return chunk
        else:
            return None
    
    def add_player_to_worldmap(self, tmp_player, position):
        self.get_chunk_by_position(position).players.append(tmp_player)
        

    def get_chunk_by_position(self, position):
        x = int(position.x / self.chunk_size)
        y = int(position.y / self.chunk_size)

        return self.WORLDMAP[x][y]
    
    


    def build_json_building_at_position(self, filename, position): # applys the json file to world coordinates. can be done over multiple chunks.
        print('building: ' + str(filename) + ' at ' + str(position))
        #start = time.time()
        #TODO: fill the chunk overmap tile with this om_terrain
        with open(filename) as json_file:
            data = json.load(json_file)
        #print(data)
        # group = data['group']
        # overmap_terrain = data['overmap_terrain']
        floors = data['floors']
        #print(floors)
        terrain = data['terrain'] # list
        fill_terrain = data['fill_terrain'] # string

        impassable_tiles = ['t_wall'] # TODO: make this global
        for k, floor in floors.items():
            #print(k)
            i, j = 0, 0
            for row in floor:
                i = 0
                for char in row:
                    #print(char)
                    #print(terrain)
                    impassable = False
                    t_position = Position(position.x + i, position.y + j)
                    self.put_object_at_position(Terrain(fill_terrain, impassable), t_position) # use fill_terrain if unrecognized.
                    if char in terrain:
                        #print('char in terrain')
                        if terrain[char] in impassable_tiles:
                            impassable = True
                        #print('placing: ' + str(terrain[char]))
                        self.put_object_at_position(Terrain(terrain[char], impassable), t_position)
                    else:
                        #print('placed : ' + str(fill_terrain))
                        pass
                    i = i + 1
                j = j + 1
        #end = time.time()
        #duration = end - start
        #print('Building '+ str(filename) + ' took: ' + str(duration) + ' seconds.')
