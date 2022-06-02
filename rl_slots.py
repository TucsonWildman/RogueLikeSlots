# **ROGUELIKE SLOTS**
import argparse
import pandas as pd
import re

from math     import ceil
from os.path  import isfile
from random   import choices

INDEX_LEVELS = ['Challenge', 'Difficulty', 'Class']
COLUMNS      = ['High Score', 'Times Played']

#  Historical Data
HISTORICAL_DATA_NAME = 'hist.pkl'
if isfile(HISTORICAL_DATA_NAME): historical_data = pd.read_pickle(HISTORICAL_DATA_NAME)
else:                            historical_data = pd.DataFrame([], pd.MultiIndex.from_arrays([[''],[''],['']], names=tuple(INDEX_LEVELS) ), COLUMNS)

# Functions
## GetRaffleWeights
_GetRaffleWeights_hash  = None
_GetRaffleWeights_stash = None
def GetRaffleWeights(raffleItems):
    global _GetRaffleWeights_hash, _GetRaffleWeights_stash
    str2hash = ''
    for rItem in raffleItems.items(): str2hash += f' {rItem[0]}:{rItem[1]} '
    new_hash = hash(str2hash)
    if new_hash == _GetRaffleWeights_hash: return _GetRaffleWeights_stash
    _GetRaffleWeights_hash = new_hash

    raffleWeights = dict()
    if min(raffleItems.values() ) > 1:
        for item in raffleItems.items():
            raffleWeights[item[0] ] = 0
            for val in raffleItems.values(): raffleWeights[item[0] ] += (ceil(item[1]) - 1)/(ceil(val) - 1)
            raffleWeights[item[0] ] = 1/raffleWeights[item[0] ]
        #End-for
    else:
        for item in raffleItems.items():
            raffleWeights[item[0] ] = 0
            if item[1] == 0: raffleWeights[item[0] ] = 1
        #End-for
    #End-if

    _GetRaffleWeights_stash = raffleWeights
    return _GetRaffleWeights_stash
#End-def

## BiasedEliminationRaffle
def BiasedEliminationRaffle(raffleItems):
    raffleWeights = GetRaffleWeights(raffleItems)
    return choices(list(raffleWeights.keys() ), list(raffleWeights.values() ) )
#End-def

## GetAllPossibleModes
_AllCombos = []
def GetAllPossibleModes(challenge='', difficulty='', playerclass=''):
    global _AllCombos
    if len(_AllCombos) == 0:
        for _challenge in historical_data.index.get_level_values('Challenge'):
            for _difficulty in historical_data.index.get_level_values('Difficulty'):
                for _playerclass in historical_data.index.get_level_values('Class'):
                    _AllCombos += [(_challenge, _difficulty, _playerclass)]
                #End-for
            #End-for
        #End-for
    #End-if
    retList = set()
    argTup  = (challenge, difficulty, playerclass)
    for l_item in _AllCombos:
        reject = False
        lvl    = 0
        while (lvl < 3) and (not reject):
            reject |= (len(argTup[lvl]) > 0) and (l_item[lvl] != argTup[lvl])
            lvl += 1
        #End-while
        if not reject: retList.add(l_item)
    #End-for
    return retList
#End-def

## GenFilter
def GenFilter(challenge='', difficulty='', playerclass='', invert=False):
    lvl_res = []
    for lvl in [challenge, difficulty, playerclass]: 
        if lvl == '': lvl_res += [re.compile('.+')]
        else:         lvl_res += [re.compile(f'^{lvl}$')]
    #End-for

    loc_idx = set(GetAllPossibleModes(challenge, difficulty, playerclass) )
    hist_rows = set(historical_data.index.to_flat_index().to_list() )
    if invert: return hist_rows - loc_idx
    return loc_idx & hist_rows
#End-def

