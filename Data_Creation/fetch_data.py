from riotwatcher import LolWatcher, ApiError, RiotWatcher
from env_vars import riot_key

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
    matchIDs = set()
    
    for id in puuids:
        try:
            matchIDs.update(watcher.match.matchlist_by_puuid(puuid = id, region = region))
        except Exception as e:
            pass
    
    return list(matchIDs)

if __name__ == "__main__":
    
    # Load API Key and set variables
    key = riot_key()
    watcher = LolWatcher(key)