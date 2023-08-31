# Vacuums and Stone Hands: An Exploration of First Baseman Receiving

## Abstract

In an era where the game is increasingly quantified, the receiving aspect of first baseman defense has been largely ignored. While particularly skilled (or lacking) play contributes to a fielder’s reputation, even advanced defensive metrics fail to explicitly consider the role of the first baseman in the assist. In this analysis, I describe what makes an out at first from the perspective of the first baseman. I find that bounced and offline throws are less likely to be outs, and that some players seem to be better at fielding these than others, lending credence to the conventional wisdom that some possess this skill. While the data are insufficient to compute full player-level first baseman receiving rankings, I demonstrate a viable framework for its evaluation. Finally, I discuss the role that first baseman receiving can take in player development and valuation, and suggest future extensions of this approach.


## An Overview of this Repo

### Foundational
The files that power all analysis are:
- `src/game.py`, contains a class for a Game. Game does all of the preprocessing and imputation 
- `src/plotting.py`, contains a class for a Baseball_Field. This does all of the plotting and gif making.
- `src/utils.py`, contains a assorted functions used in both classes and throughout the analysis.

### Analysis


- outputs

### Media From Paper

#### Aligning Ball and Player Data

![A misalighed play](media_for_paper/dp_misaligned_ts.mp4)

[![A realighed play](media_for_paper/dp_realigned_ts.mp4)](https://raw.githubusercontent.com/nicholson2208/smt-data-challenge/main/media_for_paper/dp_misaligned_ts.mp4)

The above show a misaligned play (Play ID 124, from Game 1903_01_TeamNE_TeamA2), notice the second basemen is not near the ball or bag when the turn is made. The second video shows the same play with the ball and player timestamps aligned as described in the section 3.1 of the paper


