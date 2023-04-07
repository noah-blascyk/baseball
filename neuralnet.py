from calendar import month
from decimal import DivisionByZero
from getdata import TeamSeason, LeagueSeason, Date, Game
import pickle
from os.path import exists
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# input data for a game is:
# [
# home team win pct, 
# home team win pct last year, 
# home team win pct home, 
# home team win pct last 10, 
# home team win pct last 10 home, 
# games played against other team, 
# win pct against other team, 
# away team win pct, 
# away team win pct last year,
# away team win pct away,
# away team win pct last 10,
# away team win pct last 10 away,
# month,
# day
# ]

# output data is [home odds, away odds]

def genInputData(year: int):
    s = LeagueSeason(year)
    last = LeagueSeason(year - 1)
    inputData = []
    dt = datetime.today()
    for date in s.dates:
        if year != 2022 or date.month_int * 32 + date.day <= dt.month * 32 + dt.day :
            print(f"calculating for {date.month_int}/{date.day}")   
            for game in date.games:
                # get home team data
                ht = TeamSeason(game.home_team, year, s)
                
                # get the record so far both at home and total
                home_idx = 0
                ht_wins = 0
                ht_played = 0
                ht_wins_home = 0
                ht_played_home = 0
                ht_wins_against = 0
                ht_played_against = 0
                ht_runs_for_avg = 0
                ht_runs_against_avg = 0
                ht_runs_for_home = 0
                ht_runs_against_home = 0
                ht_runs_for_against = 0
                ht_runs_against_against = 0
                while ht.dates[home_idx].month_int * 32 + ht.dates[home_idx].day < date.month_int * 32 + date.day and home_idx < len(ht.dates):
                    for game_td in ht.dates[home_idx].games:
                        if game_td.winner == game.home_team:
                            ht_wins += 1
                        ht_played += 1

                        if game_td.home_team == game.home_team:
                            ht_played_home += 1
                            ht_runs_for_avg += game_td.home_score
                            ht_runs_against_avg += game_td.away_score
                            ht_runs_for_home += game_td.home_score
                            ht_runs_against_home += game_td.away_score
                            if game.home_team == game_td.winner:
                                ht_wins_home += 1
                        else:
                            ht_runs_for_avg += game_td.away_score
                            ht_runs_against_avg += game_td.home_score

                        if game_td.home_team == game.away_team or game_td.away_team == game.away_team:
                            ht_played_against += 1
                            if game_td.home_team == game.home_team:
                                ht_runs_for_against += game_td.home_score
                                ht_runs_against_against += game_td.away_score
                            else:
                                ht_runs_for_against += game_td.away_score
                                ht_runs_against_against += game_td.home_score
                            if game_td.winner == game.home_team:
                                ht_wins_against += 1
                    home_idx += 1

                try:
                    ht_win_pct = ht_wins / ht_played
                except ZeroDivisionError:
                    ht_win_pct = 0
                
                try:
                    ht_win_pct_home = ht_wins_home / ht_played_home
                except ZeroDivisionError:
                    ht_win_pct_home = 0

                try:
                    ht_win_pct_against = ht_wins_against / ht_played_against
                except ZeroDivisionError:
                    ht_win_pct_against = 0

                try:
                    ht_runs_for_against /= ht_played_against
                    ht_runs_against_against /= ht_played_against
                except ZeroDivisionError:
                    ht_runs_for_against = 0
                    ht_runs_against_against = 0

                try:
                    ht_runs_for_avg /= ht_played
                    ht_runs_against_avg /= ht_played
                except ZeroDivisionError:
                    ht_runs_for_avg = 0
                    ht_runs_against_avg = 0

                try:
                    ht_runs_for_home /= ht_played_home
                    ht_runs_against_home /= ht_played_home
                except ZeroDivisionError:
                    ht_runs_for_home = 0
                    ht_runs_against_home = 0


                # print(f"going into game on {date.month} {date.day}, {date.year}, the {game.home_team} are")
                # print(f"\t{ht_win_pct} in {ht_played} total games")
                # print(f"\t{ht_win_pct_home} in {ht_played_home} home games")

                # get the last 10 (sometimes 11) games played
                ht_game_count = 0
                cur_date = home_idx - 1
                ht_last_10_w = 0
                ht_runs_for_last10 = 0
                ht_runs_against_last10 = 0
                while ht_game_count < 10 and cur_date >= 0:
                    for game_td in ht.dates[cur_date].games:
                        ht_game_count += 1
                        if game_td.winner == game.home_team:
                            ht_last_10_w += 1
                        if game_td.home_team == game.home_team:
                            ht_runs_for_last10 += game_td.home_score
                            ht_runs_against_last10 += game_td.away_score
                        else:
                            ht_runs_for_last10 += game_td.away_score
                            ht_runs_against_last10 += game_td.home_score
                    cur_date -= 1

                try:
                    ht_last_10_pct = ht_last_10_w / ht_game_count
                except ZeroDivisionError:
                    ht_last_10_pct = 0

                try:
                    ht_runs_for_last10 /= ht_game_count
                    ht_runs_against_last10 /= ht_game_count
                except ZeroDivisionError:
                    ht_runs_for_last10 = 0
                    ht_runs_against_last10 = 0

                ht_game_count_h = 0
                cur_date = home_idx - 1
                ht_last_10_w_h = 0
                ht_runs_for_last10_h = 0
                ht_runs_against_last10_h = 0
                while ht_game_count_h < 10 and cur_date >= 0:
                    for game_td in ht.dates[cur_date].games:
                        if game_td.home_team == game.home_team:
                            ht_game_count_h += 1
                            if game_td.winner == game.home_team:
                                ht_last_10_w_h += 1
                            ht_runs_for_last10_h += game_td.home_score
                            ht_runs_against_last10_h += game_td.away_score
                    cur_date -= 1

                try:
                    ht_last_10_pct_h = ht_last_10_w_h / ht_game_count_h
                except ZeroDivisionError:
                    ht_last_10_pct_h = 0

                try:
                    ht_runs_for_last10_h /= ht_game_count_h
                    ht_runs_against_last10_h /= ht_game_count_h
                except ZeroDivisionError:
                    ht_runs_for_last10_h = 0
                    ht_runs_against_last10_h = 0

                # print(f"{date.month} {date.day}, {date.year}: {game.home_team} is {ht_last_10_pct} in their last {ht_game_count} total games")
                # print(f"{date.month} {date.day}, {date.year}: {game.home_team} is {ht_last_10_pct_h} in their last {ht_game_count_h} home games")

                # print(f"{date.month} {date.day}: {game.home_team} are {ht_win_pct_against} in {ht_played_against} games against {game.away_team}")
                
                # get away team data
                at = TeamSeason(game.away_team, year, s)
                
                # get the record so far both away and total
                away_idx = 0
                at_wins = 0
                at_played = 0
                at_wins_away = 0
                at_played_away = 0
                at_runs_for_avg = 0
                at_runs_against_avg = 0
                at_runs_for_away = 0
                at_runs_against_away = 0
                while at.dates[away_idx].month_int * 32 + at.dates[away_idx].day < date.month_int * 32 + date.day and away_idx < len(at.dates):
                    for game_td in at.dates[away_idx].games:
                        if game_td.winner == game.away_team:
                            at_wins += 1
                        at_played += 1

                        if game_td.away_team == game.away_team:
                            at_played_away += 1
                            if game.away_team == game_td.winner:
                                at_wins_away += 1
                            at_runs_for_avg += game_td.away_score
                            at_runs_against_avg += game_td.home_score
                            at_runs_for_away += game_td.away_score
                            at_runs_against_away += game_td.away_score
                        else:
                            at_runs_for_avg += game_td.home_score
                            at_runs_against_avg += game_td.away_score
                    away_idx += 1

                try:
                    at_win_pct = at_wins / at_played
                except ZeroDivisionError:
                    at_win_pct = 0
                
                try:
                    at_win_pct_away = at_wins_away / at_played_away
                except ZeroDivisionError:
                    at_win_pct_away = 0

                try:
                    at_runs_for_avg /= at_played
                    at_runs_against_avg /= at_played
                except ZeroDivisionError:
                    at_runs_for_avg = 0
                    at_runs_against_avg = 0

                try:
                    at_runs_for_away /= at_played_away
                    at_runs_against_away /= at_played_away
                except ZeroDivisionError:
                    at_runs_for_away = 0
                    at_runs_against_away = 0

                # print(f"going into game on {date.month} {date.day}, {date.year}, the {game.home_team} are")
                # print(f"\t{ht_win_pct} in {ht_played} total games")
                # print(f"\t{ht_win_pct_home} in {ht_played_home} home games")

                # get the last 10 (sometimes 11) games played
                at_game_count = 0
                cur_date = away_idx - 1
                at_last_10_w = 0
                at_runs_for_last10 = 0
                at_runs_against_last10 = 0
                while at_game_count < 10 and cur_date >= 0:
                    for game_td in at.dates[cur_date].games:
                        if game_td.away_score != None:
                            at_game_count += 1
                        if game_td.winner == game.away_team :
                            at_last_10_w += 1
                        if game_td.home_team == game.away_team and game_td.away_score != None:
                            at_runs_for_last10 += game_td.home_score
                            at_runs_against_last10 += game_td.away_score
                        elif game_td.away_score != None:
                            at_runs_for_last10 += game_td.away_score
                            at_runs_against_last10 += game_td.home_score
                    cur_date -= 1

                try:
                    at_last_10_pct = at_last_10_w / at_game_count
                    at_runs_for_last10 /= at_game_count
                    at_runs_against_last10 /= at_game_count
                except ZeroDivisionError:
                    at_last_10_pct = 0
                    at_runs_for_last10 = 0
                    at_runs_against_last10 = 0

                at_game_count_a = 0
                cur_date = away_idx - 1
                at_last_10_w_a = 0
                at_runs_for_last10_a = 0
                at_runs_against_last10_a = 0
                while at_game_count_a < 10 and cur_date >= 0:
                    for game_td in at.dates[cur_date].games:
                        if game_td.away_team == game.away_team:
                            at_game_count_a += 1
                            at_runs_for_last10_a += game_td.away_score
                            at_runs_against_last10_a += game_td.home_score
                            if game_td.winner == game.away_team:
                                at_last_10_w_a += 1
                    cur_date -= 1

                try:
                    at_last_10_pct_a = at_last_10_w_a / at_game_count_a
                    at_runs_for_last10_a /= at_game_count_a
                    at_runs_against_last10_a /= at_game_count_a
                except ZeroDivisionError:
                    at_last_10_pct_a = 0
                    at_runs_for_last10_a = 0
                    at_runs_against_last10_a = 0

                # print(f"{date.month} {date.day}, {date.year}: {game.away_team} is {at_last_10_pct} in their last {at_game_count} total games")
                # print(f"{date.month} {date.day}, {date.year}: {game.away_team} is {at_last_10_pct_a} in their last {at_game_count_a} away games")

                ht_win_pct_last_year = TeamSeason(game.home_team, year - 1, last).win_pct
                at_win_pct_last_year = TeamSeason(game.away_team, year - 1, last).win_pct
                inputData.append([
                    ht_win_pct,                 #0
                    ht_runs_for_avg,
                    ht_runs_against_avg, 
                    ht_win_pct_last_year, 
                    ht_win_pct_home, 
                    ht_runs_for_home,           #5
                    ht_runs_against_home,
                    ht_last_10_pct,
                    ht_runs_for_last10,
                    ht_runs_against_last10, 
                    ht_game_count,              #10
                    ht_last_10_pct_h,
                    ht_runs_for_last10_h,
                    ht_runs_against_last10_h,
                    ht_game_count_h,
                    ht_played_against,          #15
                    ht_win_pct_against,
                    ht_runs_for_against,
                    ht_runs_against_against,
                    at_win_pct,
                    at_runs_for_avg,            #20
                    at_runs_against_avg,
                    at_win_pct_last_year,
                    at_win_pct_away,
                    at_runs_for_away,
                    at_runs_against_away,       #25
                    at_last_10_pct,
                    at_runs_for_last10,
                    at_runs_against_last10,
                    at_game_count,
                    at_last_10_pct_a,           #30
                    at_runs_for_last10_a,
                    at_runs_against_last10_a,
                    at_game_count_a,
                    date.month_int,
                    date.day,                   #35
                    game.home_open_prob,
                    game.away_open_prob
                    ])

    if not exists(f"./input training/input-{year}.ind"):
        file = open(f"./input training/input-{year}.ind", "xb")
    else:
        file = open(f"./input training/input-{year}.ind", "wb") 

    pickle.dump(inputData, file)
    return inputData

