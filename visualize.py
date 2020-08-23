if '.' in __name__:
    from .getdata import LeagueSeason, TeamSeason
else:
    from getdata import LeagueSeason, TeamSeason
import matplotlib.pyplot as plt
import numpy as np

def plotAvg(year):
    season = LeagueSeason(year)
    date_count = 0
    date_list = []
    avg_list = []
    for i in season.dates:
        date_list.append(date_count)
        avg_list.append(i.cum_wins/(i.cum_wins+i.cum_losses))
        date_count += 1
    plt.plot(date_list, avg_list)

def compYears(years):
    for i in years:
        plotAvg(i)
    plt.grid(True)
    plt.yticks([0,.4,.5,.6,.7,1])
    plt.show()