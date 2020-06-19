import datetime
import json
from enum import IntEnum


class RoomManager(object):
    def __init__(self):
        self.rooms = {}  # for now have dict of (k: v) room_id: BuzzerRoom

        self.max_inactive_seconds = 3600  # after an hour of inactivity the rooms get removed
        self._room_ids = None

    # @property
    # def room_ids(self):
    #     if not self._room_ids:
    #         self._room_ids = [room.id for room in self.rooms.values()]
    #     return self._room_ids

    def get_room(self, room_id):
        return self.rooms[room_id]

    def add_room_if_not_exists(self, room_id):
        if room_id not in self.rooms.keys():
            new_room = BuzzerRoom(id=room_id)
            self.rooms[new_room.id] = new_room

    def _delete_room(self, old_room):
        if isinstance(old_room, BuzzerRoom) and old_room.id in self.rooms.keys():
            del self.rooms[old_room.id]

    def cleanup_rooms(self):  # currently run every time a buzzer is reset, point is we just need to do it infrequently
        current_time = datetime.datetime.now().timestamp()
        to_delete = []
        for room in self.rooms.values():
            if room.last_active_time < current_time - self.max_inactive_seconds:
                to_delete.append(room)  # deleting whilst in the iterator could cause problems
        for r in to_delete:
            self._delete_room(r)

    def get_busiest_rooms(self, n=5):
        busiest_rooms = []
        for room in self.rooms.values():
            if len(busiest_rooms) < n:
                busiest_rooms.append(room)
                continue
            busiest_rooms = sorted(busiest_rooms, key=lambda x: x.n_players)
            if room.n_players > busiest_rooms[0].n_players:
                busiest_rooms.pop(0)
                busiest_rooms.append(room)
        return [room.id for room in busiest_rooms]


class BuzzerRoom(object):
    def __init__(self, id):
        self.id = id

        self.buzzes = []
        self.players = {}

        self.created_time = datetime.datetime.now().timestamp()
        self.last_active_time = datetime.datetime.now().timestamp()

        # default settings
        self.config = dict(correct_points=10,
                           early_incorrect_points=5,
                           sort_latency=1000,  # ms to wait before sorting people's buzzes -- this ensures fairness! time evaluated client-side
                           time_evaluation_method='server'
                           )

    @property
    def currently_buzzed_player_names(self):
        return [p['name'] for p in self.buzzes]

    @property
    def n_players(self):
        return len(self.players.keys())

    def update_last_changed_at(self):
        self.last_active_time = datetime.datetime.now().timestamp()

    def reset_buzzer(self):
        self.buzzes = []
        self.update_last_changed_at()

    def buzz(self, name, client_side_time, server_side_time):
        if name not in self.currently_buzzed_player_names:
            if self.config['time_evaluation_method'] == 'server':
                self.buzzes.append({'name': name, "time": server_side_time})
            elif self.config['time_evaluation_method'] == 'client':
                self.buzzes.append({'name': name, "time": client_side_time})
            elif self.config['time_evaluation_method'] == 'client_with_offset_correction':
                player = self.get_player(participant_name=name)
                adjusted_client_side_time = server_side_time - player.offset
                self.buzzes.append({'name': name, "time": adjusted_client_side_time})
                print('offset: {}'.format(player.offset))
            elif self.config['time_evaluation_method'] == 'another':
                if 'max' in name.lower():
                    server_side_time += 1
                self.buzzes.append({'name': name, "time": server_side_time})

    def mark_correct(self):
        if self.buzzes:
            self.players[self.buzzes.pop(0)['name']].score += self.config['correct_points']
        self.reset_buzzer()
        self.update_last_changed_at()

    def mark_standard_incorrect(self):
        if self.buzzes:
            self.buzzes.pop(0)
        self.update_last_changed_at()

    def mark_early_incorrect(self):
        if self.buzzes:
            self.players[self.buzzes.pop(0)['name']].score -= self.config['early_incorrect_points']
        self.update_last_changed_at()

    def add_player(self, participant_name):
        if participant_name not in self.players.keys():
            new_player = Player(name=participant_name)
            self.players[participant_name] = new_player

    def get_player(self, participant_name):
        return self.players[participant_name]

    def remove_player(self, participant_name):
        del self.players[participant_name]
        self.update_last_changed_at()

    def reset_all_scores(self):
        for player in self.players.values():
            player.score = 0

    def update_setting(self, key, value):
        if key in self.config.keys():
            self.config[key] = value
        self.update_last_changed_at()

    def get_scoreboard(self):
        scores = [dict(name=player.name, score=player.score) for player in self.players.values()]
        return sorted(scores, key=lambda x: x['score'], reverse=True)

    def sort_buzzes(self):
        return sorted(self.buzzes, key=lambda x: x['time'])

    def update_config(self, config):
        for key, value in config.items():
            if key in self.config.keys():
                self.config[key] = value

    def get_room_state(self):
        state = {}
        state['scoreboard'] = self.get_scoreboard()
        state['current_buzzes'] = self.sort_buzzes()
        state['config'] = self.config
        return json.dumps(state)


class Player(object):
    def __init__(self, name):
        self.name = name
        self.score = 0

        self.ping_offsets = []

    def add_ping_offset(self, offset, max_offsets=10):
        self.ping_offsets.append(offset)
        if len(self.ping_offsets) >= max_offsets:
            self.ping_offsets.pop(0)

    @property
    def offset(self):
        from numpy import average
        if len(self.ping_offsets) > 0:
            return average(self.ping_offsets)
        else:
            return 0
