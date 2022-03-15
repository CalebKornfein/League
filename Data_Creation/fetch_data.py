from riotwatcher import LolWatcher, ApiError, RiotWatcher
from env_vars import riot_key
from collections import defaultdict

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
    
    for player in challenger_players:
        puuid = fetch_puuid(player)
        if puuid != "ERROR":
            puuids.append(puuid)
            
    return puuids

def fetch_matchIDs(watcher, puuids):
    region="AMERICAS"
    queue = 420
    matchIDs = set()
    
    for id in puuids:
        try:
            matchIDs.update(watcher.match.matchlist_by_puuid(puuid = id, 
                                                             region = region,
                                                             queue = queue))
        except Exception as e:
            pass
    
    return list(matchIDs)

def fetch_gameinfo(watcher, matchID):
    region = "AMERICAS"
    
    game = watcher.match.by_id(region, matchID)
    timeline = watcher.match.timeline_by_match(region, matchID)

    ### Define Players
    
    players= defaultdict(lambda: dict())
    for player in game["info"]["participants"]:
        players[player['puuid']]['participantId'] = player['participantId']
    
    ### Find roles of players and win status
    
    for player in game["info"]["participants"]:
        players[player["puuid"]]["win"] = player["win"]
        players[player["puuid"]]["position"] = player["teamPosition"]
    
if __name__ == "__main__":
    
    # Load API Key and set variables
    key = riot_key()
    watcher = LolWatcher(key)