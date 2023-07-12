# This file contains tests on the Game class so I can keep try of known data issues

import numpy as np
import pandas as pd
import os

from src.utils import *
from src.plotting import Baseball_Field
from src.game import Game

import pytest



# Some of this exploration is informed by 
# every half inning of 1903_30 should work, except for the bottom of the 9th


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5



    
    
    
    
    
    
