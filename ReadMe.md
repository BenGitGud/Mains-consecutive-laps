
# Mains Consecutive Laps
`Best X Consecutive Races` class ranking plugin for RotorHazard

## Installation

Copy the `rank_best_consecutive_races` plugin into the `src/server/plugins` directory in your RotorHazard install. Start RotorHazard.

If installation is successful, the RotorHazard log will contain the message `Loaded plugin module rank_best_consecutive_races` at startup.

## Usage

__After creating a class, select "Best X Consecutive Races (Average)" for the class ranking method.__

This plugin is used to determine the best total times for a given amount of races.		
The race totals will also be factored only for completed races for a given amount of laps.

For example: 	
- `X` amount of consecutive laps for your best overall time		
- And then your best `Y` overall best times are what qualifies you for relevant mains (A,B,C,x,x,x)


### Example Input
`Best X Consecutive Races` Ranking Format

Settings:
- `Required number of laps (X)` (The required number of laps per race)
- `Number of races (Y)` (The amount of best overall races you want to use to determine ranking)


## Leaderboard Example

| **Rank** | **Pilot Callsign** | **Best 3 Races (Total Time)** | **Races Counted** |
|----------|--------------------|-------------------------------|-------------------|
| 1        | Pilot 4            | 1:30.000                      | 3                 |
| 2        | Pilot 1            | 1:40.000                      | 3                 |
| 3        | Pilot 6            | 1:45.000                      | 3                 |
| 4        | Pilot 2            | 2:15.000                      | 3                 |
| 5        | Pilot 3            | 2:30.000                      | 3                 |
| 6        | Pilot 5            | 2:45.000                      | 3                 |

>__Note:__ If not enough pilots have completed the minimum amount of laps + minimum amount of races then 
> the output of the class ranking will be empty until the given leaderboard settings have been met.
## Grouping of Mains
Use the generator function 	
- Input: Qualifying Class (Where the results to be used for mains grouping is)		
- Output: Finals Class (Where the pilots will be seeded into mains)

Then use the ranked fill function to seed your mains (A,B,C,etc...)

> __Note:__ Utilize the `Maximum pilots per heat` field to sort by the amount of pilots you want per main.
