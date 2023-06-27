# Data Questions/things that look very odd to me:

June 2023


## Batters showing as 0, when there is hitting data




``` python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import os


from src.utils import *
from src.plotting import Baseball_Field
from src.game import Game


# get all games into a list, so I can use my Game class
all_games = []

for sub_dir, dirs, files in os.walk('data/game_events/'):
    for file in files:
        if "checkpoint" in file:
                continue
    
        all_games.append(file.split("-")[-1].split(".csv")[0])

print(len(all_games))        


zeros = pd.DataFrame()

for g in all_games:
    this_game = Game(g)
    
    zero_batters = this_game.game_info_df.loc[this_game.game_info_df["batter"] == 0, :]

    events_w_data = this_game.game_events_df.loc[(this_game.game_events_df["play_per_game"].isin(zero_batters["play_per_game"]))
                                                , ["game_str", "play_id", "play_per_game", "event_code"]]
    
    zeros = pd.concat([zeros, events_w_data])
    

zeros[["game_str", "play_id", "play_per_game"]].drop_duplicates().to_csv("data_debugging/batter_as_zeros.csv", index = False)

```


This returns:

|index|game_str             |play_id|play_per_game|
|-----|---------------------|-------|-------------|
|1    |1903_01_TeamNE_TeamA2|101    |101          |
|2    |1903_01_TeamNE_TeamA2|160    |160          |
|3    |1903_01_TeamNE_TeamA2|161    |161          |
|4    |1903_01_TeamNE_TeamA2|162    |162          |
|5    |1903_01_TeamNE_TeamA2|203    |203          |
|6    |1903_11_TeamNC_TeamA1|110    |111          |
|7    |1903_02_TeamNE_TeamA2|4      |4            |
|8    |1903_02_TeamNE_TeamA2|132    |133          |
|9    |1903_25_TeamNK_TeamB |126    |131          |
|10   |1903_28_TeamNF_TeamA2|158    |158          |
|11   |1903_07_TeamND_TeamA2|168    |169          |
|12   |1903_07_TeamND_TeamA2|304    |305          |
|13   |1903_30_TeamNF_TeamA2|94     |94           |
|14   |1903_30_TeamNF_TeamA2|244    |244          |
|15   |1903_25_TeamNH_TeamA3|289    |291          |



I guess this doesn't happen that often, but often enough that is mainly


## In game events, "play_id" and "play_per_game" not lining up

I need to use play_per_game to join!


## 