def getInputData(years):
    inputData = []
    for year in years:
        if exists(f"./input training/input-{year}.ind"):
            print(f"found input training data from {year}")
            file = open(f"./input training/input-{year}.ind", "rb")
            inputData.extend(pickle.load(file))
            file.close()
        else:
            inputData.extend(genInputData(year))

    # # Normalize data
    # ht_runs_for_avg_max = 0 #idx 1
    # ht_runs_against_avg_max = 0 #idx 2
    # ht_runs_for_home_max = 0   #idx 5
    # ht_runs_against_home_max = 0 #idx 6
    # ht_runs_for_last10_max = 0 #idx 8
    # ht_runs_against_last10_max = 0 #idx 9
    # ht_game_count_max = 0   #idx 10
    # ht_runs_for_last10_h_max = 0 #idx 12
    # ht_runs_against_last10_h_max = 0 #idx 13
    # ht_game_count_h_max = 0 #idx 14
    # ht_played_against_max = 0 #idx 15
    # ht_runs_for_against_max = 0 #idx 17
    # ht_runs_against_against_max = 0 #idx 18
    # at_runs_for_avg_max = 0 #idx 20
    # at_runs_against_avg_max = 0 #idx 21
    # at_runs_for_away_max = 0 #idx 24
    # at_runs_against_away_max = 0 #idx 25
    # at_runs_for_last10_max = 0 #idx 27
    # at_runs_against_last10_max = 0 #idx 28
    # at_game_count_max = 0   #idx 29
    # at_runs_for_last10_a_max = 0 #idx 31
    # at_runs_against_last10_a_max = 0 #idx 32
    # at_game_count_a_max = 0 #idx 33
    # month_max = 0   #idx 34
    # day_max = 0 #idx 35

    # for x in inputData:
    #     if x[1] > ht_runs_for_avg_max:
    #         ht_runs_for_avg_max = x[1]
    #     if x[2] > ht_runs_against_avg_max:
    #         ht_runs_against_avg_max = x[2]
    #     if x[5] > ht_runs_for_home_max:
    #         ht_runs_for_home_max = x[5]
    #     if x[6] > ht_runs_against_home_max:
    #         ht_runs_against_home_max = x[6]
    #     if x[8] > ht_runs_for_last10_max:
    #         ht_runs_for_last10_max = x[8]
    #     if x[9] > ht_runs_against_last10_max:
    #         ht_runs_against_last10_max = x[9]
    #     if x[10] > ht_game_count_max:
    #         ht_game_count_max = x[10]
    #     if x[12] > ht_runs_for_last10_h_max:
    #         ht_runs_for_last10_h_max = x[12]
    #     if x[13] > ht_runs_against_last10_h_max:
    #         ht_runs_against_last10_h_max = x[13]
    #     if x[14] > ht_game_count_h_max:
    #         ht_game_count_h_max = x[14]
    #     if x[15] > ht_played_against_max:
    #         ht_played_against_max =  x[15]
    #     if x[17] > ht_runs_for_against_max:
    #         ht_runs_for_against_max = x[17]
    #     if x[18] > ht_runs_against_against_max:
    #         ht_runs_against_against_max = x[18]
    #     if x[20] > at_runs_for_avg_max:
    #         at_runs_for_avg_max = x[20]
    #     if x[21] > at_runs_against_avg_max:
    #         at_runs_against_avg_max = x[21]
    #     if x[24] > at_runs_for_away_max:
    #         at_runs_for_away_max = x[24]
    #     if x[25] > at_runs_against_away_max:
    #         at_runs_against_away_max = x[25]
    #     if x[27] > at_runs_for_last10_max:
    #         at_runs_for_last10_max = x[27]
    #     if x[28] > at_runs_against_last10_max:
    #         at_runs_against_last10_max = x[28]
    #     if x[29] > at_game_count_max:
    #         at_game_count_max = x[29]
    #     if x[31] > at_runs_for_last10_a_max:
    #         at_runs_for_last10_a_max = x[31]
    #     if x[32] > at_runs_against_last10_a_max:
    #         at_runs_against_last10_a_max = x[32]
    #     if x[33] > at_game_count_a_max:
    #         at_game_count_a_max = x[33]
    #     if x[34] > month_max:
    #         month_max = x[34]
    #     if x[35] > day_max:
    #         day_max = x[35]

    # for x in inputData:
    #     x[1] /= ht_runs_for_avg_max
    #     x[2] /= ht_runs_against_avg_max
    #     x[5] /= ht_runs_for_home_max
    #     x[6] /= ht_runs_against_home_max
    #     x[8] /= ht_runs_for_last10_max
    #     x[9] /= ht_runs_against_last10_max
    #     x[10] /= ht_game_count_max
    #     x[12] /= ht_runs_for_last10_h_max
    #     x[13] /= ht_runs_against_last10_h_max
    #     x[14] /= ht_game_count_h_max
    #     x[15] /= ht_played_against_max
    #     x[17] /= ht_runs_for_against_max
    #     x[18] /= ht_runs_against_against_max
    #     x[20] /= at_runs_for_avg_max
    #     x[21] /= at_runs_against_avg_max
    #     x[24] /= at_runs_for_away_max
    #     x[25] /= at_runs_against_away_max
    #     x[27] /= at_runs_for_last10_max
    #     x[28] /= at_runs_against_last10_max
    #     x[29] /= at_game_count_max
    #     x[31] /= at_runs_for_last10_a_max
    #     x[32] /= at_runs_against_last10_a_max
    #     x[33] /= at_game_count_a_max
    #     x[34] /= month_max
    #     x[35] /= day_max

    return inputData

