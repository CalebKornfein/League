from riotwatcher import LolWatcher, ApiError, RiotWatcher
from env_vars import riot_key
from collections import defaultdict, Counter
import pandas as pd
import tqdm

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
    for frame in frames:
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
                
    return players
    
def main():
    # Load API Key and set variables
    key = riot_key()
    watcher = LolWatcher(key)
    
    # Fetch Challenger IDs and write them to a csv
    challenger_puuids = pd.DataFrame(fetch_challenger_puuids(watcher), columns = ['Puuid'])
    challenger_puuids.to_csv('Data/Puuids.csv', index=False)
    
    # Fetch Match IDs given Challenger IDs
    challenger_puuids = pd.read_csv('Data/Puuids.csv')
    challenger_matches = fetch_matchIDs(watcher, list(challenger_puuids['Puuid'].values))
    
    
    #out = 'data.csv'
    #f = open(out, 'a')
    
if __name__ == "__main__":
    main()