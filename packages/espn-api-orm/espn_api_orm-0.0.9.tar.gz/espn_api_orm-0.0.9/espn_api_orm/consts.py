from enum import Enum

######################################
# Sport Consts
######################################

class ESPNSportTypes(Enum):
    AUSTRALIAN_FOOTBALL = 'australian-football'
    BASEBALL = 'baseball'
    BASKETBALL = 'basketball'
    CRICKET = 'cricket'
    FIELD_HOCKEY = 'field-hockey'
    FOOTBALL = 'football'
    GOLF = 'golf'
    HOCKEY = 'hockey'
    LACROSSE = 'lacrosse'
    MMA = 'mma'
    RACING = 'racing'
    RUGBY = 'rugby'
    RUGBY_LEAGUE = 'rugby-league'
    SOCCER = 'soccer'
    TENNIS = 'tennis'
    VOLLEYBALL = 'volleyball'
    WATER_POLO = 'water-polo'

## All Sport/League Pairs
class ESPNSportLeagueTypes(Enum):
    BASEBALL_COLLEGE_BASEBALL = 'baseball/college-baseball'
    BASEBALL_COLLEGE_SOFTBALL = 'baseball/college-softball'
    BASEBALL_MLB = 'baseball/mlb'
    BASKETBALL_MENS_COLLEGE_BASKETBALL = 'basketball/mens-college-basketball'
    BASKETBALL_NBA = 'basketball/nba'
    BASKETBALL_WNBA = 'basketball/wnba'
    BASKETBALL_WOMENS_COLLEGE_BASKETBALL = 'basketball/womens-college-basketball'
    FIELD_HOCKEY_WOMENS_COLLEGE_FIELD_HOCKEY = 'field-hockey/womens-college-field-hockey'
    FOOTBALL_COLLEGE_FOOTBALL = 'football/college-football'
    FOOTBALL_NFL = 'football/nfl'
    GOLF_LIV = 'golf/liv'
    GOLF_LPGA = 'golf/lpga'
    GOLF_PGA = 'golf/pga'
    HOCKEY_MENS_COLLEGE_HOCKEY = 'hockey/mens-college-hockey'
    HOCKEY_NHL = 'hockey/nhl'
    HOCKEY_WOMENS_COLLEGE_HOCKEY = 'hockey/womens-college-hockey'
    LACROSSE_MENS_COLLEGE_LACROSSE = 'lacrosse/mens-college-lacrosse'
    LACROSSE_PLL = 'lacrosse/pll'
    LACROSSE_WOMENS_COLLEGE_LACROSSE = 'lacrosse/womens-college-lacrosse'
    MMA_UFC = 'mma/ufc'
    SOCCER_UEFA_CHAMPIONS = 'soccer/uefa.champions'
    SOCCER_ENG_1 = 'soccer/eng.1'
    SOCCER_ESP_1 = 'soccer/esp.1'
    SOCCER_GER_1 = 'soccer/ger.1'
    SOCCER_USA_1 = 'soccer/usa.1'
    SOCCER_ITA_1 = 'soccer/ita.1'
    SOCCER_FRA_1 = 'soccer/fra.1'
    SOCCER_ENG_2 = 'soccer/eng.2'
    SOCCER_NED_1 = 'soccer/ned.1'
    SOCCER_POR_1 = 'soccer/por.1'
    VOLLEYBALL_MENS_COLLEGE_VOLLEYBALL = 'volleyball/mens-college-volleyball'
    VOLLEYBALL_WOMENS_COLLEGE_VOLLEYBALL = 'volleyball/womens-college-volleyball'
    WATER_POLO_MENS_COLLEGE_WATER_POLO = 'water-polo/mens-college-water-polo'
    WATER_POLO_WOMENS_COLLEGE_WATER_POLO = 'water-polo/womens-college-water-polo'

class ESPNSportSeasonTypes(Enum):
    PRE = 1
    REG = 2
    POST = 3
    OFF = 4

class ESPNCalendarTypes(Enum):
    ONDAYS='ondays'
    OFFDAYS='offdays'
    BLACKLIST='blacklist'
    WHITELIST='whitelist'

FIRST_SEASON = 1998 # For all sports only go back to 1998
