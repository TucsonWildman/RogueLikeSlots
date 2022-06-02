# RogueLikeSlots
A Python Script you can use to pseudorandomly select options for your next RogueLike playthrough based on your high score and playthrough history.

# Historical Data
This is loaded prior to [Main](#-main).
Exists as a Pandas Serial with a MultiIndex to
identify the game mode.
- Unplayed modes have a score of 0.
- Prohibited modes have a score of -1.


# Functions
## GetRaffleWeights
### Input: raffleItems
A dictionary with strings as keys and numbers as values
### Output:
Each key of raffleItems is assigned a probability calculated as follows:

$$P_i = \dfrac{N_i}{\sum_{} N_i}$$

... where

$$N_i = \prod_{j \neq i} n_j - 1$$

Where $n_j$ is raffleItems[j].

## BiasedEliminationRaffle
Also referred to as "Biased Elimination Raffle"
### Input: raffleItems
A dictionary with strings as keys and numbers as values
### Output:
A pseudorandomly selected key from raffleItems probability
of each set by GetRaffleWeights

## GetAllPossibleModes
### Input: historical_data, challenge, difficulty, playerclass
### Output:
All possible game modes based on current data, including those unplayed.
Filtered by non-blank arguments

## GenFilter
### Input: historical_data, challenge, difficulty, playerclass, invert
### Output: loc_idx
An array of row labels used to select rows within the historical_data.
Additional filtering by non-blank arguments.
If invert, exclude matching rows.

# Main
## Parameters
### Base
These are the 'sub-modes'
- Challenge
- Difficulty
- Class
### Options
#### \[None\]
If no arguments are specified the script will randomly select
a new gameplay mode per the following process:
```
After excluding all prohibited modes, are there any unplayed game modes?
|-  [Yes]: Is there more than one game mode?
    |-  [Yes]:  Select game mode with Biased Elimination Raffle on each
        sub-mode
    |-  [No]:   The one unplayed game mode is selected
|-  [No]: Choose from all played game modes with the Biased Elimination
    Raffle
```
Additional filtering is applied when a sub-mode is specified.
If it is a new sub-mode, it will be saved to the historical
data.
#### Add High Score
Add the high score for a (fully specified) game mode
#### Add Prohibited Combo
Specify (at least) 2 sub-modes of an invalid game mode
#### Remove High Score
Remove the high score for a (fully specified) game mode.
It will be set to zero marking it as unplayed.
#### Remove Sub-Mode
Remove a sub-mode.  CAUTION: This will delete data of all related modes!
#### Remove Prohibited Combo
Mark a combination of (at least) 2 sub-modes as valid.
All related game modes will be marked as unplayed.
#### Show Data
Show a Markdown-formatted table of High Scores and
Times Played of all game modes.
## Process
1. Load up the historical data.  If it's not there, initialize it.
   This is done before "Main".
1. Process the arguments from the user and act accordingly.
1. Save the data for a later run.

# Compatibility
Written for Anaconda Python 3.9 with Pandas 1.3.4
