#TODO try to create a one big class and this and match_list will be like child
#TODO classes or methods in a big class

from fotmob_stats import FotMobStats

klasa = FotMobStats(league_id=38)
print(klasa.get_available_teams(tab="overview",season="2024-2025"))