# Main
### Options
#### \[None\]
mode_args_doc='''
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
'''
#### Add High Score
add_high_score_doc='''
Add the high score for a (fully specified) game mode
'''
#### Add Prohibited Combo
add_prohibited_combo_doc='''
Specify (at least) 2 sub-modes of an invalid game mode
'''
#### Remove High Score
rm_high_score_doc='''
Remove the high score for a (fully specified) game mode.
It will be set to zero marking it as unplayed.
'''
#### Remove Sub-Mode
rm_sub_mode_doc='''
Remove a sub-mode.  CAUTION: This will delete data of all related modes!
'''
#### Remove Prohibited Combo
rm_prohibited_combo_doc='''
Mark a combination of (at least) 2 sub-modes as valid.
All related game modes will be marked as unplayed.
'''
#### Show Data
show_data_doc='''
Show a Markdown-formatted table of High Scores and
Times Played of all game modes.
'''
## Process
if __name__ == '__main__':
    parser      = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    action_args = parser.add_mutually_exclusive_group()
    action_args.add_argument('--add-high-score',type=int,dest='new_high_score',help=add_high_score_doc)
    action_args.add_argument('--add-prohibited-combo',action='store_true',dest='prohibited_combo',help=add_prohibited_combo_doc)
    action_args.add_argument('--rm-high-score',action='store_true',dest='rm_high_score',help=rm_high_score_doc)
    action_args.add_argument('--rm-sub-mode',action='store_true',dest='rm_sub_mode',help=rm_sub_mode_doc)
    action_args.add_argument('--rm-prohibited-combo',action='store_true',dest='rm_prohibited_combo',help=rm_prohibited_combo_doc)
    action_args.add_argument('--show-data',action='store_true',dest='show_data',help=show_data_doc)
    mode_args = parser.add_argument_group('submode',description=mode_args_doc)
    mode_args.add_argument('--challenge',type=str,default='')
    mode_args.add_argument('--difficulty',type=str,default='')
    mode_args.add_argument('--playerclass',type=str,default='')
    results = parser.parse_args()
    row_tup = (results.challenge,results.difficulty,results.playerclass)
    num_modes_specd = 3 - row_tup.count('')
    if results.new_high_score and (num_modes_specd == 3):
        hist_row = {'High Score' : results.new_high_score, 'Times Played' : 1}
        if historical_data.index.isin([row_tup]).any(): hist_row = {'High Score' : max(results.new_high_score, historical_data.loc[row_tup, 'High Score'] ), 'Times Played' : historical_data.loc[row_tup, 'Times Played'] + 1}
        historical_data.loc[row_tup] = hist_row
    elif (results.prohibited_combo | results.rm_prohibited_combo) and (num_modes_specd >= 2):
        hist_row = {'High Score' : -1, 'Times Played' : 0}
        if results.rm_prohibited_combo: hist_row['High Score'] = 0
        if '' not in row_tup: historical_data.loc[row_tup] = hist_row
        else:
            for new_row in GetAllPossibleModes(*row_tup):
                historical_data.loc[new_row] = hist_row
            #End-for
        #End-if
    elif results.rm_high_score and (num_modes_specd == 3): historical_data.loc[row_tup] = {'High Score' : 0, 'Times Played' : 0}
    elif results.rm_sub_mode and (num_modes_specd == 1): historical_data = historical_data.loc[GenFilter(*row_tup, True)]
    elif results.show_data:
        data2print = historical_data.loc[GenFilter(*row_tup)]
        print(data2print.loc[data2print['High Score'] > 0])
    else:
        loc_idx  = GetAllPossibleModes(*row_tup)
        raw_dict = historical_data.to_dict()
        times_played      = dict()
        high_score        = dict()
        hs_partial        = dict()
        partial_keys      = set()
        for r_idx in loc_idx:
            flat_key = f'Challenge: {r_idx[0]}, Difficulty: {r_idx[1]}, Class: {r_idx[2]}'
            currHighScore = raw_dict['High Score'  ].get(r_idx, 0)
            if currHighScore < 0: continue
            high_score[flat_key] = currHighScore
            times_played[flat_key] = raw_dict['Times Played'].get(r_idx, 0)
            for pk in flat_key.split(','): hs_partial[pk] = max(hs_partial.get(pk,0), high_score[flat_key])
        #End-for

        run_filter = True
        while run_filter:
            run_filter      = False
            total_playthrus = max(sum(times_played.values() ), 1)
            weights         = GetRaffleWeights(high_score)
            for k in weights.keys():
                if times_played[k]/total_playthrus > weights[k]:
                    run_filter = True
                    del high_score[k]
                    del times_played[k]
                #End-if
            #End-for
        #End-while
        if not any(times_played.values() ):
            for k in times_played.keys():
                for p in k.split(','): high_score[k] += hs_partial[p]/3
            #End-for
        #End-if
        print(BiasedEliminationRaffle(high_score)[0])
    #End-if
    historical_data.to_pickle(HISTORICAL_DATA_NAME)
#End-if
