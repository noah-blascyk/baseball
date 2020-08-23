from datetime import date
from html.parser import HTMLParser
import requests

# TODO: Program to scrape more info, as needed

debug = True


class Game:
    ''' 
    A class to hold the results of a game.

            away_team: str containing name of the away team.
            away_score: int containing score of the away team.
            home_team: str containing name of the home team.
            home_score: int containing score of the home team.
    '''

    def __init__(self, away_team: str, away_score: int, home_team: str, home_score: int):
        self.away_team          = away_team
        self.away_score         = away_score
        self.away_elo           = None
        self.home_team          = home_team
        self.home_score         = home_score
        self.home_elo           = None
        if home_score is None or away_score is None:
            self.winner         = None
            self.loser          = None
            self.game_played    = False
        elif home_score > away_score:
            self.winner         = home_team
            self.loser          = away_team
            self.game_played    = True
        else:
            self.winner         = away_team
            self.loser          = home_team
            self.game_played    = True

    
    def calcLines(self):
        self.home_prob_simple = 1 / (1 + 10 ** ((self.away_elo-self.home_elo)/400))
        self.home_prob = self.home_prob_simple + 0.04
        if self.home_prob > 0.5:
            self.away_line = self.home_prob / (1 - self.home_prob) * 100
            self.home_line = -1 * self.home_prob / (1 - self.home_prob) * 100
        elif self.home_prob < 0.5:
            self.home_line = self.home_prob / (1 - self.home_prob) * 100
            self.away_line = -1 * self.home_prob / (1 - self.home_prob) * 100
        else:
            self.home_line = 100
            self.away_line = 100
        self.home_dec = 1/self.home_prob
        self.away_dec = 1/(1-self.home_prob)


    def __str__(self):
        self.calcLines()
        try:
            return f'{self.away_elo:<5.0f} {self.away_team:<22} {self.away_score:<3} {(1-self.home_prob)*100:<3.1f} {self.away_line:<+4.0f} {self.away_dec:<5.3f} @ {self.home_elo:<5.0f} {self.home_team:<22} {self.home_score:<3} {self.home_prob*100:<3.1f} {self.home_line:<+4.0f} {self.home_dec:<5.3f}'
        except TypeError:
            return f'{self.away_elo:<5.0f} {self.away_team:<26} {(1-self.home_prob)*100:<3.1f} {self.away_line:<+4.0f} {self.away_dec:<5.3f} @ {self.home_elo:<5.0f} {self.home_team:<26} {self.home_prob*100:<3.1f} {self.home_line:<+4.0f} {self.home_dec:<5.3f}'



class GameParser(HTMLParser):
    def __init__(self):
        self.convert_charrefs   = False
        self.span_handle        = False
        self.away_team_process  = False
        self.away_team_done     = False
        self.home_team_process  = False
        self.away_score_done    = False
        self.home_score         = None
        self.away_score         = None
        self.away_team          = ''
        self.away_score_str     = ''
        self.home_team          = ''
        self.home_score_str     = ''
        self.reset()

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and not self.away_team_done:
            self.away_team_process = True
        elif tag == 'a':
            self.home_team_process = True
        elif tag == 'span':
            self.span_handle = True
    
    def handle_data(self, data):
        if self.span_handle:
            pass
        elif self.away_team_process:
            self.away_team = data
            self.away_team_process = False
            self.away_team_done = True
        elif self.home_team_process:
            self.home_team = data
            self.home_team_process = False
        elif not self.away_score_done:
            for i in data:
                if i not in '"() &nbsp;@':
                    self.away_score_str += i
            self.away_score = int(self.away_score_str) if self.away_score_str != '' else None
            if self.away_score is not None:
                self.away_score_done = True
        else:
            for i in data:
                if i not in '"() &nbsp;@':
                    self.home_score_str += i
            self.home_score = int(self.home_score_str) if self.home_score_str != '' else 0

    def handle_endtag(self, tag):
        if tag == 'span':
            self.span_handle = False



