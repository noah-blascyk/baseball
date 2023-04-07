import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from neuralnet import getInputData, getOutputData
from getdata import LeagueSeason
import matplotlib.pyplot as plt

def simulateBetting(year):
    print(f"Loading {year} season data")
    s = LeagueSeason(year)

    treasury = 1
    betcount = 0

    #linearize the list of games
    gamelist = []
    treasury_history = []
    game_history = []
    for x in s.dates:
        for y in x.games:
            gamelist.append(y)

    print("Loading neural net")
    inputs = keras.Input(shape=(38,))
    x_input = np.array(getInputData([2010,2012,2014,2016,2018,2011,2013,2015,2017,2019]))
    y_output = np.array(getOutputData([2010,2012,2014,2016,2018,2011,2013,2015,2017,2019]))
    x = layers.BatchNormalization()(inputs)
    x = layers.Dense(18, activation="sigmoid")(x)
    x = layers.Dense(18, activation="sigmoid")(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="baseball")


    model.compile(
        loss=keras.losses.BinaryCrossentropy(),
        optimizer=keras.optimizers.RMSprop(),
        metrics=[ "accuracy"],
    )

    history = model.fit(x=x_input, y=y_output, batch_size = 128, epochs = 25, verbose=2, validation_split = 0.5, shuffle=True)

    print(f"Predicting outcomes of games in {year}")
    real_input = np.array(getInputData([year]))
    pred_output = model.predict(real_input)
    real_output = getOutputData([year])

    roi = []
    avg_roi = []
    win_count = 0
    print(f"Calculating returns following Kelly strategy")
    for x in range(real_input.shape[0]):
        pred_home = pred_output[x][0]
        pred_away = 1 - pred_home
        er_home = pred_home / gamelist[x].home_close_prob
        er_away = pred_away / gamelist[x].away_close_prob
        adv_home = er_home - 1
        adv_away = er_away - 1
        if pred_home > 0.5 and real_output[x][0] == 1:
            win_count += 1
        if pred_home < 0.5 and real_output[x][0] == 0:
            win_count += 1
        # print(f"home adv {adv_home:.2f} away adv {adv_away:.2f} home odds {1/gamelist[x].home_close_prob:.2f} away odds {1/gamelist[x].away_close_prob:.2f}")
        kelly_wager = 0
        if adv_home > 0.1:
            bet = 'h'
            betcount += 1
            kelly_wager = adv_home / (1 / gamelist[x].home_close_prob - 1) / 2
        elif adv_away > 0.1:
            bet = 'a'
            betcount += 1
            kelly_wager = adv_away / (1 / gamelist[x].away_close_prob - 1) / 2
        else:
            bet = 'n'
        bet_amt = min(treasury * kelly_wager, 1)
        # print(f"betting ${bet_amt:.2f} on {bet}")

        if bet == 'h':
            if real_output[x][0] != 1:
                treasury -= bet_amt
                # print("lost.")
                roi.append(-1)
            else:
                treasury += bet_amt / gamelist[x].home_close_prob - bet_amt
                roi.append((bet_amt / gamelist[x].home_close_prob - bet_amt) / bet_amt)
                # print(f"won ${bet_amt / gamelist[x].home_close_prob - bet_amt:.2f}!")
        elif bet == 'a':
            if real_output[x][0] != 0:
                treasury -= bet_amt
                # print("lost.")
                roi.append(-1)
            else:
                treasury += bet_amt / gamelist[x].away_close_prob - bet_amt
                roi.append((bet_amt / gamelist[x].away_close_prob - bet_amt) / bet_amt)
                # print(f"won ${bet_amt / gamelist[x].away_close_prob - bet_amt:.2f}!")
        else:
            roi.append(0)

        treasury_history.append(treasury)
        game_history.append(x)
        try:
            avg_roi.append(sum(roi)/betcount)
            print(f"after game {x}, treasury is at ${treasury:.2f}. I have made {betcount} bets at an average ROI of {sum(roi)/betcount*100:.2f}%")
        except ZeroDivisionError:
            avg_roi.append(0)
            print(f"after game {x}, treasury is at ${treasury:.2f}. I have made {betcount} bets at an average ROI of {0:.2f}%")

    print(f"Total return for {year}: {(treasury - 1) * 100}%")
    print(f"{win_count/real_input.shape[0]:.3f}")
    plt.figure(figsize=(15,1))
    plt.plot(game_history, treasury_history)
    plt.xlabel('Game')
    plt.ylabel('Wealth, multiple of original wealth')
    plt.show()

def generateProb(year):
    s = LeagueSeason(year)

    treasury = 1
    betcount = 0

    #linearize the list of games
    gamelist = []
    treasury_history = []
    game_history = []
    for x in s.dates:
        for y in x.games:
            gamelist.append(y)

    print("Loading neural net")
    inputs = keras.Input(shape=(36,))
    x_input = np.array(getInputData([2010,2012,2014,2016,2018]))
    y_output = np.array(getOutputData([2010,2012,2014,2016,2018]))
    x = layers.BatchNormalization()(inputs)
    x = layers.Dense(20, activation="tanh")(x)
    x = layers.Dense(20, activation="sigmoid")(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="baseball")

    pred = model.predict(np.array(getInputData([year])))

    x = 0
    for i in s.dates:
        print(f"{i.month_int}/{i.day}")
        for j in s.games:
            print(f"{j.home_team} {pred[x][0]} {j.away_team} {1-pred[x][0]}")
            x += 1

def calcRecordOddsmakers(year):
    s = LeagueSeason(year)
    close_wins = 0
    close_wins = 0
    game_count = 0
    for date in s.dates:
        for game in date.games:
            game_count += 1
            if game.winner == game.home_team:
                if game.home_close_prob > game.away_close_prob:
                    close_wins += 1
                if game.home_close_prob > game.away_close_prob:
                    close_wins += 1
            else:
                if game.away_close_prob > game.home_close_prob:
                    close_wins += 1
                if game.away_close_prob > game.home_close_prob:
                    close_wins += 1
    print(f"close: {close_wins / game_count:.3f}")
    print(f"close: {close_wins / game_count:.3f}")