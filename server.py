import json
import os
import random
import sys
import time

from src.worldmap import Worldmap
from src.position import Position
from src.calendar import Calendar
from src.command import Command
from src.action import Action
from src.item import Item, ItemManager
from src.player import Player

from Mastermind._mm_server import MastermindServerTCP


class Server(MastermindServerTCP):
    def __init__(self):
        MastermindServerTCP.__init__(self, 0.25, 0.25, 300.0)
        self.calendar = Calendar(0, 0, 0, 0, 0, 0) # all zeros is the epoch
        self.worldmap = Worldmap(13) # create this many chunks in x and y for genning the world.

    def callback_client_handle(self, connection_object, data):
        #print("Server: Recieved data \""+str(data)+"\" from client \""+str(connection_object.address)+"\".")
        # use the data to determine what player is giving the command and if they are logged in yet.

        if(isinstance(data, Command)): # the data we recieved was a command. process it.
            if(data.command == 'login'):
                if(data.args[0] == 'password'): # TODO: put an actual password system in.
                    print('password accepted for ' + str(data.ident))
                    tmp_player = self.worldmap.get_player(data.ident) # by 'name'
                    if(tmp_player is not None): # player exists
                        print('player exists. loading.')
                        player.connection_object = connection_object
                    else:
                        print('player doesnt exist yet.')
                        tmp_player = Player(2,2,connection_object, str(data.ident))
                        self.worldmap.add_player_to_worldmap(tmp_player, Position(2,2))
                        

                    print('Player ' + str(data.ident) + ' entered the world at position ' + str(tmp_player.position))
                    self.callback_client_send(connection_object, tmp_player)
                else:
                    print('password not accepted.')
                    connection_object.disconnect()

            # all the commands that are actions need to be put into the command_queue then we will loop through the queue each turn and process the actions.
            if(data.command == 'move'):
               tmp_player.command_queue.append(Action(tmp_player, 'move', [data.args[0]]))

            if(data.command == 'request_map'):
                # find the chunk the player is on and send it to them.
                print('player wants a map update.')
                tmp_chunk = self.worldmap.get_chunk_by_player(data.ident)
                player_map = tmp_chunk.map
                self.callback_client_send(connection_object, player_map)

           
            if(data.command == 'move_item'):
                # client sends 'hey server. can you move this item from this to that?'
                _player_requesting = tmp_player
                _item = data.args[0] # the item we are moving.
                _from_type = data.args[1] # creature.held_item, creature.held_item.container, bodypart.equipped, bodypart.equipped.container, position, blueprint
                _from_list = [] # the object list that contains the item. parse the type and fill this properly.
                _to_list = data.args[2] # the list the item will end up. passed from command.
                _position = Position(data.args[3], data.args[4]) # pass the position even if we may not need it.

                ### possible move types ###
                # creature(held) to creature(held) (give to another player)
                # creature(held) to position(ground) (drop)
                # creature(held) to bodypart (equip)
                # bodypart to creature(held) (unequip)
                # bodypart to position (drop)

                # position to creature(held) (pick up from ground)
                # position to bodypart (equip from ground)
                # position to position (move from here to there)

                # creature to blueprint (fill blueprint)

                # blueprint to position (empty blueprint on ground)
                # blueprint to creature (grab from blueprint)

        return super(Server,self).callback_client_handle(connection_object,data)

    def callback_client_send(self, connection_object, data, compression=True):
        #print("Server: Sending data \""+str(data)+"\" to client \""+str(connection_object.address)+"\" with compression \""+str(compression)+"\"!")
        return super(Server, self).callback_client_send(connection_object, data, compression)

    def callback_connect_client(self, connection_object):
        print("Server: Client from \""+str(connection_object.address)+"\" connected.")
        return super(Server, self).callback_connect_client(connection_object)

    def callback_disconnect_client(self, connection_object):
        print("Server: Client from \""+str(connection_object.address)+"\" disconnected.")
        return super(Server, self).callback_disconnect_client(connection_object)

    def process_creature_command_queue(self, creature):
        actions_to_take = creature.actions_per_turn
        for action in creature.command_queue[:]: # iterate a copy so we can remove on the fly.
            if(actions_to_take == 0):
                return # this creature is out of action points.

            if(creature.next_action_available > 0): # this creature can't act until x turns from now.
                creature.next_action_available = creature.next_action_available - 1
                return

            # if we get here we can process a single action
            if(action.action_type == 'move'):
                actions_to_take = actions_to_take - 1 # moving costs 1 action point.
                if(action.args[0] == 'south'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x, creature.position.y+1))):
                        creature.position = Position(creature.position.x, creature.position.y+1)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'north'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x, creature.position.y-1))):
                        creature.position = Position(creature.position.x, creature.position.y-1)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'east'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x+1, creature.position.y))):
                        creature.position = Position(creature.position.x+1, creature.position.y)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'west'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x-1, creature.position.y))):
                        creature.position = Position(creature.position.x-1, creature.position.y)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'up'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x, creature.position.y+1))):
                        creature.position = Position(creature.position.x, creature.position.y+1)
                    creature.command_queue.remove(action) # remove the action after we process it.
                if(action.args[0] == 'down'):
                    if(self.worldmap.move_object_from_position_to_position(creature, creature.position, Position(creature.position.x, creature.position.y-1))):
                        creature.position = Position(creature.position.x, creature.position.y-1)
                    creature.command_queue.remove(action) # remove the action after we process it.

    # this function handles overseeing all creature movement, attacks, and interactions
    def compute_turn(self):
        # each chunk in the worldmap with active players needs to be updated.
        creatures_to_compute = list()
        for _, x in self.worldmap.WORLDMAP.items():
            for _, chunk in x.items(): 
                for i, x in chunk.map.items():
                    for j, terrain in x.items():
                        terrain.light_levels = 1 # reset light levels.
                for creature in chunk.players:
                    creatures_to_compute.append(creature)
                for creature in chunk.creatures:
                    creatures_to_compute.append(creature)


        for creature in creatures_to_compute:
            if(len(creature.command_queue) > 0): # as long as there at least one we'll pass it on and let the function handle how many actions they can take.
                print('doing actions for: ' + str(creature.name))
                self.process_creature_command_queue(creature)
                if(isinstance(creature, Player)):
                    self.callback_client_send(creature.connection_object, self.worldmap.get_chunk_by_position(creature.position))
        
        # we need a way to auto update the players each turn
            
            
        # now that we've processed what everything wants to do we can return.

    def generate_and_apply_city_layout(self, city_size):
        city_layout = self.worldmap.generate_city(city_size) 
        # for every 1 city size it's 12 tiles across and high
        for j in range(city_size*12):
            for i in range(city_size*12):
                if(server.worldmap.get_chunk_by_position(Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1)).was_loaded == 'no'):
                    if(city_layout[i][j] == 'r'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/residential/'))
                        server.worldmap.build_json_building_at_position('./data/json/mapgen/residential/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1))
                    elif(city_layout[i][j] == 'c'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/commercial/'))
                        server.worldmap.build_json_building_at_position('./data/json/mapgen/commercial/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1))
                    elif(city_layout[i][j] == 'i'):
                        json_file = random.choice(os.listdir('./data/json/mapgen/industrial/'))
                        server.worldmap.build_json_building_at_position('./data/json/mapgen/industrial/' + json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1))
                    elif(city_layout[i][j] == 'R'): # complex enough to choose the right rotation.
                        attached_roads = 0
                        try:
                            if(city_layout[int(i-1)][int(j)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i+1)][int(j)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i)][int(j-1)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(city_layout[int(i)][int(j+1)] == 'R'):
                                attached_roads = attached_roads + 1
                            if(attached_roads == 4):
                                json_file = './data/json/mapgen/road/city_road_4_way.json'
                            elif(attached_roads == 3): #TODO: make sure the roads line up right.
                                if(city_layout[int(i+1)][int(j)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_s0.json'
                                elif(city_layout[int(i-1)][int(j)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_p0.json'
                                elif(city_layout[int(i)][int(j+1)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_d0.json'
                                elif(city_layout[int(i)][int(j-1)] != 'R'):
                                    json_file = './data/json/mapgen/road/city_road_3_way_u0.json'
                            elif(attached_roads <= 2):
                                if(city_layout[int(i+1)][int(j)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_h.json'
                                elif(city_layout[int(i-1)][int(j)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_h.json'
                                elif(city_layout[int(i)][int(j+1)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_v.json'
                                elif(city_layout[int(i)][int(j-1)] == 'R'):
                                    json_file = './data/json/mapgen/road/city_road_v.json'
                            server.worldmap.build_json_building_at_position(json_file, Position(i * server.worldmap.chunk_size + 1 , j * server.worldmap.chunk_size + 1))
                        except:
                            #TODO: fix this blatant hack to account for coordinates outside the city layout.
                            pass

# do this if the server was started up directly.
if __name__ == "__main__":
   
    ip = '127.0.0.1'
    port = 6317

    server = Server()
    server.connect(ip, port)
    server.accepting_allow()
    server.generate_and_apply_city_layout(1)
    
    time_offset = 0.25 # 0.5 is twice as fast, 2.0 is twice as slow
    last_turn_time = time.time()
   

    print('Started up Mutiplayer Roguelike Work in Progress with no definitive Title.. Yet...')
    while True:
        try:
            
            while(time.time() - last_turn_time < time_offset): # try to keep up with the time offset but never go faster than it.
                time.sleep(.01)
            server.calendar.advance_time_by_x_seconds(1) # a turn is one second.
            server.compute_turn() # where all queued creature actions get taken care of, as well as physics engine stuff.
            #print('turn: ' + str(server.calendar.get_turn()))
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            #TODO: unload from memory chunks that have no updates required. (such as no monsters, players, or fires)
            last_turn_time = time.time() # based off of system clock.
        except KeyboardInterrupt:
            print('cleaning up before exiting.')
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            print('done cleaning up.')
            break
        except Exception as e:
            print('!! Emergency Exit due to Server Exception. !!')
            print(e)
            print()
            server.accepting_disallow()
            server.disconnect_clients()
            server.disconnect()
            server.worldmap.update_chunks_on_disk() # if the worldmap in memory changed update it on the hard drive.
            sys.exit()
