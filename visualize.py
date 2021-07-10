if '.' in __name__:
    from .getdata import LeagueSeason, TeamSeason
else:
    from getdata import LeagueSeason, TeamSeason
import matplotlib.pyplot as plt
import numpy as np
import time

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

def compReturns(years):
    for i in years:
        plotReturn(i)
    plt.grid(True)
    plt.show()

def plotReturn(year):
    season = LeagueSeason(year)
    date_count = 0
    month_open_cum = 0
    month_close_cum = 0
    date_list = []
    open_return_list = []
    close_return_list = []
    for i in season.dates:
        date_list.append(date_count)
        open_return_list.append(i.cum_open_return)
        close_return_list.append(i.cum_close_return)
        if i.month_int <= 6 and i.month_int % 2 == 1 and i.day == 31:
            print(f'\t{season.year} {i.month}: {i.cum_open_return - month_open_cum:10.2f}, {i.cum_close_return - month_close_cum:10.2f}')
            month_open_cum = i.cum_open_return
            month_close_cum = i.cum_close_return
        if i.month_int <= 6 and i.month_int % 2 == 0 and i.day == 30:
            print(f'\t{season.year} {i.month}: {i.cum_open_return - month_open_cum:10.2f}, {i.cum_close_return - month_close_cum:10.2f}')
            month_open_cum = i.cum_open_return
            month_close_cum = i.cum_close_return
        if i.month_int > 6 and i.month_int % 2 == 1 and i.day == 30:
            print(f'\t{season.year} {i.month}: {i.cum_open_return - month_open_cum:10.2f}, {i.cum_close_return - month_close_cum:10.2f}')
            month_open_cum = i.cum_open_return
            month_close_cum = i.cum_close_return
        if i.month_int > 6 and i.month_int % 2 == 0 and i.day == 31:
            print(f'\t{season.year} {i.month}: {i.cum_open_return - month_open_cum:10.2f}, {i.cum_close_return - month_close_cum:10.2f}')
            month_open_cum = i.cum_open_return
            month_close_cum = i.cum_close_return
        date_count += 1
    plt.plot(date_list, open_return_list)
    plt.plot(date_list, close_return_list)
    print(f'\t{season.year} {season.dates[-1].month}: {season.dates[-1].cum_open_return - month_open_cum:10.2f}, {season.dates[-1].cum_close_return - month_close_cum:10.2f}')
    print(f'{season.year}: {season.dates[-1].cum_open_return:10.2f}, {season.dates[-1].cum_close_return:10.2f}')

def printAvg(years, hff, k):
    avg_sum = 0
    cum_wins = 0
    cum_losses = 0
    num_years = len(years)
    for i in years:
        j = LeagueSeason(i, hff, k)
        #print(f'{i}: {j.algo_wins}-{j.algo_losses} ({j.algo_wins/(j.algo_wins+j.algo_losses):#.3f})')
        avg_sum += j.algo_wins/(j.algo_wins+j.algo_losses)
        cum_wins += j.algo_wins
        cum_losses += j.algo_losses
    #print(f'Total: {cum_wins}-{cum_losses} ({avg_sum/num_years:#.5f})')
    return avg_sum/num_years

def optimizehff():
    max = 0
    for i in range(435041,435060):
        avg = printAvg(range(2000,2020), i/10000000, 10)
        if avg > max:
            print(f'New Max! {avg} w/ hff {i/10000000}')
            max = avg
        else:
            print(i/10000000)
        #time.sleep(5)

def optimizek():
    max = 0
    for i in range(99980,100000):
        avg = printAvg(range(2000,2020), 0.0435044, i/10000)
        if avg > max:
            print(f'New Max! {avg} w/ K {i/10000}')
            max = avg
        else:
            print(i/10000)