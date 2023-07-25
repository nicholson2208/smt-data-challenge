# Data Questions/things that look very odd to me:

June 2023


## Batters showing as 0


``` python
import numpy as np
import pandas as pd
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

# this returns 97        
print(len(all_games))        


zeros = pd.DataFrame()

for g in all_games:
    
    # a user defined object that just cleans up the data
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



I guess this doesn't happen that often, but often enough that it might mess up my out and at_bat imputing.

I think it is often the case where the batter of the prior play ends up being the first_baserunner in plays where the batter is 0 


## In game_events, "play_id" and "play_per_game" not lining up

I think these are different, and I don't think I can just use them interchangeably -- I think the implication is that game_info should be the base table


### There are many instances where play_id and play_per_game are not the same

I think this is becuase there must be play_per_games that have been removed?
- Maybe like a mound visit or something?


```python
import numpy as np
import pandas as pd
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

# this returns 97        
print(len(all_games))        


mismatches = pd.DataFrame()

for g in all_games:
    this_game = Game(g)
    
    
    mismatched_play_ids = this_game.game_events_df.loc[this_game.game_events_df["play_id"] != this_game.game_events_df["play_per_game"], :]
    first_mismatch = mismatched_play_ids.loc[mismatched_play_ids["play_id"].diff() != mismatched_play_ids["play_per_game"].diff(), :]

    game_events_mismatched = this_game.game_events_df.loc[(this_game.game_events_df["play_per_game"].isin(first_mismatch["play_per_game"]))  &\
                                                          (this_game.game_events_df["play_id"].isin(first_mismatch["play_id"]))
                                                , ["game_str", "play_id", "play_per_game", "event_code"]]
    
    mismatches = pd.concat([mismatches, game_events_mismatched])


# Tells me that there are 138 times where there is a discontinuity in the counting of play_id and play_per_game
print(mismatches[["game_str", "play_id", "play_per_game"]].drop_duplicates().shape)


```


Here is a sample of the mismatches:

|index |game_str            |play_id|play_per_game|
|------|--------------------|-------|-------------|
|1     |1900_01_TeamKJ_TeamB|178    |179          |
|2     |1900_03_TeamKJ_TeamB|166    |167          |
|3     |1900_05_TeamKK_TeamB|205    |206          |




### There are some instances where play_id and play_per_game appear to be incorrectly indexed

In the below sample, it appears that play_id, at_bat, and play_per_game stopped counting upwards! 

|index|game_str|play_id|at_bat |play_per_game |timestamp |player_position  | event_code  |event             |
|---|---------------------|---|---|----|--------|---|---|------------------|
|810 |1903_02_TeamNE_TeamA2 |210 |67 |211 |8018687 |10 |4  |ball hit into play|
|811 |1903_02_TeamNE_TeamA2 |210 |67 |211 |8018737 |0  |5  |end of play       |
|812 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8050687 |1  |1  |pitch             |
|813 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8051187 |0  |5  |end of play       |
|814 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8051187 |2  |2  |ball acquired     |
|815 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8087787 |1  |1  |pitch             |
|816 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8088237 |0  |5  |end of play       |
|817 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8088237 |2  |2  |ball acquired     |
|818 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8110437 |1  |1  |pitch             |
|819 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8110987 |2  |2  |ball acquired     |
|820 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8110987 |0  |5  |end of play       |
|821 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8146687 |1  |1  |pitch             |
|822 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8147087 |10 |4  |ball hit into play|
|823 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8152537 |6  |2  |ball acquired     |
|824 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8152587 |0  |5  |end of play       |
|825 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8189637 |1  |1  |pitch             |
|826 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8190137 |2  |2  |ball acquired     |
|827 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8190137 |0  |5  |end of play       |
|828 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8211287 |1  |1  |pitch             |
|829 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8211787 |2  |2  |ball acquired     |
|830 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8211787 |0  |5  |end of play       |
|831 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8230737 |1  |1  |pitch             |
|832 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8231187 |0  |5  |end of play       |
|833 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8231187 |2  |2  |ball acquired     |
|834 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8252287 |1  |1  |pitch             |
|835 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8252737 |2  |2  |ball acquired     |
|836 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8252737 |0  |5  |end of play       |
|837 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8270787 |1  |1  |pitch             |
|838 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8271237 |2  |2  |ball acquired     |
|839 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8271237 |0  |5  |end of play       |
|840 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8294987 |1  |1  |pitch             |
|841 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8295387 |10 |4  |ball hit into play|
|842 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8295437 |0  |5  |end of play       |
|843 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8326187 |1  |1  |pitch             |
|844 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8326687 |2  |2  |ball acquired     |
|845 |1903_02_TeamNE_TeamA2 |211 |69 |222 |8326687 |0  |5  |end of play       |




## 



Other issues:
- disagreement between runners on base
- players not in the correct spot?
    - its like the ball and players are not on the same time scale?
    - some plays are good though: 1903_23_TeamNA_TeamA1_play148--steal, not picked

