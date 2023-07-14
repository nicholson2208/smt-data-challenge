# This file contains a class for plotting

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D 
import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib as mpl
import numpy as np 
import pandas as pd 

from src.game import Game

class Baseball_Field:
    # originally inspired by this!
    # https://www.kaggle.com/code/debojit23/baseball-field-structure-matplotlib
    def __init__(self, which_game, figsize=(12,12)):
        
        plt.ioff()
        self.figsize = figsize
        self.fig, self.ax = self.plot_2d_field()
        
        # a Game object takes all of the data for a given game
        # and does common data cleaning tasks
        self.game_obj = Game(which_game)
        
        
        # these are needed so you can clear some of the figure, but not all
        self.fielders_artist = None
        self.fielders_velo_artist = None
        
        self.batters_artist = None
        self.batters_velo_artist = None
        
        self.ball_artist = None
        # TODO: Maybe add a ball velo?
        
        # this will be a list and I am going to map/reduce the remove I think
        self.event_annotation_artist = []
        
        
        self.last_plot_event = None
        self.last_player_pos = None
        
        
        self.this_ts_fielders = None
        self.this_ts_batters = None
        self.this_ts_ball = None
        
        

    def plot_2d_field(self):
        
        fig, ax = plt.subplots(1, figsize=self.figsize)

        
        dirt_color = "#D89E79"
        grass_color = "#247309"

        # light green for the whole field
        ax.add_patch(patches.Rectangle((-40, -40), 425, 425,
                                       facecolor=grass_color,
                                       alpha=0.75,
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        # inside infield dirt
        ax.add_patch(patches.Rectangle((-3, -3), 90, 90,
                                       facecolor=dirt_color,
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        # outer infield dirt wedge
        ax.add_patch(patches.Wedge((0, 60.5),
                                   95,
                                   # this is th angle where it crosses the foul line,
                                   # which is 3 ft right of the line
                                   18.51, 
                                   180 - 18.51,
                                   facecolor=dirt_color
                                      ))

        # fill in the corner gaps
        ax.add_patch(patches.Rectangle((85, -3), 127.2 - 85, 30,
                                       facecolor=dirt_color,
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.add_patch(patches.Rectangle((-85, -3), - 127.2 + 85, 30,
                                       facecolor=dirt_color,
                                       angle=-45,
                                       rotation_point = (0, 0)
                                      ))


        # infield grass
        ax.add_patch(patches.Rectangle((3, 3), 84, 84,
                                       facecolor=grass_color,
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        # pitchers mound
        ax.add_patch(patches.Circle((0, 60.5), 18,
                                       facecolor=dirt_color
                                      ))

        # home plate area
        ax.add_patch(patches.Circle((0, 0), 13,
                                       facecolor=dirt_color
                                      ))

        # foul lines
        ax.add_patch(patches.Rectangle((0, 0), 1, 300,
                                       facecolor="white",
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.add_patch(patches.Rectangle((0, 0), 300, 1,
                                       facecolor="white",
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.add_patch(patches.Rectangle((90, 0), 3, 3,
                                       facecolor="white",
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.add_patch(patches.Rectangle((90, 90), 3, 3,
                                       facecolor="white",
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.add_patch(patches.Rectangle((0, 90), 3, 3,
                                       facecolor="white",
                                       angle=45,
                                       rotation_point = (0, 0)
                                      ))

        ax.axvline(0, color='b', alpha = 0.3)
        ax.axhline(0, color='b', alpha = 0.3)

        ax.grid()

        ax.set_xlim(-200, 200)
        ax.set_ylim(-40, 440)
        
        # plt.show()
        return fig, ax
    
    def clear_plot(self):
        """
        a convenience function to clear a plot, so you can reuse the same objects
        """
        self.remove_fielders_from_plot()
        self.remove_batters_from_plot()
        self.remove_ball_from_plot()
        self.remove_event_annotations_from_plot()
    
    def plot_all_components(self, play_id=None, frame_index=None,
                            timestamp=None, show_velos=False, show_trails=False):
        
        
        """
        if self.this_ts_fielders is None or self.this_ts_fielders.shape[0] != 0:
            self.this_ts_fielders = this_ts_fielders.copy()
        
        if this_ts_event.shape[0] != 0:
            self.last_plot_event = this_ts_event["event"].values[0]
            self.last_player_pos = this_ts_event['player_position'].values[0]
        
        
        if self.last_plot_event == "ball acquired":
            # this means the ball is in the fielders hand I think
            
            print("ball should be in glove here of player " + str(self.last_player_pos))
            
            this_ts_ball.loc[:, "ball_position_x"] = self.this_ts_fielders.loc[self.this_ts_fielders["player_position"] == self.last_player_pos, "field_x"].values
            this_ts_ball.loc[:, "ball_position_y"] = self.this_ts_fielders.loc[self.this_ts_fielders["player_position"] == self.last_player_pos, "field_y"].values
            this_ts_ball["ball_position_z"] = 0
        
        """
        
        self.add_fielders_to_plot(play_id=play_id, timestamp=timestamp, frame_index=frame_index, show_velos=show_velos)
        self.add_batters_to_plot(play_id=play_id, timestamp=timestamp, frame_index=frame_index, show_velos=show_velos)
        self.add_ball_to_plot(play_id=play_id, timestamp=timestamp, frame_index=frame_index, show_velos=show_velos)
        self.add_event_annotations(play_id=play_id, timestamp=timestamp, frame_index=frame_index)

    
    # @staticmethod
    def _gif_writer(self, i, play_id):
        
        self.clear_plot()
        self.plot_all_components(play_id=play_id, frame_index=i)
        
        return self.fig 
        
        
    def create_gif(self, play_id, file_path="image_outputs/", tag=""):
        
        # Need to gather all of the timestamps (in a way that is robust to smoothing/snapping)
        # create a function? I think this should be plot_all_components
        
        frames = self.game_obj.get_this_play_ts(play_id)

        
        ani = FuncAnimation(self.fig, self._gif_writer, fargs=(play_id,), frames=len(frames),
                    interval=50, repeat=True, repeat_delay = 1500)
            
        file_name = file_path + self.game_obj.which_game + "_play" + str(play_id) + tag + ".gif"
        
        ani.save(file_name, dpi=100)
        
        

    def remove_fielders_from_plot(self):
        
        if self.fielders_artist:
            self.fielders_artist.remove()
            self.fielders_artist = None
            
        if self.fielders_velo_artist:
            self.fielders_velo_artist.remove()
            self.fielders_velo_artist = None
               
    def add_fielders_to_plot(self, play_id=None, frame_index=None, timestamp=None, this_ts_fielders=None, show_velos=False, show_trails=False, color="yellow"):
        """
        Adds the fields to this objects ax
        
        Params:
            play_id (int):
            
            
        Returns:
            None
            
        Modifies:
            self.fielders_artist
        
        """
        
        if not (timestamp or play_id or this_ts_fielders):
            raise TypeError("Must provide at least one of play_id, timestamp or this_ts_fielders")
            
        if timestamp and type(frame_index) == int:
            raise TypeError("Cannot use both timestamp and frame_index")
        
        if play_id and (type(frame_index) != int) and (not timestamp):
            # this means to plot the whole play
            # this will ignore show_vectors and show_trails
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 9), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            # make the size smaller if plotting all
            self.fielders_artist = self.ax.scatter(this_play_pos_data["field_x"], this_play_pos_data["field_y"], color=color, marker='o', s=30)
            return
        elif timestamp:
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 9), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            this_ts_fielders = this_play_pos_data.loc[this_play_pos_data["timestamp"] == timestamp]
            
        elif type(frame_index) == int:
            frames = self.game_obj.get_this_play_ts(play_id)
            
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 9), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            this_ts_fielders = this_play_pos_data.loc[this_play_pos_data["timestamp"] == frames[frame_index]]

            
        # if there is nothing in this timestamp, just quit and leave it
        if this_ts_fielders.shape[0] == 0:    
            return
        
        elif this_ts_fielders.shape[0] < 9:
            print("missing fielders data at timestamp")
            print(str(this_ts_fielders.loc[:, ["timestamp", "player_position"]]))
        
        
        # this part might yell at me! 
        if self.fielders_artist is not None and show_trails == False:
            self.fielders_artist.remove()
        
        self.fielders_artist = self.ax.scatter(this_ts_fielders["field_x"], this_ts_fielders["field_y"], color=color, marker='o', s=80)
        
        if show_velos:
            if self.fielders_velo_artist is not None:
            
                self.fielders_velo_artist.remove()
                self.fielders_velo_artist = None
                
            velo_scale_factor = 0.2
            
            self.fielders_velo_artist = self.ax.quiver(this_ts_fielders["field_x"], 
                                                       this_ts_fielders["field_y"], 
                                                       velo_scale_factor * this_ts_fielders["velo_x"], 
                                                       velo_scale_factor * this_ts_fielders["velo_y"],
                                                       color=color,
                                                       angles="xy"
                                                      )
            
        
    def remove_batters_from_plot(self):
        
        if self.batters_artist:
            self.batters_artist.remove()
            self.batters_artist = None
    
        if self.batters_velo_artist:
            self.batters_velo_artist.remove()
            self.batters_velo_artist = None
    
    def add_batters_to_plot(self, play_id=None, frame_index=None, timestamp=None, this_ts_batters=None, show_velos=False, show_trails=False, color="black"):
        
        if not (timestamp or play_id or this_ts_batters):
            raise TypeError("Must provide at least one of play_id, timestamp or this_ts_batters")
                    
        if timestamp and type(frame_index) == int:
            raise TypeError("Cannot use both timestamp and frame_index")
        
        if play_id and (type(frame_index) != int) and (not timestamp):
            # this means to plot the whole play
            # this will ignore show_vectors and show_trails
            
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] >= 10) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 13), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            # make the size smaller if plotting all
            self.batters_artist = self.ax.scatter(this_play_pos_data["field_x"], this_play_pos_data["field_y"], color=color, marker='o', s=30)
            return
        elif timestamp:
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] >= 10) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 13), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            this_ts_batters = this_play_pos_data.loc[this_play_pos_data["timestamp"] == timestamp]
            
        elif type(frame_index) == int:
            frames = self.game_obj.get_this_play_ts(play_id)

            
            this_play_pos_data = self.game_obj.new_player_pos.loc[(self.game_obj.new_player_pos["play_id"] == play_id) &\
                                                                  (self.game_obj.new_player_pos["player_position"] >= 10) &\
                                                                  (self.game_obj.new_player_pos["player_position"] <= 13), ["timestamp", "player_position", "field_x", "field_y", "velo_x", "velo_y"]].copy()
            
            this_ts_batters = this_play_pos_data.loc[this_play_pos_data["timestamp"] == frames[frame_index]]
        
        
        # if there is nothing in this timestamp, just quit and leave it
        if this_ts_batters.shape[0] == 0:
            
            return
        #elif this_ts_batters.shape[0] < 9:
        #    print("missing batters data at timestamp")
        #    print(str(this_ts_batters.loc[:, ["timestamp", "player_position"]]))
        
        if self.batters_artist is not None and show_trails == False:
            self.batters_artist.remove()
        
        self.batters_artist = self.ax.scatter(this_ts_batters["field_x"], this_ts_batters["field_y"], color=color, marker='o', s=80)
        
        if show_velos:
            if self.batters_velo_artist is not None:
            
                self.batters_velo_artist.remove()
                self.batters_velo_artist = None
                
            velo_scale_factor = 0.2
            
            self.batters_velo_artist = self.ax.quiver(this_ts_batters["field_x"], 
                                                      this_ts_batters["field_y"], 
                                                      velo_scale_factor * this_ts_batters["velo_x"], 
                                                      velo_scale_factor * this_ts_batters["velo_y"],
                                                      color=color,
                                                      angles="xy"
                                                     )
            
        
    def remove_ball_from_plot(self):
        
        if self.ball_artist:
            self.ball_artist.remove()
            self.ball_artist = None

    
    def add_ball_to_plot(self, play_id=None, frame_index=None, timestamp=None, this_ts_ball_pos=None, show_velos=False, show_trails=False, color="white"):
        
        if not (timestamp or play_id or this_ts_ball_pos):
            raise TypeError("Must provide at least one of play_id, timestamp or this_ts_ball_pos")
        
        if timestamp and type(frame_index) == int:
            raise TypeError("Cannot use both timestamp and frame_index")
        
        if play_id and (type(frame_index) != int) and (not timestamp):
            # this means to plot the whole play
            # this will ignore show_vectors and show_trails
            
            
            this_play_ball_data = self.game_obj.new_ball_pos.loc[(self.game_obj.new_ball_pos["play_id"] == play_id),
                                                                 ["timestamp", "ball_position_x", "ball_position_y",
                                                                  "ball_position_z", "ball_velo_x", "ball_velo_y", "ball_velo_z",]].copy()
            
            z_coords = this_play_ball_data["ball_position_z"].values
            ball_scale_factor = 2
            
            self.ball_artist = self.ax.scatter(this_play_ball_data["ball_position_x"],
                                               this_play_ball_data["ball_position_y"], 
                                               color=color,
                                               marker='o',
                                               s=10
                                               # TODO: make this vary
                                               #s=z_coord ** 2 * ball_scale_factor if z_coords > 5 else 5 ** 2 * ball_scale_factor
                                              )
            return
        elif timestamp:
            this_play_ball_data = self.game_obj.new_ball_pos.loc[(self.game_obj.new_ball_pos["play_id"] == play_id),
                                                                 ["timestamp", "ball_position_x", "ball_position_y",
                                                                  "ball_position_z", "ball_velo_x", "ball_velo_y", "ball_velo_z",]].copy()
            
            this_ts_ball_pos = this_play_ball_data.loc[this_play_ball_data["timestamp"] == timestamp]
            
        elif type(frame_index) == int:
            frames = self.game_obj.get_this_play_ts(play_id)
                        
            this_play_ball_data = self.game_obj.new_ball_pos.loc[(self.game_obj.new_ball_pos["play_id"] == play_id),
                                                                 ["timestamp", "ball_position_x", "ball_position_y",
                                                                  "ball_position_z", "ball_velo_x", "ball_velo_y", "ball_velo_z",]].copy()
            
            this_ts_ball_pos = this_play_ball_data.loc[this_play_ball_data["timestamp"] == frames[frame_index]]
        
        
        # if there is nothing in this timestamp, just quit and leave it
        if this_ts_ball_pos.shape[0] == 0:
            return
        
        if self.ball_artist is not None and show_trails == False:
            self.ball_artist.remove()
            
        # this should just be one value
        z_coord = this_ts_ball_pos["ball_position_z"].values[0]
        ball_scale_factor = 1
        
        self.ball_artist = self.ax.scatter(this_ts_ball_pos["ball_position_x"].values[0], 
                                           this_ts_ball_pos["ball_position_y"].values[0],
                                           color=color,
                                           marker='o', 
                                           s=z_coord ** 2 * ball_scale_factor if z_coord > 5 else 5 ** 2 * ball_scale_factor)
        

    def remove_event_annotations_from_plot(self):
        
        if len(self.event_annotation_artist):
            
            for artist in self.event_annotation_artist:
                artist.remove()
            
            
            self.event_annotation_artist = []

        
    def add_event_annotations(self, x= -190, y=425, play_id=None, frame_index=None, timestamp=None, this_ts_event=None):
        
        if not (timestamp or play_id or this_ts_event):
            raise TypeError("Must provide at least one of play_id, timestamp or this_ts_event")
                
        if timestamp and type(frame_index) == int:
            raise TypeError("Cannot use both timestamp and frame_index")
            
        if play_id and (type(frame_index) != int) and (not timestamp):
            # this means to plot the whole play
            
            
            this_play_events = self.game_obj.game_events_df.loc[(self.game_obj.game_events_df["play_id"] == play_id),
                                                               :].copy()
            
            event_descs = this_play_events.apply(lambda row: str(row["timestamp"]) + ": " + str(row["event"]) + " by " + str(row["player_position"]), axis = 1).values
            
            
            y_text_spacing = 12
            for ii, event in enumerate(event_descs):
                self.event_annotation_artist.append(self.ax.annotate(event, (x, y - (ii*y_text_spacing))))
            
            return
            
            
        elif timestamp:
            this_play_events = self.game_obj.game_events_df.loc[(self.game_obj.game_events_df["play_id"] == play_id),
                                                               :].copy()
            
            this_ts_event = this_play_events.loc[this_play_events["timestamp"] == timestamp]
            
        elif type(frame_index) == int:
            frames = self.game_obj.get_this_play_ts(play_id)
            
            this_play_events = self.game_obj.game_events_df.loc[(self.game_obj.game_events_df["play_id"] == play_id),
                                                               :].copy()
            
            this_ts_event = this_play_events.loc[this_play_events["timestamp"] == frames[frame_index]]


        
        # if there is nothing in this timestamp, just quit
        if this_ts_event.shape[0] == 0:
            return
        
        if len(self.event_annotation_artist):
            for artist in self.event_annotation_artist:
                artist.remove()
        
        text =  str(this_ts_event["timestamp"].values[0]) + ": "
        text += str(this_ts_event["event"].values[0]) + " by " + str(this_ts_event["player_position"].values[0]) 
        
        self.event_annotation_artist = [self.ax.annotate(text, (100, 10))]