class Date:
    ''' 
    A class to hold the results of the games played on a certain date.

            weekday: str containing the day of the week.
            month: str containing the month.
            day: int containing the day of the month.
            year: int containing the year.
            games: a list of Game objects.
            month_int: int corresponding to the month.
            weekday_int: int corresponding to the day of the week. Monday = 1.
    '''

    month_dict = {
        "January"   :   1   ,
        "February"  :   2   ,
        "March"     :   3   ,
        "April"     :   4   ,
        "May"       :   5   ,
        "June"      :   6   ,
        "July"      :   7   ,
        "August"    :   8   ,
        "September" :   9   ,
        "October"   :   10  ,
        "November"  :   11  ,
        "December"  :   12
    }


    weekday_dict = {
        "Monday"    :   1   ,
        "Tuesday"   :   2   ,
        "Wednesday" :   3   ,
        "Thursday"  :   4   ,
        "Friday"    :   5   ,
        "Saturday"  :   6   ,
        "Sunday"    :   7   ,
        "Today"     :   8   ,
    }

    def __init__(self, weekday: str, month, day: int, year: int):
        self.weekday        = weekday
        if type(month) is str:
            self.month      = month
            self.month_int  = self.month_dict.get(month)
        else:
            self.month_int  = month
            for i, j in self.month_dict.items():
                if j == self.month_int:
                    self.month = i
        self.day            = day
        self.year           = year
        self.games          = []
        self.weekday_int    = self.weekday_dict.get(weekday)


    def calcRecord(self):
        self.algo_wins = 0
        self.algo_losses = 0
        self.algo_no_call = 0
        self.home_wins = 0
        self.home_losses = 0
        for j in self.games:
            j.calcLines()
            if j.home_prob > 0.5:
                if j.winner == j.home_team:
                    self.home_wins += 1
                    self.algo_wins += 1
                elif j.winner == j.away_team:
                    self.algo_losses += 1
                    self.home_losses += 1
                else:
                    pass
            if j.home_prob < 0.5:
                if j.winner == j.home_team:
                    self.home_wins += 1
                    self.algo_losses += 1
                elif j.winner == j.away_team:
                    self.algo_wins += 1
                    self.home_losses += 1
                else:
                    pass
            elif j.home_prob == 0.5:
                self.algo_no_call += 1
                if j.winner == j.home_team:
                    self.home_wins += 1
                elif j.winner == j.away_team:
                    self.home_losses += 1


    def __str__(self):
        self.calcRecord()
        ret = f'{self.weekday}, {self.month} {self.day}, {self.year}'
        for i in self.games:
            ret += '\n\t\t' + str(i)
        ret += f'\tRecord for the day (straight up): {self.algo_wins}-{self.algo_losses}-{self.algo_no_call}'
        return ret + '\n'


    def __eq__(self, other):
        return self.month == other.month and self.day == other.day and self.year == other.year



