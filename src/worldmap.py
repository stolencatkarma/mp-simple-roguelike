import json
import os
import pickle
import random
import time

from src.terrain import Terrain
from src.creature import Creature
from src.item import Item
from src.position import Position


class Chunk:
    def __init__(self, x, y, chunk_size): # x, y relate to it's position on the world map.
        #print(chunk_size)
        self.is_dirty = True # set this to true to have the changes updated on the disk, default is True so worldgen writes it to disk
        self.was_loaded = 'no'
        self.map = dict()
        for i in range(chunk_size[0]):
            self.map[i] = dict()
            for j in range(chunk_size[1]): 
                self.map[i][j] = Terrain('t_grass', Position((x * chunk_size[0]) + i, (y * chunk_size[1]) + j))

        self.creatures = list() # individual x, y
        self.items = list() # grabable items individual x, y
        self.furnitures = list() # doors, altars, etc. individual x, y
        self.players = list() # current active players on this chunk individual x, y
       

class Worldmap:
    def move_object_from_position_to_position(self, obj, obj_position, position):
        pass

    # let's make the world map and fill it with rooms!
    def __init__(self, WORLD_SIZE): # size in chunks along one axis.
        self.WORLDMAP = dict() # dict of dicts for chunks
        self.chunk_size = (51,27) # size of the chunk, leave it hardcoded here. 
        self.WORLD_SIZE = WORLD_SIZE
        start = time.time()
        #TODO: only need to load the chunks where there are actual players present in memory after generation.
        print('creating/loading world chunks')
        for i in range(self.WORLD_SIZE):
            self.WORLDMAP[i] = dict()
            for j in range(self.WORLD_SIZE):
                # self.WORLDMAP[i][j] = dict()
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
        for _, x in self.WORLDMAP.items():
            for _, chunk in x.items(): 
                chunks.append(chunk)
        return chunks

    def get_player(self, name):
        for chunk in self.get_all_chunks():
            for player2 in chunk.players:
                if(player2.name == name):
                    return player2
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
        x = int(position.x / self.chunk_size[0])
        y = int(position.y / self.chunk_size[1])

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
        layout = data['layout']
        #print(floors)
        terrain = data['terrain'] # list
        fill_terrain = data['fill_terrain'] # string

        i, j = 0, 0
        for row in layout:
            i = 0
            for char in row:
                #print(char)
                #print(terrain)
                t_position = Position(position.x + i, position.y + j)
                if char in terrain:
                    self.put_object_at_position(Terrain(terrain[char], t_position), t_position)
                else:
                    self.put_object_at_position(Terrain(fill_terrain, t_position), t_position) # use fill_terrain if unrecognized.
                    pass
                i = i + 1
            j = j + 1
        #end = time.time()
        #duration = end - start
        #print('Building '+ str(filename) + ' took: ' + str(duration) + ' seconds.')

    def put_object_at_position(self, obj, position): # attempts to take any object (creature, item, etc.) and put it in the right spot in the WORLDMAP
        #TODO: check if something is already there. right now it just replaces it
        chunk = self.get_chunk_by_position(position)
        chunk.is_dirty = True
        #print(tile)

        if isinstance(obj, Creature):
            chunk.creatures.append(obj)
            return
        elif isinstance(obj, Terrain):
            ter = self.get_terrain_by_position(position)
            ter.ident = obj.ident
            return

        elif isinstance(obj, Item):
            chunk.items.append(obj)
            return
    
    def get_terrain_by_position(self, position):
        #print('Looking for position: ' + str(position))
        x_count = 0 #
        x = position.x
        while(x >= self.chunk_size[0]):
            x = x - self.chunk_size[0]
            x_count = x_count + 1

        y_count = 0 #
        y = position.y
        # worldmap[x][y].tiles
        while(y >= self.chunk_size[1]):
            y = y - self.chunk_size[1]
            y_count = y_count + 1


        chunk = self.get_chunk_by_position(position)

        for _, x in chunk.map.items():
            #print(_x)
            for _, terrain in x.items(): 
                #print(terrain.position)
                if(terrain.position == position):
                    return terrain
        else:
            print('FATAL ERROR: couldn\'t find', position, 'anywhere.')



    
    def generate_city(self, size):
        size = int(size * 12) # multiplier
        # this function creates a overmap that can be translated to build json buildings.
        # size is 1-10
        city_layout = dict()
        for i in range(size):
            city_layout[i] = dict()
            for j in range(size):
                city_layout[i][j] = '.' # . is grass or nothing

        # first place roads along the center lines of the city
        for tile in range(size):
            city_layout[int(size/2)][tile] = 'R'
            city_layout[tile][int(size/2)] = 'R'


        #figure out how many buildings of each we need to build
        num_buildings = size*size # size squared.
        num_residential = int(num_buildings/2 * 0.34) # 34% percent of the total tiles are residential.
        num_commercial = int(num_buildings/2 * 0.22)
        num_industrial = int(num_buildings/2 * 0.22)

        num_hospitals = int(size / 12)
        num_police = int(size / 12)
        num_firedept = int(size / 12)
        num_jail = int(size / 12)

        #print('num_residential: ' + str(num_residential))
        #print('num_commercial: ' + str(num_commercial))
        #print('num_industrial: ' + str(num_industrial))
        #print('num_hospitals: ' + str(num_hospitals))
        #print('num_police: ' + str(num_police))
        #print('num_firedept: ' + str(num_firedept))
        #print('num_jail: ' + str(num_jail))


        # put road every 4th tile with houses on either side.
        for j in range(1, size-1):
            for i in range(random.randrange(0, 2), size - int(random.randrange(0, 2))): # draw horizontal lines.
                if i == int(size/2):
                    continue # don't overwrite the middle road.

                if j % 2 == 0:
                    city_layout[i][j] = 'R'
                else:
                    if(random.randrange(0, 10) == 0):
                        city_layout[i][j] = 'R' #rarely build a road between roads.
                        continue
                    city_layout[i][j] = 'B' # else build a building.

                #if we have a building to build
                if(city_layout[i][j] == 'B'):
                    if(num_residential > 0):
                        city_layout[i][j] = 'r'
                        num_residential = num_residential - 1
                    elif(num_commercial > 0):
                        city_layout[i][j] = 'c'
                        num_commercial = num_commercial - 1
                    elif(num_industrial > 0):
                        city_layout[i][j] = 'i'
                        num_industrial = num_industrial - 1
                    elif(num_hospitals > 0):
                        city_layout[i][j] = 'H'
                        num_hospitals = num_hospitals - 1
                    elif(num_jail > 0):
                        city_layout[i][j] = 'J'
                        num_jail = num_jail - 1
                    elif(num_police > 0):
                        city_layout[i][j] = 'P'
                        num_police = num_police - 1
                    elif(num_firedept > 0):
                        city_layout[i][j] = 'F'
                        num_firedept = num_firedept - 1


        #if we haven't placed our city services we need to go back and add them.
        while(num_police > 0 or num_firedept > 0 or num_jail > 0 or num_hospitals > 0):
            i = random.randrange(1, size-1)
            j = random.randrange(1, size-1)

            if(city_layout[i][j] != 'R'):
                if(num_police > 0):
                    city_layout[i][j] = 'P'
                    num_police = num_police - 1
                elif(num_firedept > 0):
                    city_layout[i][j] = 'F'
                    num_firedept = num_firedept - 1
                elif(num_jail > 0):
                    city_layout[i][j] = 'J'
                    num_jail = num_jail - 1
                elif(num_hospitals > 0):
                    city_layout[i][j] = 'H'
                    num_hospitals = num_hospitals - 1


        for j in range(size):
            for i in range(size):
                #print(str(city_layout[i][j]), end = '') # the visual feedback on the console.
                pass
            print()

        return city_layout

        