import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
from mpl_toolkits.mplot3d import Axes3D 
import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib as mpl
import numpy as np 
import pandas as pd 


class Baseball_Field:
    # originally inspired by this!
    # https://www.kaggle.com/code/debojit23/baseball-field-structure-matplotlib
    def __init__(self, figsize):
        
        plt.ioff()
        self.figsize = figsize
        self.fig, self.ax = self.plot_2d_field()
        
        # these are needed so you can clear some of the figure, but not all
        self.fielders_artist = None
        self.ball_artist = None
        self.event_annotation_artist = None
        

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

        ax.axvline(0, color='b')
        ax.axhline(0, color='b')

        ax.grid()

        ax.set_xlim(-200, 200)
        ax.set_ylim(-40, 440)
        
        # plt.show()
        return fig, ax
    
    
    def add_fielders_to_plot(self, this_ts_fielders, show_trails = False):
        
        # if there is nothing in this timestamp, just quit and leave it
        if this_ts_fielders.shape[0] == 0:
            
            return
        elif this_ts_fielders.shape[0] < 9:
            print("missing fielders data at timestamp")
            print(str(this_ts_fielders.loc[:, ["timestamp", "player_position"]]))
        
        if self.fielders_artist is not None and show_trails == False:
            self.fielders_artist.remove()
        
        self.fielders_artist = self.ax.scatter(this_ts_fielders["field_x"], this_ts_fielders["field_y"], color='yellow', marker='o', s=80)
        
        
        
    def add_ball_to_plot(self, this_ts_ball_pos, show_trails = False):
        
        # if there is nothing in this timestamp, just quit and leave it
        if this_ts_ball_pos.shape[0] == 0:
            return
        
        if self.ball_artist is not None and show_trails == False:
            self.ball_artist.remove()
            
        # this should just be one value
        z_coord = this_ts_ball_pos["ball_position_z"].values[0]
        
        self.ball_artist = self.ax.scatter(this_ts_ball_pos["ball_position_x"].values[0], this_ts_ball_pos["ball_position_y"].values[0], color='white', marker='o', s=z_coord ** 2 * 2 if z_coord > 5 else 50)
        
        
    def add_event_annotations(self, this_ts_event, xy = (100, 10)):
        
        # if there is nothing in this timestamp, just quit
        if this_ts_event.shape[0] == 0:
            return
        
        if self.event_annotation_artist is not None:
            self.event_annotation_artist.remove()
        
        text =  str(this_ts_event["timestamp"].values[0]) + ": "
        text += str(this_ts_event["event"].values[0]) + " " + "by " + str(this_ts_event["player_position"].values[0]) 
        
        self.event_annotation_artist = self.ax.annotate(text, xy)
