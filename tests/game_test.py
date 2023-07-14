# This file contains tests on the Game class so I can keep try of known data issues

import numpy as np
import pandas as pd
import os

from src.utils import *
from src.plotting import Baseball_Field
from src.game import Game

import pytest

pd.options.mode.chained_assignment = None  # default='warn'


# Some of this exploration is informed by 
# every half inning of 1903_30 should work, except for the bottom of the 9th



def test_working_full_game_1903_30():
    """
    
    I have hand validated all of these plays and situations and I am pretty confident they are all outs
    
    """
    bf_1903_30 = Baseball_Field("1903_30_TeamNB_TeamA1")
    game_info_1903_30 = bf_1903_30.game_obj.game_info_df.copy()
    
    
    this_game_outs = game_info_1903_30.loc[game_info_1903_30["this_play_outs"] > 0, "play_per_game"].values
    
    true_this_game_outs = [
        3, 7, 11, 29, 46, 56, 62, 65, 75, 85, 87, 90, 94, 97,
        109, 114, 119, 121, 122, 128, 131, 132, 134, 137, 138, 142,
        144, 159, 160, 165, 171, 178, 182, 198, 200, 202, 206, 211, 215,
        219, 223, 227, 234, 249, 256, 260, 263, 267, 271, 275, 276
    ]
    
    for ppg in this_game_outs:
        assert ppg in true_this_game_outs
    

def test_not_working_half_inning_game_1900_01():
    """
    definitely don't trust this half because the last play was a HR,
    so it can't be a working half inning
    """
    bf_1900_01 = Baseball_Field("1900_01_TeamKJ_TeamB")
    game_info_1900_01 = bf_1900_01.game_obj.game_info_df.copy()
    
    # definitely don't trust this half because the last play was a HR 
    assert game_info_1900_01.loc[(game_info_1900_01["inning"] == 2) & (game_info_1900_01["top_bottom_inning"] == "Top"), "trust_this_half"].sum() == 0


def test_double_plays():
    """
    a subset of things I know are definitely double plays
    
    """
    ### I have gifs for these
    
    bf_1903_13 = Baseball_Field("1903_13_TeamNG_TeamA3")
    game_info_1903_13 = bf_1903_13.game_obj.game_info_df.copy()
    
    this_game_dp = game_info_1903_13.loc[game_info_1903_13["this_play_outs"] > 0, "play_per_game"].values

    assert bf_1903_13.game_obj.get_ppg_from_pid(236) in this_game_dp
    
    
    ### I have gifs for these
    
    bf_1903_17 = Baseball_Field("1903_17_TeamNI_TeamA3")
    game_info_1903_17 = bf_1903_17.game_obj.game_info_df.copy()
    
    this_game_dp = game_info_1903_17.loc[game_info_1903_17["this_play_outs"] > 0, "play_per_game"].values

    assert bf_1903_17.game_obj.get_ppg_from_pid(114) in this_game_dp
    
