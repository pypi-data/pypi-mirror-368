import requests
from fmscraper.xmas_generator import generate_xmas_header


class FotMobStats:
    def __init__(self,league_id):
        self.url = "https://www.fotmob.com/api"
        self.league_id = league_id
        self.matchdetails_url = self.url+f'/matchDetails?matchId='
        self.leagues_url = self.url+f'/leagues?id={self.league_id}'
        self.team_url = self.url+f'/teams?id='
        self.player_url = self.url+f'/playerData?id='
        self.headers = {
            "x-mas": generate_xmas_header(self.matchdetails_url)
        }
        self.match_content_types = ['matchFacts', 'stats', 'playerStats',
                              'shotmap','lineup']

    def get_json_content(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


    def get_player_stats(self,player_id):
        url = self.player_url+str(player_id)
        data = self.get_json_content(url)
        return data


    def get_team_stats(self,team_id,tab):
        url = self.team_url+str(team_id)
        data = self.get_json_content(url)
        assert tab in data.keys()
        return data[tab]


    def get_matches_list(self, season,team_or_all):
        season_formated = season.replace('-',"%2F")
        data = self.get_json_content(self.leagues_url+f"&season={season_formated}")
        games_list = data['matches']['allMatches']
        if team_or_all == "all":
            game_ids = [game['id'] for game in games_list]
        else:
            assert team_or_all.lower() in self.get_available_teams(season).keys()
            team = team_or_all.lower().replace(" ","-")
            game_ids = [game['id'] for game in games_list if team in game['pageUrl']]
        return game_ids




    def get_match_details(self, match_id,content_type:str):
        data = self.get_json_content(url=self.matchdetails_url + str(match_id))
        assert content_type in self.match_content_types
        return data['content'][content_type]
    #TODO add option for different keys here, machfacts, stats, playerstats, shotmap, lineup

    def get_available_teams(self, season):
        season_formatted = season.replace("-", "%2F")
        data = self.get_json_content(url=self.leagues_url + f"&season={season_formatted}&tab=overview&type=league")
        try:
            teams = data['table'][0]['data']['table']['all']
        except KeyError as e:
            teams = data['table'][0]['data']['tables'][2]['table']['xg']
        teams_dict = {team['name'].lower(): {"name": team['name'].replace(" ", "-").lower(),
                                             "id": team['id']} for team in teams}
        return teams_dict


if __name__ == "__main__":
    bundesliga_stats = FotMobStats(league_id=38)
    # print(klasa.get_available_teams("2024-2025"))
    # print(klasa.get_matches_list("2024-2025","rapid wien"))
    # print(klasa.get_team_stats(10011)['history'].keys())
    # staty = klasa.get_match_details(match_id=4525341,content_type='playerStats')
    # for value in staty.values():
    #     print(value)