def genOutputData(year: int):
    s = LeagueSeason(year)
    outputData = []
    for date in s.dates:
        for game in date.games:
            if game.winner == game.home_team:
                outputData.append([1])
            elif game.winner == game.away_team:
                outputData.append([0])
            else:
                outputData.append([0.5])
    if not exists(f"./output training/output-{year}.oud"):
        file = open(f"./output training/output-{year}.oud", "xb")
    else:
        file = open(f"./output training/output-{year}.oud", "wb")
    pickle.dump(outputData, file)
    file.close()
    return outputData

def getOutputData(years):
    outputData = []
    for year in years:
        if exists(f"./output training/output-{year}.oud"):
            print(f"found output training data for {year} on file")
            file = open(f"./output training/output-{year}.oud", "rb")
            outputData.extend(pickle.load(file))
            file.close()
        else:
            outputData.extend(genOutputData(year))

    return outputData

class NeuralNetwork:

    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.weights1 = np.array([[.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50]])
        self.weights2 = np.array([[.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50], [.50]])

        self.error_history = []
        self.epoch_list = []

    def sigmoid(self, x, deriv=False):
        print(f"sigmoid({x})")
        if deriv == True:
            return x * (1 - x)
        return 1 / (1 + np.exp(-x))

    def feed_forward(self):
        self.hidden1 = self.sigmoid(np.dot(self.inputs, self.weights1))
        self.hidden2 = self.sigmoid(np.dot(self.hidden1, self.weights2))

    def backpropagation(self):
        self.error2 = self.outputs - self.hidden2
        delta2 = self.error2 * self.sigmoid(self.hidden2, deriv=True)
        self.error1 = delta2.dot(self.weights2.T)
        delta1 = self.error1 * self.sigmoid(self.hidden1, deriv=True)
        self.weights2 += 1

    def train(self, epochs=5):
        for epoch in range(epochs):
            print(f"feed forward {epoch}")
            self.feed_forward()
            print(f"back propagation {epoch}")
            self.backpropagation()
            self.error_history.append(np.average(np.abs(self.error)))
            self.epoch_list.append(epoch)
            if epoch % 1000 == 0:
                print(f"after epoch {epoch} error is {np.average(np.abs(self.error))}")

    def predict(self, new_input):
            prediction = self.sigmoid(np.dot(new_input, self.weights))
            return prediction

# inputs = np.array(getInputData([2010,2012,2014,2016,2018]))
# outputs = np.array(getOutputData([2010,2012,2014,2016,2018]))
# nn = NeuralNetwork(inputs, outputs)
# nn.train()

# plt.figure(figsize=(15,5))
# plt.plot(nn.epoch_list, nn.error_history)
# plt.xlabel('Epoch')
# plt.ylabel('Error')
# plt.show()