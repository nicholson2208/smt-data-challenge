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


def concat_game_events_into_single_file(write=False, path="data/"):
    
    
    all_game_events = pd.DataFrame()

    root_dirs = ['data/game_events/'] 


    for root_dir in root_dirs:
        for sub_dir, dirs, files in os.walk(root_dir):
            for file in files:
                if "checkpoint" in file:
                    continue

                temp_game_events_df = pd.read_csv(os.path.join(sub_dir, file), index_col=0)

                temp_game_events_df["last_event_code"] = temp_game_events_df["event_code"].shift(1)
                temp_game_events_df["last_player_position"] = temp_game_events_df["player_position"].shift(1)

                temp_game_events_df["event"] = temp_game_events_df["event_code"].map(lambda x: EVENT_CODE_TO_DESC[x])
                temp_game_events_df["last_event"] = temp_game_events_df["last_event_code"].map(lambda x: EVENT_CODE_TO_DESC[x] if pd.notnull(x) else x)


                # take just the first part
                temp_game_events_df["game"] = file.split(".csv")[0]


                all_game_events = pd.concat([all_game_events, temp_game_events_df])
                
    # add some of these fields I want            
    all_game_events["away"] = all_game_events["game"].str.split("_Team").apply(lambda x: x[1])
    all_game_events["home"] = all_game_events["game"].str.split("_Team").apply(lambda x: x[-1])

    all_game_events["year"] = all_game_events["game"].str.strip("game_events-").str.split("_").apply(lambda x: x[0])
    all_game_events["game_num"] = all_game_events["game"].str.strip("game_events-").str.split("_").apply(lambda x: x[1])
                
    if write:
        all_game_events.to_csv(path+"all_game_events.csv")
    
    return all_game_events     


