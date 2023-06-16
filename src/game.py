import pandas as pd
import os

# some mappings to make my life easier
EVENT_CODE_TO_DESC = {1 : "pitch",
                      2 : "ball acquired",
                      3 : "throw (ball-in-play)",
                      4 : "ball hit into play",
                      5 : "end of play",
                      6 : "pickoff throw",
                      7 : "ball acquired - unknown field position",
                      8 : "throw (ball-in-play) - unknown field position",
                      9 : "ball deflection",
                      10 : "ball deflection off of wall",
                      11 : "home run",
                      16 : "ball bounce",
                      None : None
                     }

PLAYER_POSITION_CODE_TO_DESC = {1 : "P",
                      2 : "C",
                      3 : "1B",
                      4 : "2B",
                      5 : "3B",
                      6 : "SS",
                      7 : "LF",
                      8 : "CF",
                      9 : "RF",
                      10 : "Runner 1st",
                      11 : "Runner 2nd",
                      16 : "Runner 3rd"
                     }

class Game:
    def __init__(self, which_game, file_path="data/"):
        
        # compute a bunch of things to help me later
        self.which_game = which_game
        
        game_string_tokens =  which_game.split("_")
        
        self.home_team = game_string_tokens[-1]
        self.away_team = game_string_tokens[-2]
        
        self.season = game_string_tokens[0]
        self.game_num = game_string_tokens[1]
        
        # read in all my data
        self.game_info_df = pd.read_csv(file_path + "game_info/game_info-" + which_game + ".csv", index_col=0)
        self.game_events_df = pd.read_csv(file_path + "game_events/game_events-" + which_game + ".csv", index_col=0)
        self.game_events_df["event"] = self.game_events_df["event_code"].map(lambda x: EVENT_CODE_TO_DESC[x])
        
        self.ball_pos_df = pd.read_csv(file_path + "ball_pos/ball_pos-" + which_game + ".csv", index_col=0)
        
        player_pos_path = file_path + "player_pos/" + self.home_team + "/player_pos-"
        player_pos_path += self.season + "_" + self.home_team + "/player_pos-" + which_game + ".csv"
        self.player_pos_df = pd.read_csv(player_pos_path, index_col=0)
        
        # compute velocities so I have 
        # these should get smoothed and the names and times should maybe change the name from new lol
        self.new_ball_pos = self._compute_velos(self.ball_pos_df, ["play_id"], ["timestamp", "ball_position_x", "ball_position_y", "ball_position_z"])
        self.new_player_pos = self._compute_velos(self.player_pos_df, ["play_id", "player_position"], ["timestamp", "field_x", "field_y"])
        
        self.timestamp_df = self.collect_all_timestamps(self.new_ball_pos, self.new_player_pos, self.game_events_df)
        
        self.this_ts_fielders = None
        self.this_ts_batters = None
        self.this_ts_ball = None
        
        
    def __repr__(self):
        
        game_string = self.which_game + "\n"
        game_string += "game_info shape: " + str(self.game_info_df.shape) + "\n"
        game_string += "game_events shape: " + str(self.game_events_df.shape) + "\n"
        game_string += "ball_pos shape: " + str(self.ball_pos_df.shape) + "\n"
        game_string += "player_pos shape: " + str(self.player_pos_df.shape) + "\n"
        
        return game_string
    
    def _compute_velos(self, df, group_by_cols, cols):
        
        lagged_df = df.groupby(group_by_cols)[cols].shift(1)
        lagged_df.columns = ["lag_1_" + s for s in cols]
        
        diff_df = df.groupby(group_by_cols)[cols].diff()
        diff_df.columns = ["diff_" + s for s in cols]
        
        velo_df = diff_df[["diff_" + s for s in cols]].div(diff_df["diff_timestamp"] / 1000, axis=0)
        cols.remove("timestamp")
        
        velo_df = velo_df.loc[:, ["diff_" + s for s in cols]]
        velo_df.columns = [s.replace("position", "velo").replace("field", "velo") for s in cols]
        
        return pd.concat([df, lagged_df, diff_df, velo_df], axis=1)
        
    
    def _smooth_columns(self, df, cols):
        pass
    
        # the easiest would be like a moving average 
        # with more effort, could do a Kalman filter?
        
        
    def collect_all_timestamps(self, ball_df, player_df, game_events_df, cols = ["play_id", "timestamp"]):
        """
        A utility function for identifying all the timestamps across the different files
        for convenience when making a gif, etc
        
        
        can be used outside of the obejct too
        """

        timestamp_df = pd.concat([self.new_ball_pos[cols], self.new_player_pos[cols], self.game_events_df[cols]]).groupby("play_id").value_counts().reset_index() 

        timestamp_df = timestamp_df[cols].drop_duplicates().sort_values(cols)
        
        return timestamp_df
        
    def get_this_play_ts(self, play_id):
        """
        a util for returning a specific play's timestamps
        """
        
        return self.timestamp_df.loc[self.timestamp_df["play_id"] == play_id, "timestamp"].values
