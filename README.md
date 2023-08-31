# Vacuums and Stone Hands: An Exploration of First Baseman Receiving

## Abstract

In an era where the game is increasingly quantified, the receiving aspect of first baseman defense has been largely ignored. While particularly skilled (or lacking) play contributes to a fielder’s reputation, even advanced defensive metrics fail to explicitly consider the role of the first baseman in the assist. In this analysis, I describe what makes an out at first from the perspective of the first baseman. I find that bounced and offline throws are less likely to be outs, and that some players seem to be better at fielding these than others, lending credence to the conventional wisdom that some possess this skill. While the data are insufficient to compute full player-level first baseman receiving rankings, I demonstrate a viable framework for its evaluation. Finally, I discuss the role that first baseman receiving can take in player development and valuation, and suggest future extensions of this approach.


## An Overview of this Repo

### Foundational Files
The files that power all analysis are:
- `src/game.py`, contains a class for a Game. Game does all of the preprocessing and imputation 
- `src/plotting.py`, contains a class for a Baseball_Field. This does all of the plotting and gif making.
- `src/utils.py`, contains a assorted functions used in both classes and throughout the analysis.

### Analysis Files

#### Final
- [Final Analysis Pipeline](AnalysisPipeline.ipynb)
    - Contains figures included in the final paper

#### Explorations

- [Game Info and Player Pos Disagreements](GameInfo_PlayerPos_Disagreement.ipynb)
    - A look into how wide player pos and game info disagreements are

- [Timestamp Alignment](PlotDebugging.ipynb)
    - An attempt to realign plot timestamps
 
- [Retagging Outs Manually](Retagging.ipynb)
    - An attempt to manually identify why outs get mislabeled


#### Outputs
- [CSV outputs of this analysis](full_computed_dataset.csv)
- [Produced Gifs of Plays](image_outputs/)

### Media From Paper

#### Aligning Ball and Player Data

a. ![A misaligned play](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/dp_misaligned_ts.mp4)
- A misaligned play (Play ID 124, from Game 1903_01_TeamNE_TeamA2), notice the second basemen is not near the ball or bag when the turn is made. 

b. ![A realigned play](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/dp_realigned_ts.mp4)
- The same play with the ball and player timestamps aligned as described in the section 3.1 of the paper

#### Example Scenarios

a. ![A likely out that was converted for an out](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/should_have_been_and_was.mp4)
- A likely out that was converted for out. These plays are considered routine. (Play ID 150, from Game 1902_26_TeamMH_TeamA3) 

b. ![A unlikely out that was not converted for an out](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/no_shot_at_out.mp4)
- An unlikely out that was not converted for an out. These plays are long shots. (Play ID 132, from Game 1903_32_TeamNB_TeamA1) 

c. ![A unlikely out that was converted for an out](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/good_scoop_good_play.mp4)
- An unlikely out that was converted for an out. This is a great play by the first baseman. (Play ID 106, from Game 1903_30_TeamNF_TeamA2) 

d. ![A likely out that was not converted for an out](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/should_have_been_out_bad_play.mp4)
- A likely out that was not converted. (Play ID 193, from Game 1903_05_TeamND_TeamA2) These plays are hard to interpret without additional context. It could be a blunder on the first basemen, or a throw bad enough that preventing the throw from getting away is more important than the out.


#### Preventing a bad play from getting worse

a. ![](https://github.com/nicholson2208/smt-data-challenge/blob/main/media_for_paper/AlonsoSnagSavesError.png)
- [Mets first baseman Pete Alonso saves an error on a throw well off the bag](https://www.mlb.com/video/joey-lucchesi-in-play-no-out-to-masyn-winn)

b. ![A bad throw pulls a player off the bag](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/sample.mp4)
- A similarly bad throw pulls the first baseman off the bag in Play ID 25 of Game 1902_05_TeamML_TeamB. While there is value in stopping a bad play from getting worse, the data anonymization hampered my ability to explore that in this analysis.


