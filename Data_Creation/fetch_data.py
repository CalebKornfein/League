from riotwatcher import LolWatcher, ApiError, RiotWatcher
from env_vars import riot_key
from collections import defaultdict, Counter
import pandas as pd
import tqdm
import random
import csv
from itertools import product

# Note, much help for code was taken from this amazing resource: https://github.com/Hab5/league-machine-learning/blob/main/PipelineAPI.py

def fetch_challenger_puuids(watcher):
    region = "NA1"
    queue = 'RANKED_SOLO_5x5'
    challenger_league = watcher.league.challenger_by_queue(region, queue)
    challenger_players = [summoner['summonerId'] for summoner in challenger_league["entries"]]
    
    def fetch_puuid(player):
        try:
            puuid = watcher.summoner.by_id(region, player)["puuid"]
            return puuid
        except Exception as e:
            return "ERROR"
    
    puuids = []
    
    for player in tqdm.tqdm(challenger_players, desc = 'tqdm() Progress Bar'):
        puuid = fetch_puuid(player)
        if puuid != "ERROR":
            puuids.append(puuid)
            
    return puuids

def fetch_matchIDs(watcher, puuids):
    region="AMERICAS"
    queue = 420
    matchIDs = set()
    
    for id in tqdm.tqdm(puuids, desc = 'tqdm() Progress Bar'):
        try:
            matchIDs.update(watcher.match.matchlist_by_puuid(puuid = id, 
                                                             region = region,
                                                             queue = queue,
                                                             count = 100))
        except Exception as e:
            pass
    
    return list(matchIDs)

def fetch_gameinfo(watcher, matchID):
    region = "AMERICAS"
    
    try:
        game = watcher.match.by_id(region, matchID)
        timeline = watcher.match.timeline_by_match(region, matchID)
        frames = timeline["info"]["frames"]
        
        ### Define Players
        
        players= defaultdict(lambda: dict())
        for player in timeline["info"]["participants"]:
            players[player['puuid']]['participantId'] = player['participantId']
            players[player['puuid']]['kills'] = []
        
        reverse_players = {v['participantId']: k for k, v in players.items()} 
        
        ### Find roles of players and win status
        
        for player in game["info"]["participants"]:
            players[player["puuid"]]["win"] = player["win"]
            players[player["puuid"]]["position"] = player["teamPosition"]
        
        ### Fetch gold at 15 minutes for each player
        fifteen = frames[15]["participantFrames"]
        for participantID, status_dict in fifteen.items():
            players[reverse_players[int(participantID)]]["Gold"] = status_dict['totalGold']
        
        ### Fetch kills for each player by rolling through frames
        for frame in frames[:16]:
                for event in frame['events']:
                    if event['type'] == 'CHAMPION_KILL':
                        if event['killerId'] == 0:
                            # ignore case when participant is killed by minions
                            continue
                        players[reverse_players[event['killerId']]]['kills'].append(event['victimId'])                
        
        ### Consolidate Kills
        for player in players:
            kills = Counter([players[reverse_players[id]]['position'] for id in players[player]['kills']])
            players[player]['kills'] = defaultdict(lambda: 0)
            for lane, num_kills in kills.items():
                players[player]['kills'][lane] = num_kills
        
        ### Map teams and roles to players
        
        roles = {}
        for player, player_values in players.items():
            position = player_values['position']
            if player_values['win'] == True:
                roles[position + '1'] = player
            else:
                roles[position + '2'] = player
                
        ### Calculate all team1 stats:
        team1 = ['TOP1', 'JUNGLE1', 'MIDDLE1', 'BOTTOM1', 'UTILITY1']
        team2 = ['TOP2', 'JUNGLE2', 'MIDDLE2', 'BOTTOM2', 'UTILITY2']

        consolidated_stats = {}
        
        for role in team1 + team2:
            consolidated_stats[f'{role}_GOLD'] = players[roles[role]]['Gold'] 
        
        for p1, p2 in product(team1, team2):
            key = f'{p1}_{p2}'
            consolidated_stats[key] = players[roles[p1]]['kills'][p2[:-1]]    
        
        for p1, p2 in product(team2, team1):
            key = f'{p1}_{p2}'
            consolidated_stats[key] = players[roles[p1]]['kills'][p2[:-1]]  
            
        return consolidated_stats    
    except Exception as e:
        print(e)
        return 'ERROR'

def fetch_matches(watcher, matches):
    
    def write_csv(data):
        with open('Data/Matches.csv', 'a') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(data)
    
    team1 = ['TOP1', 'JUNGLE1', 'MIDDLE1', 'BOTTOM1', 'UTILITY1']
    team2 = ['TOP2', 'JUNGLE2', 'MIDDLE2', 'BOTTOM2', 'UTILITY2']
    
    gold = [f'{role}_GOLD' for role in team1 + team2]
    team1keys = [f'{p1}_{p2}' for p1, p2 in product(team1, team2)]
    team2keys = [f'{p1}_{p2}' for p1, p2 in product(team2, team1)]
    
    keys = gold + team1keys + team2keys
    write_csv(keys)
    
    for matchID in tqdm.tqdm(matches, desc = 'tqdm() Progress Bar'):
        stats = fetch_gameinfo(watcher, matchID)
        
        if stats == 'ERROR': continue
        
        ordered_stats = [stats[key] for key in keys]
        write_csv(ordered_stats)
        
    
def main():
    # Load API Key and set variables
    key = riot_key()
    watcher = LolWatcher(key)
    
    # Fetch Challenger IDs and write them to a csv
    #challenger_puuids = pd.DataFrame(fetch_challenger_puuids(watcher), columns = ['Puuid'])
    #challenger_puuids.to_csv('Data/Puuids.csv', index=False)
    
    # Fetch Match IDs given Challenger IDs
    #challenger_puuids = pd.read_csv('Data/Puuids.csv')
    #challenger_matches = fetch_matchIDs(watcher, list(challenger_puuids['Puuid'].values))
    #random.shuffle(challenger_matches)
    #challenger_matches = pd.DataFrame(challenger_matches, columns = ['MatchID'])
    #challenger_matches.to_csv('Data/MatchIDs.csv', index=False)
    
    # Fetch data for each Match given their IDs
    matchIDs = pd.read_csv('Data/MatchIDs.csv')
    matchinfo = fetch_matches(watcher, list(matchIDs['MatchID'].values))
    
if __name__ == "__main__":
    main()