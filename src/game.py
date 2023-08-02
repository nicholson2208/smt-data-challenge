# This file contains a class for the Game

import numpy as np
import pandas as pd
import os

# some mappings to make my life easier
EVENT_CODE_TO_DESC = {
    1 : "pitch",
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


PLAYER_POSITION_CODE_TO_DESC = {
    1 : "P",
    2 : "C",
    3 : "1B",
    4 : "2B",
    5 : "3B",
    6 : "SS",
    7 : "LF",
    8 : "CF",
    9 : "RF",
    10 : "Batter",
    11 : "Runner 1st",
    12 : "Runner 2nd",
    13 : "Runner 3rd"
 }

class Game:
    def __init__(self, which_game, file_path="data/", debug_mode=False):
        """
        When you instantiate a Game object, all of the data gets read, prepped, and cleaned
        
        Params:
            which_game: (str)
                - a string representation of the game, looks like "1902_24_TeamMA_TeamA1"
            file_path: (str)
                - where your data lives
                
        """
        # compute a bunch of info to help me later
        self.which_game = which_game
        
        game_string_tokens =  which_game.split("_")
        
        self.home_team = game_string_tokens[-1]
        self.away_team = game_string_tokens[-2]
        
        self.season = game_string_tokens[0]
        self.game_num = game_string_tokens[1]
        
        self.ts_lag_df = None
        
        # Possible TODOs:
        # - runs for each team
        
        # TODO: I don't know that I will fill this in for each case, but I will for the easy ones
        self.winner = None
        
        self.which_half_innings_are_valid = {}
        
        #### read in all my data ###
        
        # read in game info
        self.game_info_df = pd.read_csv(file_path + "game_info/game_info-" + which_game + ".csv", index_col=0)
        
        # read in game events
        self.game_events_df = pd.read_csv(file_path + "game_events/game_events-" + which_game + ".csv", index_col=0)
        
        # play per game and play_id are not the same, make a mapper between the two
        self.play_id_to_per_game_mapper = self.game_events_df[["play_id" , "play_per_game"]].drop_duplicates()
        
        # read in ball pos
        self.ball_pos_df = pd.read_csv(file_path + "ball_pos/ball_pos-" + which_game + ".csv", index_col=0)        
        
        # read in play pos
        player_pos_path = file_path + "player_pos/" + self.home_team + "/player_pos-"
        player_pos_path += self.season + "_" + self.home_team + "/player_pos-" + which_game + ".csv"
        self.player_pos_df = pd.read_csv(player_pos_path, index_col=0)
        
        
        if debug_mode:
            # I think I have an infinite recursion somewhere
            # add this so I can just skip
            
            return
        
        #### clean and impute data
        # add a bunch of fields to events to make my life easier
        self.game_events_df = self._prep_events_df(self.game_events_df)
        
        # self.new_ball_pos = self._compute_velos(self.ball_pos_df, ["play_id"], ["timestamp", "smoothed_ball_position_x", "smoothed_ball_position_y", "smoothed_ball_position_z"])
        
        # check whether we should bother with the timestamp lining up thing (and data rewriting?)
        self.avg_ball_and_player_dist = self._check_positions_when_acquired(
            self.game_events_df, 
            self.player_pos_df, 
            self.ball_pos_df
        )
        
        if self.avg_ball_and_player_dist > 5:
            print("Distance between ball and player is large on average, should maybe clean up {}"\
                  .format(self.avg_ball_and_player_dist))
            
            self.player_pos_df = self._align_ball_and_player_ts(
                self.game_events_df, 
                self.player_pos_df, 
                self.ball_pos_df
            )
            
        # compute some velos, descs, etc
        self.new_player_pos = self._prep_player_pos_df(self.player_pos_df)   
        
        # fill the gaps in the ball_pos data
        self.ball_pos_df = self._fill_ball_pos_when_acquired(
            self.game_events_df, 
            self.player_pos_df, 
            self.ball_pos_df)

        # smoothing should go here
        self.ball_pos_df = self._smooth_ball_position(self.ball_pos_df)
        
        # compute velocities so I have that for further analysis and plotting
        # these should get smoothed and the names and times should maybe change the name from new lol
        self.new_ball_pos = self._compute_velos(
            self.ball_pos_df, 
            ["play_id"], 
            ["timestamp",
             "ball_position_x", 
             "ball_position_y", 
             "ball_position_z",
             "smoothed_ball_position_x", 
             "smoothed_ball_position_y", 
             "smoothed_ball_position_z"
            ]
        )

    
        # fill in the missing players in game_info with player_pos data
        self.game_info_df = self._prep_info_df(self.game_info_df)
        
        # compute features at the event level!
        # add in angle of throw to first, elevation angle, norminal velo
        self.game_events_df = self._add_throw_details_to_events(self.game_events_df)
        
        # add more features for the thrower, batter, ball at event level
        self.game_events_df = self._add_player_details_to_events(
            self.game_events_df,
            self.new_ball_pos, 
            self.new_player_pos
        )
        
        self.timestamp_df = self.collect_all_timestamps(
            self.new_ball_pos, 
            self.new_player_pos, 
            self.game_events_df
        )

        
        self.this_ts_fielders = None
        self.this_ts_batters = None
        self.this_ts_ball = None
        
        
    def __repr__(self):
        
        game_string = self.which_game + "\n"
        game_string += "game_info shape: " + str(self.game_info_df.shape) + "\n"
        game_string += "\t\tNumber of invalid half inning"
        game_string += "game_events shape: " + str(self.game_events_df.shape) + "\n"
        game_string += "ball_pos shape: " + str(self.ball_pos_df.shape) + "\n"
        game_string += "player_pos shape: " + str(self.player_pos_df.shape) + "\n"
        
        return game_string
    
    
    def _check_positions_when_acquired(self, game_events, player_pos, ball_pos):
        """
        This will let me know whether I need to write that function to correct the ts, I think I won't mostly

        """
        # events when the ball is acquired by not the catcher, gets rid of pitches
        ball_acq_ts = game_events.loc[
            (game_events["event"] == "ball acquired") & 
            (game_events["player_position"] != 2)
            ,
            ["play_id", "timestamp", "player_position"]
        ]

        # where the ball is when it is acquired
        ball_pos_when_acquired = ball_pos.loc[
            ball_pos["timestamp"].isin(ball_acq_ts.timestamp.values), 
            ["play_id", "ball_position_x", "ball_position_y"]
        ]

        # merge them so we can compute the dist
        merged_pos_df = player_pos.loc[
            (player_pos["timestamp"].isin(ball_acq_ts.timestamp.values)) &
            (player_pos["player_position"].isin(ball_acq_ts.player_position.values)),
            ["play_id", "field_x", "field_y"]
        ].merge(ball_pos_when_acquired, how="left", on="play_id")

        merged_pos_df["dist"] = merged_pos_df.apply(
            lambda row: 
            np.sqrt((row["field_x"] - row["ball_position_x"]) ** 2 + 
                    (row["field_y"] - row["ball_position_y"]) ** 2),
            axis = 1 
        )

        return merged_pos_df.groupby("play_id")["dist"].min().mean()
    
    
    def _align_ball_and_player_ts(self, game_events, player_pos, ball_pos, margin=3):
        """
        There are many instances where it seems like the ball and player are lagged in someway
        
        Make a function to line up timestamps based on the distance the ball is from the player 
        that acquired the ball when it is marked as acquired
        
        
        margin (int or float) defaults to 3
             how far we allow the ball to be away from the player and still say acquired in feet
             3 is roughly an arms length, could do better with limb data
        
        """
        game_events = game_events.copy()
        player_pos = player_pos.copy()
        ball_pos = ball_pos.copy()
        
        # get all of the players and times when the ball was acquired
        ball_acq_event = game_events.loc[
            game_events["event"] == "ball acquired"
        ][["play_id", "player_position", "timestamp"]]
        
        # get ball_position of all the ball acq for each play
        ball_acq_pos = ball_pos.merge(
            ball_acq_event, 
            how="inner", 
            on=["play_id", "timestamp"]
        )[["play_id", "ball_position_x", "ball_position_y"]]
        
        # get the player_pos for each player that first acquires the ball for each play
        player_pos_acq = player_pos.merge(
            ball_acq_event, 
            how="inner", 
            on=["play_id", "player_position"], 
            suffixes=["", "_ball_acq"]
        )
        
        # merge the ball pos when first acquired and player dfs
        combined_acq = player_pos_acq.merge(ball_acq_pos, on="play_id", how="left")

        # get the distance between the ball and player who acquired
        combined_acq["delta_dist"] = np.sqrt(
            (combined_acq["field_x"] - combined_acq["ball_position_x"])**2 +\
            (combined_acq["field_y"] - combined_acq["ball_position_y"])**2                                    
        )

        # I think the raw min won't work because you could reach for the ball and 
        # then run over to where you picked it so have a margin and pick the first
        # time you get close enough
        when_within_margin = combined_acq[
            combined_acq["delta_dist"] < margin
        ].groupby(["play_id", "player_position"]).min("delta_dist")
        
        when_within_margin["time_offset"] = (when_within_margin["timestamp"] - when_within_margin["timestamp_ball_acq"])
        
        # self.ts_lag_df = when_within_margin
        # this step picks corrects for the case where the first acquiring player
        # doesn't have to move (and thus is already in the correct spot too early)
        when_within_margin =  when_within_margin.loc[
            when_within_margin.groupby("play_id")["time_offset"].idxmax()
        ]
 
        plays_within_margin = when_within_margin.reset_index()["play_id"].unique()

        # pick a looser margin for the other ones that don't work
        # so we at least have coverage
        plays_that_not_within_margin = set(combined_acq["play_id"].unique()) - \
            set(plays_within_margin)

        not_within_margin = combined_acq.loc[
            (combined_acq["play_id"].isin(plays_that_not_within_margin)) &
            (combined_acq["delta_dist"] < (2 * margin))
        ].groupby(["play_id", "player_position"]).min()
        
        not_within_margin["time_offset"] = (not_within_margin["timestamp"] - not_within_margin["timestamp_ball_acq"])

        not_within_margin =  not_within_margin.loc[
            not_within_margin.groupby("play_id")["time_offset"].idxmax()
        ]
        
        all_plays = pd.concat([not_within_margin, when_within_margin]).sort_values("play_id")        
            
        # we already computed the lags needed for each play to line up the ball with the player + margin
        ts_lag_df = all_plays.reset_index()[["play_id", "time_offset"]]

        # put this into a df, so I can inspect later
        self.ts_lag_df = ts_lag_df

        player_pos["old_ts"] = player_pos["timestamp"]

        # which TS to anchor to? ball makes the gif work, but ruins the events on screen
        # its minus if merging with player pos, addition if ball
        
        # merge only the positive, because the others are probs 
        # just the ball getting to the front of someone
        new_player_pos = player_pos.merge(ts_lag_df[ts_lag_df > 0], 
                               how = "left", 
                               left_on="play_id",
                               right_on="play_id"
        )
        
        new_player_pos["timestamp"] = new_player_pos.apply(
            lambda row:                                           
            row["old_ts"] - (row["time_offset"] if pd.notnull(row["time_offset"]) else 0),
            axis=1
        )

        return new_player_pos

    
    def _fill_ball_pos_when_acquired(self, game_events, player_pos, ball_pos):
        """
        This is making an assumption that (1) the ball data is missing when a ball is acquired and (2) that the fielder's position
        is the best proxy for where the ball is when it is missing (we can't see limbs!)

        """
        game_events = game_events.copy()
        player_pos = player_pos.copy()
        ball_pos = ball_pos.copy()

        # get the windows in the game where a ball is in someone's glove or hand
        ball_acquired_windows = game_events.loc[
            (game_events["event_code"] == 2) & 
            (game_events["next_event_code"] != 5)
            ,
            :
        ]

        for player, this_ts, next_ts in zip(ball_acquired_windows["player_position"], ball_acquired_windows["timestamp"],\
                                            ball_acquired_windows["next_event_ts"]):

            play_pos_during_window = player_pos.loc[
                (player_pos["player_position"] == player) & 
                (player_pos["timestamp"] > this_ts) & 
                (player_pos["timestamp"] < next_ts),
                :
            ]

            # I might mess with this assumption later -- you could jump and be scooping or whatever here
            play_pos_during_window["ball_position_z"] = 5

            play_pos_during_window = play_pos_during_window.loc[
                :, 
                ["game_str",
                 "play_id", 
                 "timestamp",
                 "field_x",
                 "field_y",
                 "ball_position_z"]
            ]
            
            play_pos_during_window.columns = [
                "game_str", 
                "play_id", 
                "timestamp", 
                "ball_position_x", 
                "ball_position_y", 
                "ball_position_z"
            ]

            ball_pos = pd.concat([ball_pos, play_pos_during_window])


        ball_pos.sort_values(["play_id", "timestamp"], inplace=True)

        return ball_pos
    
    
    def _prep_player_pos_df(self, player_pos_df):
        """
        prep the player_position df
        
        add human readable labels, compute velos, etc
        
        """
        
        player_pos = self.player_pos_df.copy()
        player_pos["player_position_desc"] = player_pos["player_position"].map(PLAYER_POSITION_CODE_TO_DESC)
        
        player_pos = self._compute_velos(
            player_pos, 
            ["play_id", "player_position"], 
            ["timestamp", "field_x", "field_y"]
        )

        return player_pos
    
    
    def _prep_info_df(self, game_info_df):
        """
        A utility for adding relevant fields to game info table, like at_bat and outs, etc.
        
        """
        
        game_info = game_info_df.copy()
        
        ### Make some columns to be filled in with the outs


        # the number of baserunners on a given play
        game_info["n_br"] = game_info[["first_baserunner", "second_baserunner", "third_baserunner"]].apply(lambda row: sum(row.apply(lambda x: 0 if x == 0 else 1)), axis=1)

        # placeholder columns that will get filled in
        game_info["prev_outs"] = np.nan
        game_info["this_play_outs"] = np.nan
        
        game_info["trust_this_play"] = 1

        # you know for certain that there are no outs when it is the first batter in the half inning
        switiching_sides_indices = game_info.loc[
            game_info["top_bottom_inning"].shift() != game_info["top_bottom_inning"]
        ].index

        # fill in a zero when there are no outs
        game_info.loc[switiching_sides_indices, "prev_outs"] = 0
        
        
        ### There are differences in the tracking data, and the game_info table
        # try to line up the game_info and player_pos data
        
        game_info = self._fix_info_player_pos_br_disagreements(game_info, self.new_player_pos)
       
        # TODO: more stuff goes here!
        pass
    
        # TODO: maybe do something with which_innings_are_valid
        game_info, self.which_half_innings_are_valid = self.impute_outs(game_info)
        
        game_info = self._fill_whether_to_trust_half_inning(game_info)
        
        
        return game_info

    
    def _fix_info_player_pos_br_disagreements(self, game_info, player_pos):
        """
        
        There are differences in the tracking data, and the game_info table
        
        try to line up the game_info and player_pos data
        
        """
        game_info = game_info.copy()
        
        cols = ["play_id", "player_position_desc"]

        which_brs_present_which_play = self.new_player_pos.loc[
            self.new_player_pos["player_position"].isin([10, 11, 12, 13])
        ].groupby(cols).size().unstack(fill_value=0)
        
        which_brs_present_which_play = which_brs_present_which_play.apply(
            lambda row: 
            row.apply(lambda x: x if x == 0 else 1)
            , axis=1
        )

        # do the mapping between play per game and play id here
        which_brs_present_which_play = which_brs_present_which_play.merge(
            self.play_id_to_per_game_mapper, 
            how="left", 
            on="play_id"
        )
        
        filled_info = game_info.merge(
            which_brs_present_which_play.drop("play_id", axis=1), 
            how="left", 
            on="play_per_game"
        )

        # TODO: fill in when batters are 0?
        # I think the first thing is the 0 batter fill in, then then the br thing

        # make a col assuming these two sources agree
        filled_info["player_pos_and_info_agree"] = 1
        
        # make a flag for when they don't agree
        filled_info.loc[
            ((filled_info["first_baserunner"] > 0) ^ (filled_info["Runner 1st"] > 0)) |
            ((filled_info["second_baserunner"] > 0) ^ (filled_info["Runner 2nd"] > 0)) |
            ((filled_info["third_baserunner"] > 0) ^ (filled_info["Runner 3rd"] > 0))
            ,
            "player_pos_and_info_agree"
        ] = 0
        
        
        # track that something is fishy with this play
        filled_info.loc[
            ((filled_info["first_baserunner"] > 0) ^ (filled_info["Runner 1st"] > 0)) |
            ((filled_info["second_baserunner"] > 0) ^ (filled_info["Runner 2nd"] > 0)) |
            ((filled_info["third_baserunner"] > 0) ^ (filled_info["Runner 3rd"] > 0))
            ,
            "trust_this_play"
        ] = 0

        ## ASSUMPTION: the player_pos data is generally more accurate?
        ## just fill in a 1 where there is a 0 in game info
        filled_info.loc[
            ((filled_info["first_baserunner"] == 0) &
             (filled_info["Runner 1st"] > 0))
            , "first_baserunner"
        ] = 1
        
        filled_info.loc[
            ((filled_info["second_baserunner"] == 0) &
             (filled_info["Runner 2nd"] > 0))
            , "second_baserunner"
        ] = 1
        
        filled_info.loc[
            ((filled_info["third_baserunner"] == 0) &
             (filled_info["Runner 3rd"] > 0))
            , "third_baserunner"
        ] = 1
        
        return filled_info
    
    
    def _fill_whether_to_trust_half_inning(self, game_info):
        """
        theres lots of things that iffy about this data, I want to know which I should trust
        based on whether I had to apply assumptions to get here or not
        
        """
        game_info = game_info.copy()
        
        # if any of the plays are suspect, don't trust the whole half inning, (because you need the whole sequence for outs to work)
        valid_halfs = game_info.groupby(
            ["inning", "top_bottom_inning"]
        ).min()[["trust_this_play"]].reset_index()
        
        # a valid half is one that has an out sequence that works
        valid_halfs["valid_half"] = valid_halfs.apply(
            lambda row: 
            1 if (self.which_half_innings_are_valid[str(row["inning"])+"_"+row["top_bottom_inning"]]) else 0
            , axis=1
        )
        
        # a half you should def trust doesn't have any br gaps that needed to be squared away
        valid_halfs["trust_this_half"] = valid_halfs.apply(
            lambda row: 1 if (row["trust_this_play"] and row["valid_half"]) else 0
            , axis=1
        )
                
        game_info = game_info.merge(
            valid_halfs[["inning", "top_bottom_inning", "valid_half", "trust_this_half"]], 
            how="left", 
            on=["inning", "top_bottom_inning"]
        )
        
        return game_info
        
        
    def _prep_events_df(self, df):
        """
        A utility for adding useful columns to the game_events table
        """
        
        game_events = df.copy()
        game_events = game_events.sort_values(["timestamp", "event_code"], ascending=[True, True])

        
        game_events["event"] = game_events["event_code"].map(lambda x: EVENT_CODE_TO_DESC[x])
        
        game_events["next_event_code"] =  game_events.groupby("play_per_game")["event_code"].shift(-1)
        game_events["next_event"] =  game_events.groupby("play_per_game")["event"].shift(-1)
        game_events["next_event_ts"] =  game_events.groupby("play_per_game")["timestamp"].shift(-1)
        
        
        game_events["prev_event_code"] =  game_events.groupby("play_per_game")["event_code"].shift(1)
        game_events["prev_event"] =  game_events.groupby("play_per_game")["event"].shift(1)
        game_events["prev_event_ts"] =  game_events.groupby("play_per_game")["timestamp"].shift(1)
    
    
        return game_events
    
    
    def _smooth_ball_position(self, df):
        """
        
        See exploration in SmoothingAnalysis notebook
        
        """
        
        # the easiest would be like a moving average 
        # with more effort, could do a Kalman filter?
        
        # I am not actually sure I need this
        
        smoothed_pos_df = df.copy()

        smoothed_xy = df.groupby("play_id")[["timestamp", "ball_position_x", "ball_position_y", "ball_position_z"]]\
            .rolling(3, center=True, closed="both").mean()
 
        smoothed_pos_df["smoothed_ball_position_x"] = smoothed_xy["ball_position_x"].values
        smoothed_pos_df["smoothed_ball_position_y"] = smoothed_xy["ball_position_y"].values
        smoothed_pos_df["smoothed_ball_position_z"] = smoothed_xy["ball_position_z"].values
        
        return smoothed_pos_df
    
    
    def _compute_velos(self, df, group_by_cols, cols):
        """
        A utility to compute velocities at the row level
        
        I suggest smoothing and resampling the data before this gets called
        
        """
        
        lagged_df = df.groupby(group_by_cols)[cols].shift(1)
        lagged_df.columns = ["lag_1_" + s for s in cols]
        
        diff_df = df.groupby(group_by_cols)[cols].diff()
        diff_df.columns = ["diff_" + s for s in cols]
        
        velo_df = diff_df[["diff_" + s for s in cols]].div(diff_df["diff_timestamp"] / 1000, axis=0)
        cols.remove("timestamp")
        
        velo_df = velo_df.loc[:, ["diff_" + s for s in cols]]
        velo_df.columns = [s.replace("position", "velo").replace("field", "velo") for s in cols]
        
        return pd.concat([df, lagged_df, diff_df, velo_df], axis=1)
    
    def _add_throw_details_to_events(self, df):
        """
        needs the new_ball_pos to work, needs to be a separate function
        """
        
        game_events = df.copy()

        
        # a column for the xy_throw_angle, will be na if the event is not a throw
        game_events["xy_throw_angle"] = np.nan
        game_events["elevation_throw_angle"] = np.nan
        game_events["throw_velo"] = np.nan


        # fill in xy
        game_events.loc[
            game_events["event"] == "throw (ball-in-play)", 
            "xy_throw_angle"
        ] = game_events.loc[
            game_events["event"] == "throw (ball-in-play)"
            , :
        ].apply(
            lambda row: \
            self._fill_throw_details(row["timestamp"], self.new_ball_pos, which="xy")
            , axis = 1
        )
        
        # fill in elevation
        game_events.loc[
            game_events["event"] == "throw (ball-in-play)", 
            "elevation_throw_angle"
        ] = \
            game_events.loc[
            game_events["event"] == "throw (ball-in-play)",
            :
        ].apply(lambda row: \
                self._fill_throw_details(row["timestamp"], self.new_ball_pos, which="elevation")
                , axis = 1
               )
        
         # fill in velo
        game_events.loc[
            game_events["event"] == "throw (ball-in-play)",
            "throw_velo"
        ] = game_events.loc[
            game_events["event"] == "throw (ball-in-play)"
            , :
        ].apply(lambda row: \
                self._fill_throw_details(row["timestamp"], self.new_ball_pos, which="velo")
                , axis = 1
               )

        
        
        return game_events
    
    
    def _compute_throw_details(self, a, which = "xy", target_point = np.array([63.63961031, 63.63961031])):
        """
        A utility to compute the throw angle in the xy plane to an arbitary point
        
        target_point defaults to first base

        """
    
        if which == "xy":    
            try:
                # make a vector from the first point to the target point
                xy_vect_to_target = target_point - a[["ball_position_x", "ball_position_y"]].iloc[0].values

                # scale it to be a unit vector
                unit_xy_vect_to_target = xy_vect_to_target / np.sqrt(xy_vect_to_target.dot(xy_vect_to_target))

                # Maybe the whole window so we don't get noise?
                throw_velo_xy_vect = a[["ball_position_x", "ball_position_y"]].iloc[-1].values \
                    - a[["ball_position_x", "ball_position_y"]].iloc[0].values

                # the other one is a unit vect, so we don't need to divide here
                xy_angle_to_first_rad = np.arccos(throw_velo_xy_vect.dot(unit_xy_vect_to_target) / np.sqrt(throw_velo_xy_vect.dot(throw_velo_xy_vect)))

                xy_angle_to_first_deg = xy_angle_to_first_rad * 180 / np.pi

                # hmm there are some times where you might want to miss the bag -- e.g. throws from catcher! 
                return xy_angle_to_first_deg
            
            except:

                # this should only happen when there isn't ball_pos data, which happens sometimes 

                return np.nan
        elif which == "elevation":
            # compute the angle of elevation
            try:
                throw_velo_vect = a[["ball_position_x", "ball_position_y", "ball_position_z"]].iloc[-1].values \
                    - a[["ball_position_x", "ball_position_y", "ball_position_z"]].iloc[0].values

                # a unit vector up
                unit_z_vect = np.array([0, 0, 1])

                # (PI/2 - radians from straight up)
                elevation_angle_rad = (np.pi/2 - np.arccos(throw_velo_vect.dot(unit_z_vect) / np.sqrt(throw_velo_vect.dot(throw_velo_vect))))
                elevation_angle_deg = elevation_angle_rad * 180 / np.pi
                
                return elevation_angle_deg
            
            except:
                return np.nan
        elif which == "velo":
            try:
            
                throw_velo_vect = a[["ball_position_x", "ball_position_y", "ball_position_z"]].iloc[-1].values \
        - a[["ball_position_x", "ball_position_y", "ball_position_z"]].iloc[0].values

                ball_flight_time_sec = (a["timestamp"].iloc[-1] - a["timestamp"].iloc[0])/1000

                # this is feet per (ball_flight_time) / 1.467 [fps to mph]
                velo = np.sqrt(throw_velo_vect.dot(throw_velo_vect)) / ball_flight_time_sec / 1.467

                return velo
            except:
                return np.nan
            
    
    def _fill_throw_details(self, timestamp, ball_pos_df, which = "xy", target_point = np.array([63.63961031, 63.63961031])): 
        """
        the helper function to actual fill in a given throw's angle to the target point
        
    
        """

        # ball_pos_df = new_ball_pos_df.copy()

        buffer_ms = -10
        snapshot_time = 250

        # find when the ball is in the air with a buffer or not
        ball_in_air_df = ball_pos_df.loc[(ball_pos_df["timestamp"] >= (timestamp - buffer_ms)) &\
                                           (ball_pos_df["timestamp"] <= (timestamp + snapshot_time)),
                                           # (ball_pos_1903_01["timestamp"] <= temp_throws["next_event_ts"].values[0] + buffer_ms), # this is for the whole throw
                                           :
                                          ] 

        # print(ball_in_air_df["play_id"].describe())
        angle = self._compute_throw_details(ball_in_air_df, which=which, target_point=target_point)

        return angle
    
    def _compute_player_details_at_throw(self, player_data, which=None, target_point = np.array([63.63961031, 63.63961031])):
        """
        for computing things like distance to first, etc
        
        """
        
        # find the x, y pos of the batter at the time of throw
        # player pos and velo

        try:
        
            batter_pos_at_throw = player_data[["field_x", "field_y"]].values[0]

            batter_vect_to_first = (target_point - batter_pos_at_throw)

            # find the distance of the batter to first (in ft)
            batter_dist_to_first = np.sqrt(batter_vect_to_first.dot(batter_vect_to_first))

            return batter_dist_to_first
        except:
            return np.nan
    
    def _fill_player_details_at_throw(self, timestamp, player_pos_df, which=None, thrower_position=None, target_point = np.array([63.63961031, 63.63961031])): 
        """
        a helper for filling in player details
        """
        player_stat = np.nan
        
        if which == "batter_dist":
            batter_data = player_pos_df.loc[
                (player_pos_df["timestamp"] == timestamp) &\
                (player_pos_df["player_position"] == 10)
                , ["play_id", "field_x", "field_y", "velo_x", "velo_y"]
            ]

            player_stat = self._compute_player_details_at_throw(batter_data, which=which, target_point=target_point)

      
        elif which == "thrower_x":
            
            try:
                player_stat = player_pos_df.loc[
                    (player_pos_df["timestamp"] == timestamp) &\
                    (player_pos_df["player_position"] == thrower_position)
                    , "field_x"
                ].values[0]
            except:
                pass
        
        elif which == "thrower_y":
            try:
                player_stat = player_pos_df.loc[
                    (player_pos_df["timestamp"] == timestamp) &\
                    (player_pos_df["player_position"] == thrower_position)
                    , "field_y"
                ].values[0]
            except:
                pass

        """
        elif which == "batter_x":
            
            try:
                player_stat = player_pos_df.loc[
                    (player_pos_df["timestamp"] == timestamp) &\
                    (player_pos_df["player_position"] == 10)
                    , "field_x"
                ].values[0]
            except:
                pass
        
        elif which == "batter_y":
            try:
                player_stat = player_pos_df.loc[
                    (player_pos_df["timestamp"] == timestamp) &\
                    (player_pos_df["player_position"] == 10)
                    , "field_y"
                ].values[0]
            except:
                pass
        """
        
        return player_stat
        
    
    def _add_player_details_to_events(self, df, ball_pos, player_pos):
        """
        needs the new_ball_pos to work, needs to be a separate function
        """
        game_events = df.copy()
        ball_pos = ball_pos.copy()
        player_pos = player_pos.copy()


        
        # a column for the batter dist to first, will be na if the event is not a throw
        game_events["batter_dist_to_first"] = np.nan

                
        
        game_events["thrower_x"] = np.nan
        game_events["thrower_y"] = np.nan
        
        """
        game_events["batter_x"] = np.nan
        game_events["batter_y"] = np.nan

        """
        
        # fill in batter dist from first for all events
        game_events.loc[
            # If I do this for all events I will have deltas that I can mess with in event to compute velo after the fact!
            :,
            #game_events["event"] == "throw (ball-in-play)", 
            "batter_dist_to_first"
        ] = game_events.loc[
            : # game_events["event"] == "throw (ball-in-play)"
            , :
        ].apply(
            lambda row: \
            self._fill_player_details_at_throw(row["timestamp"], self.new_player_pos, which="batter_dist")
            , axis = 1
        )


        # fill in thrower x for all throws
        # can't just be a merge because we don't know the thrower a priori
        game_events.loc[
           game_events["event"] == "throw (ball-in-play)", 
            "thrower_x"
        ] = game_events.loc[
            game_events["event"] == "throw (ball-in-play)"
            , :
        ].apply(
            lambda row: \
            self._fill_player_details_at_throw(
                row["timestamp"], 
                self.new_player_pos, 
                which="thrower_x", 
                thrower_position=row["player_position"]
            )
            , axis = 1
        )
        
        # thrower y for all throws
        game_events.loc[
           game_events["event"] == "throw (ball-in-play)", 
            "thrower_y"
        ] = game_events.loc[
            game_events["event"] == "throw (ball-in-play)"
            , :
        ].apply(
            lambda row: \
            self._fill_player_details_at_throw(
                row["timestamp"], 
                self.new_player_pos, 
                which="thrower_y", 
                thrower_position=row["player_position"]
            )
            , axis = 1
        )
        

        # everything that doesn't need to be computed can just be a merge!

        # fill in ball xyz for all events
        # I can merge on TS because I have already lined up the ball and players!
        game_events = game_events.merge(
            ball_pos[["timestamp", "ball_position_x", "ball_position_y", "ball_position_z"]],
            how = "left",
            on = "timestamp"            
        ) 
        
        # change names of cols for the batter, merge to get batter_x and batter_y
        batter_df = player_pos.loc[ 
            (player_pos["player_position"] == 10), 
            ["timestamp", "field_x", "field_y"]
        ]
        
        batter_df.rename(columns={"field_x" : "batter_x", "field_y" : "batter_y"}, inplace=True)
        
        game_events = game_events.merge(
            batter_df,
            how = "left",
            on = "timestamp"            
        ) 
               
        return game_events
    
        
    def _find_empty_cell(self, seq):
        """
        a util that takes an (n, 2) np.array() object and finds the index of the next nan value
        
        this is used to solve the outs sequence
        """
        index = None

        # this play outs is in the second column!
        for i, val in enumerate(seq[:, 1]):
            if np.isnan(val):
                return i

        return index
    

    def _is_valid_outs_assignment(self, half_inning_df, seq, this_play_outs, empty_cell_index):
        """
        The meat of the outs sequence solver -- given a game state and a proposed number of outs, 
        this function returns a bool for whether this arrangement is possible
        
        
        """
        # Assuming we have consecutive indices in half_inning_df!
        
        # define some lists for convenience
        all_batting_team = ["batter", "first_baserunner", "second_baserunner", "third_baserunner"]
        all_br = ["first_baserunner", "second_baserunner", "third_baserunner"]

        seq_len = seq.shape[0]

        this_row = half_inning_df.iloc[empty_cell_index]

        old_set_batting_team = set()
        prev_total_outs = 0

        if empty_cell_index != 0:
            # you need to set and check all of the things that look at the prev row 
            old_set_batting_team = set(half_inning_df.iloc[empty_cell_index - 1][all_batting_team])
            prev_total_outs = sum(seq[empty_cell_index - 1, :])

        # importantly, the data here are ints or sets of ints
        next_batter = None
        next_set_batting_team = set()
        next_set_br = set()
        next_second_br = None
        next_third_br = None

        # the play_per_game of HRs within this game
        hr_play_per_games = self.get_play_id_and_ppg_for_event("home run")["play_per_game"].values

        # technically, these aren't all flyouts that end the play (e.g. it could be a single, that an outfielder eats)
        # but every flyout should be here (unless, there are many plays that end after an outfielder throws it in)
        flyouts_that_end_play = self.get_play_id_and_ppg_for_event("ball acquired", 
                                                                   player_position=[7, 8, 9],
                                                                   next_event="end of play")["play_per_game"].values

        # if there is a next play to pick from
        if empty_cell_index < seq_len - 1:
            next_batter = half_inning_df.iloc[empty_cell_index + 1]["batter"]
            next_set_batting_team = set(half_inning_df.iloc[empty_cell_index + 1][all_batting_team])
            next_set_br = set(half_inning_df.iloc[empty_cell_index + 1][all_br])

            next_second_br = half_inning_df.iloc[empty_cell_index + 1]["second_baserunner"]
            next_third_br = half_inning_df.iloc[empty_cell_index + 1]["third_baserunner"]

        # again, the data here are ints or sets of ints
        this_batter = half_inning_df.iloc[empty_cell_index]["batter"]
        this_set_br = set(half_inning_df.iloc[empty_cell_index][all_br])
        this_first_br = half_inning_df.iloc[empty_cell_index]["first_baserunner"]
        this_second_br = half_inning_df.iloc[empty_cell_index]["second_baserunner"]
        this_third_br = half_inning_df.iloc[empty_cell_index]["third_baserunner"]
        this_set_batting_team = set(half_inning_df.iloc[empty_cell_index][all_batting_team])

        # do we have the same batter on the next play
        same_batter_next_play = this_batter == next_batter


        # how many outs we would have if we assigned this_play_outs to this index
        does_this_make_3 = prev_total_outs + this_play_outs
        this_play_per_game = half_inning_df.iloc[empty_cell_index]["play_per_game"]

        # to make a useful spot for breakpoints
        pass

        # TODO: It can't be an out if the batter is on base next play and a runner scores
        # TODO: Fielders choice out at home??

        if this_play_outs != 0 and this_play_per_game \
            in hr_play_per_games:
            # Outs can't go up on a home run
            return False

        if this_play_outs == 0 and this_batter not in next_set_br \
            and this_batter != next_batter and this_play_per_game not in hr_play_per_games:
            # if the batter is not on the bases when there is a new batter and it wasn't a HR then the batter got out:
            return False

        if this_play_outs > 1 and this_play_per_game in flyouts_that_end_play:
            # if the last thing that happens is a ball being acquired by an outfield, then there can't be more than 1 out on the play
            # this will fail if the outfielders get into a run down and tag someone out for a double play, but that seems super rare
            return False

        if this_play_outs == 0 and this_batter != next_batter and this_play_per_game not in hr_play_per_games and \
            this_batter in next_set_br and this_first_br not in next_set_br and this_first_br != 0 and \
                ((this_second_br in next_set_br and this_second_br != 0) or (this_third_br in next_set_br and this_third_br != 0)):
            # Outs must go up if there is a runner this isn't on the bases on the next play, and there are were runners ahead of them on this play
            # this is a fielders choice out at second
            return False

        if this_play_outs != 1 and set([br for br in this_set_br if br != 0 ]) == set([br for br in next_set_br if br != 0 ]) \
            and this_batter != next_batter:
            # It must be 1 out if there are non zero BRs that stay the same, and there is a new batter -- this is a strikeout
            # Assumption this goes wrong for mid at bat PH, but that might be rare -- ignore that
            return False

        if this_play_outs != 0 and this_set_batting_team == next_set_batting_team:
            # Outs can't go up is there is the same batter and baserunners
            return False

        if this_play_outs > (1 + half_inning_df.iloc[empty_cell_index]["n_br"]):
            # Outs can't go up by more than the number of baserunners + 1
            return False

        if this_play_outs != 0 \
            and next_set_br == this_set_batting_team:
            # Outs can't go up if the batter becomes the baserunner on the next play 
            # and the previous set of baserunners is still there
                return False

        if this_play_outs != 0 and len(this_set_batting_team) == 2 and same_batter_next_play:
            # Outs can't go up if there are no baserunners and the batter is the same in the next play
            # len(this_set_batting_team) == 2 is because the set will be batter_num and 0
            return False

        if ((seq_len - 1) == (empty_cell_index)) \
            and (does_this_make_3 != 3):
            # if we are on the last index, then this_play_outs and prev_outs must sum to three
            return False

        return True
 

    def _solve_outs_sequence(self, half_inning_df, seq):
        """
        A recursive function that solves an outs sequence
        
        """
        empty_cell_index = self._find_empty_cell(seq)

        if empty_cell_index is None:
            # you have found a valid solution and this is what makes your thing return
            return True

        # in a vacuum, each play can have 0, 1, 2, or 3 outs
        for this_play_outs in range(4):

            if self._is_valid_outs_assignment(half_inning_df, seq, this_play_outs, empty_cell_index):
                seq[empty_cell_index, 1] = this_play_outs
                
                # the next prev_play_outs is the sum of all previous this_play_outs
                temp_sum = 0 if empty_cell_index == 0 else sum(seq[empty_cell_index - 1, :])
                seq[empty_cell_index, 0] = temp_sum

                if self._solve_outs_sequence(half_inning_df, seq):
                    # you did it! you have a valid sequence of outs
                    return True

                seq[empty_cell_index, 0] = np.nan
                seq[empty_cell_index, 1] = np.nan

        return False

    
    def impute_outs(self, game_info_df, verbose = False):
        """
        The function that actually invokes the outs sequence solver
        
        
        """
        # TODO: consider making this a part of the game_info_table
        which_innings_are_valid = {}

        full_game = game_info_df.copy()
        
        # make an array to store all of these
        running_outs_seq = np.full((full_game.shape[0], 2), -99)
        running_index = 0
        
        # there could be a different amounts of innings in a game 
        num_innings = full_game["inning"].max()

        for inning in range(1, num_innings + 1):
            if verbose:
                print(inning)
            for which_half in ["Top", "Bottom"]:
                if verbose:
                    print(which_half)

                # the half inning is not valid until it is proven true
                which_innings_are_valid[str(inning) + "_" + which_half] = False

                
                this_half = full_game.loc[(full_game["inning"] == inning) & (full_game["top_bottom_inning"] == which_half), :]

                if this_half.shape[0] == 0:
                    if verbose:
                        print("no data for the {} of {}".format(which_half, inning))
                        
                    if inning == num_innings and which_half == "Bottom":
                        self.winner = self.home_team

                    running_index += outs_seq.shape[0]
                    continue

                outs_seq = this_half[["prev_outs", "this_play_outs"]].copy().values

                if verbose:
                    print(outs_seq.shape)

                self._solve_outs_sequence(this_half, outs_seq)

                try: 
                    assert sum(outs_seq[:, 1]) == 3

                except:
                    if verbose:
                        print("Assertion Error: for the {} of {}".format(which_half, inning))
                    
                    # You don't have to have 3 outs in the last half inning! It can be a walk off!!
                    if inning == num_innings and which_half == "Bottom":
                        self.winner = self.home_team

                # this won't work if there is literally one play?
                if np.isnan(outs_seq).all():
                    # this means something went wrong, fill -99 so it is obvious
                    outs_seq = np.full(outs_seq.shape, -99)

                # fill in this sequence into the array
                running_outs_seq[(running_index): (running_index + outs_seq.shape[0]), :] = outs_seq

                running_index += outs_seq.shape[0]
                which_innings_are_valid[str(inning) + "_" + which_half] = True

        # assign the array back to those cols in the df
        full_game.loc[:, ["prev_outs", "this_play_outs"]] = running_outs_seq

        return full_game, which_innings_are_valid

        
    def collect_all_timestamps(self, ball_df, player_df, game_events_df, cols = ["play_id", "timestamp"]):
        """
        A utility function for identifying all the timestamps across the different files
        for convenience when making a gif, etc
        
        
        can be used outside of the obejct too
        """

        timestamp_df = pd.concat([
            self.new_ball_pos[cols],
            self.new_player_pos[cols], 
            self.game_events_df[cols]
        ]).groupby("play_id").value_counts().reset_index() 

        timestamp_df = timestamp_df[cols].drop_duplicates().sort_values(cols)
        
        return timestamp_df
        
        
    def get_ppg_from_pid(self, play_id):
        """
        returns the play_per_game value from a play_id
        """
        
        return self.play_id_to_per_game_mapper.loc[self.play_id_to_per_game_mapper["play_id"] == play_id, "play_per_game"].values[0]
    
    
    def get_pid_from_ppg(self, play_per_game):
        """
        returns the play_id value from a play_per_game
        """
        
        return self.play_id_to_per_game_mapper.loc[self.play_id_to_per_game_mapper["play_per_game"] == play_per_game, "play_id"].values[0]
     
        
    def get_play_id_and_ppg_for_event(self, event, **kwargs):
        """
        takes in a game_events_df

        event is "home run", etc

        Examples:
        # all HR play_per_games
        self.get_play_id_and_ppg_for_event("home run")

        # all balls that are acquired by outfielders and end the play
        self.get_play_id_and_ppg_for_event("ball acquired", player_position=[7, 8, 9], next_event="end of play")
        """
        event_indices = self.game_events_df["event"] == event

        if len(kwargs) != 0:

            for k,v in kwargs.items():

                if type(v) is list:                
                    event_indices = (event_indices) & (self.game_events_df[k].isin(v))

                else:
                    event_indices = (event_indices) & (self.game_events_df[k] == v)

        return self.game_events_df.loc[event_indices, ["play_id", "play_per_game"]].drop_duplicates()
    
        
    def get_this_play_ts(self, play_id):
        """
        a util for returning a specific play's timestamps
        """
        
        return self.timestamp_df.loc[self.timestamp_df["play_id"] == play_id, "timestamp"].values

    
    def get_this_play(self, play_id, which):
        
        if which == "ball_pos":
            return self.new_ball_pos.loc[self.new_ball_pos["play_id"] == play_id, :]
        elif which == "player_pos":
            return self.new_player_pos.loc[self.new_player_pos["play_id"] == play_id, :]
        elif which == "game_info":
            
            # play per game, and play_id are different! 
            
            return self.game_info_df.loc[self.game_info_df["play_per_game"] == self.get_ppg_from_pid(play_id), :]
        
        elif which == "game_events":
            return self.game_events_df.loc[self.game_events_df["play_id"] == play_id, :]
        