class LeagueSeason(HTMLParser):
    '''
    A class to store all of the scores from every game in a given year.
    Inherits HTMLParser.

        year: int corresponding to the year
        dates: a list of Date objects, one for each day a game was played on.
        sched_url: url for the Baseball Reference schedule page.
        sched_html: the html contents of the schedule page.
    '''

    def __init__(self, year: int = 2020):
        self.year               = year
        self.dates              = []
        self.simple_elo         = {}
        self.sched_url          = f'https://baseball-reference.com/leagues/MLB/{self.year}-schedule.shtml'
        self.sched_html         = requests.get(self.sched_url).text
        # Remove all the newlines
        sched_html = ''
        for i in self.sched_html:
            if i != '\n':
                sched_html += i

        self.sched_html = sched_html
        self.convert_charrefs   = True
        self.date_process       = False
        self.game_process       = False
        self.reset()

        self.scrape()
        self.simpleEloCalc()
        self.calcRecord()


    def __str__(self):
        ret = f'All scores from {self.year}, using {self.sched_url}:'
        for i in self.dates:
                ret += '\n\t' + str(i)
        ret += f'Record for the year (straight up): {self.algo_wins}-{self.algo_losses}-{self.algo_no_call} ({self.algo_wins/(self.algo_wins+self.algo_losses):#.3f})\n'
        ret += f'League home record: {self.home_wins}-{self.home_losses} ({self.home_wins/(self.home_wins+self.home_losses):#.3f})'
        return ret


    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.date_process = True
        if attrs != []:
            if attrs[0][1] == 'game':
                self.game_process = True
                self.game_start = self.getpos()
        if self.game_process and tag == 'em':
            self.game_end = self.getpos()
            self.game_process = False
            self.addGame()


    def handle_data(self, data):
        if self.date_process:
            self.addDate(data)
            self.date_process = False


    def addDate(self, date_str: str):
        if date_str != "Today's Games":
            weekday_done = False
            month_done = False
            month_space = False
            day_done = False
            weekday = ''
            month = ''
            day = ''
            year = ''
            for i in date_str:
                if i != ',' and not weekday_done:
                    weekday += i
                elif i == ',' and not weekday_done:
                    weekday_done = True
                elif i == ' ' and not month_space:
                    month_space = True
                elif i != ' ' and not month_done:
                    month += i
                elif i == ' ' and not month_done:
                    month_done = True
                elif i != ',' and not day_done:
                    day += i
                elif i == ',':
                    day_done = True
                elif i == ' ':
                    pass
                else:
                    year += i
            try:
                self.dates.append(Date(weekday, month, int(day), int(year)))
            except ValueError:
                pass
        else:
            td = date.today()
            self.dates.append(Date('Today', td.month, td.day, td.year))
            pass


    def addGame(self):
        game_parser = GameParser()
        game_parser.feed(self.sched_html[self.game_start[1]:self.game_end[1]])
        self.dates[-1].games.append(Game(game_parser.away_team, game_parser.away_score, game_parser.home_team, game_parser.home_score))


    def scrape(self):
        self.feed(self.sched_html)


    def simpleEloCalc(self):
        '''
        Calculate the Elo of every team for the entire season. Start them at 500.
        '''
        for i in self.dates:
            for j in i.games:
                if j.home_team not in self.simple_elo:
                    self.simple_elo[j.home_team] = 500
                if j.away_team not in self.simple_elo:
                    self.simple_elo[j.away_team] = 500

                j.home_elo = self.simple_elo[j.home_team]
                j.away_elo = self.simple_elo[j.away_team]

                j.calcLines()
                if j.winner is not None:
                    if j.winner == j.home_team:
                        self.simple_elo[j.home_team] += 32 * (1 - j.home_prob)
                        self.simple_elo[j.away_team] -= 32 * (1 - j.home_prob)
                    else:
                        self.simple_elo[j.home_team] -= 32 * j.home_prob
                        self.simple_elo[j.away_team] += 32 * j.home_prob


    def printEloRankings(self):
        sorted_elo = sorted(self.simple_elo.items(), key = lambda x: x[1], reverse = True)
        for i in sorted_elo:
            print(f'{i[0]:<30} {i[1]:>10.0f}')


    def calcRecord(self):
        self.algo_wins = 0
        self.algo_losses = 0
        self.algo_no_call = 0
        self.home_wins = 0
        self.home_losses = 0
        for j in self.dates:
            j.calcRecord()
            self.algo_wins += j.algo_wins
            self.algo_losses += j.algo_losses
            self.algo_no_call += j.algo_no_call
            self.home_wins += j.home_wins
            self.home_losses += j.home_losses


    def printDate(self, month: int, day: int):
        for i in self.dates:
            if i.month_int == month and i.day == day:
                print(i)
            else:
                pass
                      

