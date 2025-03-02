import logging
import RHUtils
from eventmanager import Evt
from RHRace import StartBehavior
from Results import RaceClassRankMethod
from RHUI import UIField, UIFieldType, UIFieldSelectOption

logger = logging.getLogger(__name__)

# New function for ranking by the best 3 consecutive races
def rank_best_consecutive_races(rhapi, race_class, args):
    if 'races' not in args or not args['races'] or int(args['races']) < 1:
        return False, {}

    race_limit = int(args['races'])

    race_format = rhapi.db.raceformat_by_id(race_class.format_id)
    heats = rhapi.db.heats_by_class(race_class.id)

    combined_races = {}

    # Loop through heats and races, collecting lap times for pilots
    for heat in heats:
        races = rhapi.db.races_by_heat(heat.id)

        for race in races:
            runs = rhapi.db.pilotruns_by_race(race.id)

            for run in runs:
                if run.pilot_id not in combined_races:
                    combined_races[run.pilot_id] = []
    
                start_lap = 2 if race_format and race_format.start_behavior == StartBehavior.STAGGERED else 1
    
                laps = rhapi.db.laps_by_pilotrun(run.id)
                laps = [x for x in laps if not x.deleted]  # Remove deleted laps
            
                for lap in laps[start_lap:]:
                    combined_races[run.pilot_id].append(lap)
                else:
                logger.warning("Failed building ranking, race result not available")
                return False, {}  

    # Ranking pilots based on their best 3 consecutive races
    leaderboard = []
    for pilot_id, laps in combined_races.items():
        pilot = rhapi.db.pilot_by_id(pilot_id)
        if pilot:
            new_pilot_result = {}
            new_pilot_result['pilot_id'] = pilot.id
            new_pilot_result['callsign'] = pilot.callsign
            new_pilot_result['team_name'] = pilot.team

            # Sort laps by lap time
            laps = sorted(laps, key=lambda x: x.lap_time)
            
            # Calculate the fastest 3 consecutive races
            best_consecutive_races = []
            for i in range(len(laps) - race_limit + 1):
                consecutive_races = laps[i:i + race_limit]
                total_time = sum(lap.lap_time for lap in consecutive_races)
                best_consecutive_races.append((total_time, consecutive_races))
            
            # Sort by the best total time for the 3 consecutive races
            best_consecutive_races.sort(key=lambda x: x[0])
            
            if best_consecutive_races:
                fastest_consecutive = best_consecutive_races[0]  # Select the best set of consecutive races
                new_pilot_result['total_time_races_raw'] = fastest_consecutive[0]
                new_pilot_result['avg_time_races_raw'] = int(new_pilot_result['total_time_races_raw'] / float(len(fastest_consecutive[1])))
                new_pilot_result['races_base'] = len(fastest_consecutive[1])
                new_pilot_result['avg_time_races'] = rhapi.utils.format_time_to_str(new_pilot_result['avg_time_races_raw'])

                leaderboard.append(new_pilot_result)

    # Sort the leaderboard based on the total time for the best 3 consecutive races
    leaderboard = sorted(leaderboard, key=lambda x: (x['races_base'], x['avg_time_races_raw']))

    # Assign positions (ranking)
    last_rank = None
    last_rank_races = 0
    last_rank_time = 0
    for i, row in enumerate(leaderboard, start=1):
        pos = i
        if last_rank_races == row['races_base'] and last_rank_time == row['avg_time_races_raw']:
            pos = last_rank
        last_rank = pos
        last_rank_races = row['races_base']
        last_rank_time = row['avg_time_races_raw']

        row['position'] = pos

    # Group pilots into heats
    num_pilots_per_heat = args.get('pilots_per_heat', 4)  # Default to 4 pilots per heat
    heats = group_pilots_into_heats(leaderboard, num_pilots_per_heat)

    meta = {
        'method_label': F"Best {race_limit} Consecutive Races",
        'rank_fields': [{
            'name': 'avg_time_races',
            'label': F"{race_limit}-Race Average"
        }, {
            'name': 'races_base',
            'label': "Base"
        }]
    }

    return heats, meta

# Group pilots into heats based on their ranking
def group_pilots_into_heats(pilots, pilots_per_heat):
    heats = []
    current_heat = []

    for index, pilot in enumerate(pilots):
        current_heat.append(pilot)
        if len(current_heat) == pilots_per_heat or index == len(pilots) - 1:
            heats.append(current_heat)
            current_heat = []

    return heats

def register_handlers(args):
    args['register_fn'](
        RaceClassRankMethod(
            "Best X Consecutive Races (Average)",
            rank_best_consecutive_races,
            {
                'races': 3,
                'pilots_per_heat': 4  # Default 4 pilots per heat
            },
            [
                UIField('races', "Number of races", UIFieldType.BASIC_INT, placeholder="3"),
                UIField('pilots_per_heat', "Pilots per heat", UIFieldType.BASIC_INT, placeholder="4"),
            ]
        )
    )

def initialize(rhapi):
    rhapi.events.on(Evt.CLASS_RANK_INITIALIZE, register_handlers)