class TeamSeason:

    def __init__(self, team: str, year: int = None, league_season: LeagueSeason = None):
        self.team = team
        self.wins = 0
        self.home_wins = 0
        self.away_wins = 0
        self.losses = 0
        self.home_losses = 0
        self.away_losses = 0
        self.played = 0
        self.home_played = 0
        self.away_played = 0
        self.dates = []

        if league_season == None:
            if year == None:
                self.league_season = LeagueSeason()
                self.year = self.league_season.year
            else:
                self.league_season = LeagueSeason(year)
                self.year = year
            self.league_season.scrape()
        else:
            self.league_season = league_season

        for i in self.league_season.dates:
            for j in i.games:
                if j.away_team == team or j.home_team == team:
                    try:
                        if self.dates[-1] != i:
                            self.dates.append(Date(i.weekday, i.month, i.day, i.year))
                    except IndexError:
                        self.dates.append(Date(i.weekday, i.month, i.day, i.year))
                    self.dates[-1].games.append(Game(j.away_team, j.away_score, j.home_team, j.home_score))
                    if team == j.winner:
                        self.wins += 1
                        if team == j.home_team:
                            self.home_wins += 1
                        else:
                            self.away_wins += 1
                    elif team == j.loser:
                        self.losses += 1
                        if team == j.home_team:
                            self.home_losses += 1
                        else:
                            self.away_losses += 1
                    if j.game_played:
                        self.played += 1
                        if team == j.home_team:
                            self.home_played += 1
                        else:
                            self.away_played += 1
        
        self.win_pct = self.wins / self.played
        self.home_win_pct = self.home_wins / self.home_played
        self.away_win_pct = self.away_wins / self.away_played
        
        if debug:
            print(self)

        self.against = {}
        for i in self.dates:
            for j in i.games:
                if j.away_team != team:
                    if j.away_team not in self.against:
                        self.statsAgainst(j.away_team)
                    else:
                        pass
                else:
                    if j.home_team not in self.against:
                        self.statsAgainst(j.home_team)
                    else:
                        pass


    def __str__(self):
        return f'{self.year} {self.team} \n' +\
            f'{self.wins}-{self.losses} ({self.win_pct:#.3}) in {self.played} games. \n' +\
            f'{self.home_wins}-{self.home_losses} ({self.home_win_pct:#.3}) in {self.home_played} games at home. \n' +\
            f'{self.away_wins}-{self.away_losses} ({self.away_win_pct:#.3}) in {self.away_played} games on the road.\n'
    

    def statsAgainst(self, other_team: str):
        '''
        Get a team's stats against another team.
        '''
        wins = 0
        losses = 0
        played = 0
        home_wins = 0
        home_losses = 0
        home_played = 0
        away_wins = 0
        away_losses = 0
        away_played = 0

        for i in self.dates:
            for j in i.games:
                if j.home_team == other_team:
                    if j.winner == self.team:
                        wins += 1
                        played += 1
                        away_wins += 1
                        away_played += 1
                    elif j.winner == other_team:
                        losses += 1
                        played += 1
                        away_losses += 1
                        away_played += 1
                    else:
                        pass
                elif j.away_team == other_team:
                    if j.winner == self.team:
                        wins += 1
                        played += 1
                        home_wins += 1
                        home_played += 1
                    elif j.winner == other_team:
                        losses += 1
                        played += 1
                        home_losses += 1
                        home_played += 1
                    else:
                        pass
                else:
                    pass
            # for j in i.games
        # for i in self.dates

        if debug:
            try:
                print(f'{self.year} {self.team} stats against the {other_team}\n' +\
                    f'{wins}-{losses} ({wins/played:#.3}) in {played} games. \n' +\
                    f'{home_wins}-{home_losses} ({home_wins/home_played:#.3}) in {home_played} games at home. \n' +\
                    f'{away_wins}-{away_losses} ({away_wins/away_played:#.3}) in {away_played} games on the road.\n')
            except ZeroDivisionError:
                print(f'{self.year} {self.team} stats against the {other_team}\n' +\
                    f'{wins}-{losses} in {played} games. \n' +\
                    f'{home_wins}-{home_losses} in {home_played} games at home. \n' +\
                    f'{away_wins}-{away_losses} in {away_played} games on the road.\n')

        self.against[other_team] = {
            'wins'          :   wins,
            'losses'        :   losses,
            'played'        :   played,
            'home_wins'     :   home_wins,
            'home_losses'   :   home_losses,
            'home_played'   :   home_played,
            'away_wins'     :   away_wins,
            'away_losses'   :   away_losses,
            'away_played'   :   away_played
        }
