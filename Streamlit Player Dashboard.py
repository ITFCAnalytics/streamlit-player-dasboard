# File names to change if needed
raw_nongk = 'Raw FBRef 2024-2025'
final_nongk = 'Final FBRef 2024-2025'

from functools import lru_cache
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import statistics
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup, Comment
import os
from pathlib import Path
import time
from scipy import stats
from statistics import mean
from math import pi

# this is the file path root, i.e. where this file is located
root = os.getcwd() + '/'

# This section creates the programs that gather data from FBRef.com... Data is from FBRef and Opta
def _get_table(soup):
    return soup.find_all('table')[0]

def _get_opp_table(soup):
    return soup.find_all('table')[1]

def _parse_row(row):
    cols = None
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    return cols

def get_df(path, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            URL = path
            time.sleep(4 + attempt * retry_delay)  # Increasing delay between attempts
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            page = requests.get(URL, headers=headers, timeout=30)
            page.raise_for_status()  # Raise an exception for bad status codes
            
            soup = BeautifulSoup(page.content, "html.parser")
            table = _get_table(soup)
            data = []
            headings=[]
            headtext = soup.find_all("th",scope="col")
            for i in range(len(headtext)):
                heading = headtext[i].get_text()
                headings.append(heading)
            headings=headings[1:len(headings)]
            data.append(headings)
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')

            for row_index in range(len(rows)):
                row = rows[row_index]
                cols = _parse_row(row)
                data.append(cols)
            
            data = pd.DataFrame(data)
            data = data.rename(columns=data.iloc[0])
            data = data.reindex(data.index.drop(0))
            data = data.replace('',0)
            return data
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to fetch data after {max_retries} attempts")
            time.sleep(retry_delay)

def get_opp_df(path, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            URL = path
            time.sleep(4 + attempt * retry_delay)  # Increasing delay between attempts
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            page = requests.get(URL, headers=headers, timeout=30)
            page.raise_for_status()
            
            soup = BeautifulSoup(page.content, "html.parser")
            table = _get_opp_table(soup)
            data = []
            headings=[]
            headtext = soup.find_all("th",scope="col")
            for i in range(len(headtext)):
                heading = headtext[i].get_text()
                headings.append(heading)
            headings=headings[1:len(headings)]
            data.append(headings)
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')

            for row_index in range(len(rows)):
                row = rows[row_index]
                cols = _parse_row(row)
                data.append(cols)
            
            data = pd.DataFrame(data)
            data = data.rename(columns=data.iloc[0])
            data = data.reindex(data.index.drop(0))
            data = data.replace('',0)
            return data
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to fetch data after {max_retries} attempts")
            time.sleep(retry_delay)


# this section gets the raw tables from FBRef.com

standard = "https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats"
shooting = "https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats"
passing = "https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats"
pass_types = "https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats"
gsca = "https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats"
defense = "https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats"
poss = "https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats"
misc = "https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats"

df_standard = get_df(standard)
df_shooting = get_df(shooting)
df_passing = get_df(passing)
df_pass_types = get_df(pass_types)
df_gsca = get_df(gsca)
df_defense = get_df(defense)
df_poss = get_df(poss)
df_misc = get_df(misc)

# this section sorts the raw tables then resets their indexes. Without this step, you will
# run into issues with players who play minutes for 2 clubs in a season.

df_standard.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_shooting.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_passing.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_pass_types.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_gsca.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_defense.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_poss.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)
df_misc.sort_values(['Player', 'Squad'], ascending=[True, True], inplace=True)

df_standard = df_standard.reset_index(drop=True)
df_shooting = df_shooting.reset_index(drop=True)
df_passing = df_passing.reset_index(drop=True)
df_pass_types = df_pass_types.reset_index(drop=True)
df_gsca = df_gsca.reset_index(drop=True)
df_defense = df_defense.reset_index(drop=True)
df_poss = df_poss.reset_index(drop=True)
df_misc = df_misc.reset_index(drop=True)

# Now the fun part... merging all raw tables into one.
# Change any column name you want to change:
# Example --   'Gls': 'Goals'  changes column "Gls" to be named "Goals", etc.
## Note that I inclide all columns but don't always change the names... this is useful to me when I need to update the columns, like when FBRef witched to Opta data haha. I got lucky as this made it easier on me!

df = df_standard.iloc[:, 0:10]
df = df.join(df_standard.iloc[:, 13])
df = df.join(df_standard.iloc[:, 26])
df = df.rename(columns={'G-PK': 'npGoals', 'Gls':'Glsxx'})
df = df.join(df_shooting.iloc[:,8:25])
df = df.rename(columns={'Gls': 'Goals', 'Sh': 'Shots', 'SoT': 'SoT', 'SoT%': 'SoT%', 'Sh/90': 'Sh/90', 'SoT/90': 'SoT/90', 'G/Sh': 'G/Sh', 'G/SoT': 'G/SoT', 'Dist': 'AvgShotDistance', 'FK': 'FKShots', 'PK': 'PK', 'PKatt': 'PKsAtt', 'xG': 'xG', 'npxG': 'npxG', 'npxG/Sh': 'npxG/Sh', 'G-xG': 'G-xG', 'np:G-xG': 'npG-xG'})

df = df.join(df_passing.iloc[:,8:13])
df = df.rename(columns={'Cmp': 'PassesCompleted', 'Att': 'PassesAttempted', 'Cmp%': 'TotCmp%', 'TotDist': 'TotalPassDist', 'PrgDist': 'ProgPassDist', })
df = df.join(df_passing.iloc[:,13:16])
df = df.rename(columns={'Cmp': 'ShortPassCmp', 'Att': 'ShortPassAtt', 'Cmp%': 'ShortPassCmp%', })
df = df.join(df_passing.iloc[:,16:19])
df = df.rename(columns={'Cmp': 'MedPassCmp', 'Att': 'MedPassAtt', 'Cmp%': 'MedPassCmp%', })
df = df.join(df_passing.iloc[:,19:22])
df = df.rename(columns={'Cmp': 'LongPassCmp', 'Att': 'LongPassAtt', 'Cmp%': 'LongPassCmp%', })
df = df.join(df_passing.iloc[:,22:31])
df = df.rename(columns={'Ast': 'Assists', 'xAG':'xAG', 'xA': 'xA', 'A-xAG': 'A-xAG', 'KP': 'KeyPasses', '1/3': 'Final1/3Cmp', 'PPA': 'PenAreaCmp', 'CrsPA': 'CrsPenAreaCmp', 'PrgP': 'ProgPasses', })

df = df.join(df_pass_types.iloc[:, 9:23])
df = df.rename(columns={'Live': 'LivePass', 'Dead': 'DeadPass', 'FK': 'FKPasses', 'TB': 'ThruBalls', 'Sw': 'Switches', 'Crs': 'Crs', 'CK': 'CK', 'In': 'InSwingCK', 'Out': 'OutSwingCK', 'Str': 'StrCK', 'TI': 'ThrowIn', 'Off': 'PassesToOff', 'Blocks':'PassesBlocked', 'Cmp':'Cmpxxx'})

df = df.join(df_gsca.iloc[:, 8:16].rename(columns={'SCA': 'SCA', 'SCA90': 'SCA90', 'PassLive': 'SCAPassLive', 'PassDead': 'SCAPassDead', 'TO': 'SCADrib', 'Sh': 'SCASh', 'Fld': 'SCAFld', 'Def': 'SCADef'}))
df = df.join(df_gsca.iloc[:, 16:24].rename(columns={'GCA': 'GCA', 'GCA90': 'GCA90', 'PassLive': 'GCAPassLive', 'PassDead': 'GCAPassDead', 'TO': 'GCADrib', 'Sh': 'GCASh', 'Fld': 'GCAFld', 'Def': 'GCADef'}))

df = df.join(df_defense.iloc[:,8:13].rename(columns={'Tkl': 'Tkl', 'TklW': 'TklWinPoss', 'Def 3rd': 'Def3rdTkl', 'Mid 3rd': 'Mid3rdTkl', 'Att 3rd': 'Att3rdTkl'}))
df = df.join(df_defense.iloc[:,13:24].rename(columns={'Tkl': 'DrbTkl', 'Att': 'DrbPastAtt', 'Tkl%': 'DrbTkl%', 'Lost': 'DrbPast', 'Blocks': 'Blocks', 'Sh': 'ShBlocks', 'Pass': 'PassBlocks', 'Int': 'Int', 'Tkl+Int': 'Tkl+Int', 'Clr': 'Clr', 'Err': 'Err'}))

df = df.join(df_poss.iloc[:,8:30])
df = df.rename(columns={'Touches': 'Touches', 'Def Pen': 'DefPenTouch', 'Def 3rd': 'Def3rdTouch', 'Mid 3rd': 'Mid3rdTouch', 'Att 3rd': 'Att3rdTouch', 'Att Pen': 'AttPenTouch', 'Live': 'LiveTouch', 'Succ': 'SuccDrb', 'Att': 'AttDrb', 'Succ%': 'DrbSucc%', 'Tkld':'TimesTackled', 'Tkld%':'TimesTackled%', 'Carries':'Carries', 'TotDist':'TotalCarryDistance', 'PrgDist':'ProgCarryDistance', 'PrgC':'ProgCarries', '1/3':'CarriesToFinalThird', 'CPA':'CarriesToPenArea', 'Mis': 'CarryMistakes', 'Dis': 'Disposesed', 'Rec': 'ReceivedPass', 'PrgR':'ProgPassesRec'})

df = df.join(df_misc.iloc[:, 8:14])
df = df.rename(columns={'CrdY': 'Yellows', 'CrdR': 'Reds', '2CrdY': 'Yellow2', 'Fls': 'Fls', 'Fld': 'Fld', 'Off': 'Off', })
df = df.join(df_misc.iloc[:,17:24])
df = df.rename(columns={'PKwon': 'PKwon', 'PKcon': 'PKcon', 'OG': 'OG', 'Recov': 'Recov', 'Won': 'AerialWins', 'Lost': 'AerialLoss', 'Won%': 'AerialWin%', })

# Make sure to drop all blank rows (FBRef's tables have several)
df.dropna(subset = ["Player"], inplace=True)

# Turn the minutes columns to integers. So from '1,500' to '1500'. Otherwise it can't do calculations with minutes
for i in range(0,len(df)):
    df.iloc[i][9] = df.iloc[i][9].replace(',','')
df.iloc[:,9:] = df.iloc[:,9:].apply(pd.to_numeric)

# Save the file to the root location
df.to_csv("%s%s.csv" %(root, raw_nongk), index=False)

##################################################################################
##################### Final file for outfield data ###############################
##################################################################################

df = pd.read_csv("%s%s.csv" %(root, raw_nongk))
df_90s = pd.read_csv("%s%s.csv" %(root, raw_nongk))
df_90s['90s'] = df_90s['Min']/90
for i in range(10,125):
    df_90s.iloc[:,i] = df_90s.iloc[:,i]/df_90s['90s']
df_90s = df_90s.iloc[:,10:].add_suffix('Per90')
df_new = df.join(df_90s)

for i in range(len(df_new)):
    df_new['Age'][i] = int(df_new['Age'][i][:2])

df_new.to_csv("%s%s.csv" %(root, final_nongk), index=False)

##################################################################################
################ Download team data, for possession-adjusting ####################
##################################################################################

standard = "https://fbref.com/en/comps/Big5/stats/squads/Big-5-European-Leagues-Stats"
poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

df_standard = get_df(standard)
df_poss = get_df(poss)

df_standard = df_standard.reset_index(drop=True)
df_poss = df_poss.reset_index(drop=True)

############################################

df = df_standard.iloc[:, 0:30]

# Gets the number of touches a team has per 90
df['TeamTouches90'] = float(0.0)
for i in range(len(df)):
    df.iloc[i,30] = float(df_poss.iloc[i,5]) / float(df_poss.iloc[i,4])

# Take out the comma in minutes like above
for j in range(0,len(df)):
    df.at[j,'Min'] = df.at[j,'Min'].replace(',','')
df.iloc[:,7:] = df.iloc[:,7:].apply(pd.to_numeric)
df.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False)


##################################################################################
################ Download opposition data, for possession-adjusting ##############
##################################################################################

opp_poss = "https://fbref.com/en/comps/Big5/possession/squads/Big-5-European-Leagues-Stats"

df_opp_poss = get_opp_df(opp_poss)
df_opp_poss = df_opp_poss.reset_index(drop=True)

############################################

df = df_opp_poss.iloc[:, 0:15]
df = df.rename(columns={'Touches':'Opp Touches'})
df = df.reset_index()

#############################################

df1 = pd.read_csv("%s%s TEAMS.csv"%(root, final_nongk))

df1['Opp Touches'] = 1
for i in range(len(df1)):
    df1['Opp Touches'][i] = df['Opp Touches'][i]
df1 = df1.rename(columns={'Min':'Team Min'})
df1.to_csv("%s%s TEAMS.csv" %(root, final_nongk), index=False)


##################################################################################
################ Make the final, complete, outfield data file ####################
##################################################################################

df = pd.read_csv("%s%s.csv" %(root, final_nongk))
teams = pd.read_csv("%s%s TEAMS.csv" %(root, final_nongk))

df['AvgTeamPoss'] = float(0.0)
df['OppTouches'] = int(1)
df['TeamMins'] = int(1)
df['TeamTouches90'] = float(0.0)

player_list = list(df['Player'])

for i in range(len(player_list)):
    team_name = df[df['Player']==player_list[i]]['Squad'].values[0]
    team_poss = teams[teams['Squad']==team_name]['Poss'].values[0]
    opp_touch = teams[teams['Squad']==team_name]['Opp Touches'].values[0]
    team_mins = teams[teams['Squad']==team_name]['Team Min'].values[0]
    team_touches = teams[teams['Squad']==team_name]['TeamTouches90'].values[0]
    df.at[i, 'AvgTeamPoss'] = team_poss
    df.at[i, 'OppTouches'] = opp_touch
    df.at[i, 'TeamMins'] = team_mins
    df.at[i, 'TeamTouches90'] = team_touches

# All of these are the possession-adjusted columns. A couple touch-adjusted ones at the bottom
df['pAdjTkl+IntPer90'] = (df['Tkl+IntPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjClrPer90'] = (df['ClrPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjShBlocksPer90'] = (df['ShBlocksPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjPassBlocksPer90'] = (df['PassBlocksPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjIntPer90'] = (df['IntPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjDrbTklPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjTklWinPossPer90'] = (df['DrbTklPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjDrbPastPer90'] = (df['DrbPastPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjAerialWinsPer90'] = (df['AerialWinsPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjAerialLossPer90'] = (df['AerialLossPer90']/(100-df['AvgTeamPoss']))*50
df['pAdjDrbPastAttPer90'] = (df['DrbPastAttPer90']/(100-df['AvgTeamPoss']))*50
df['TouchCentrality'] = (df['TouchesPer90']/df['TeamTouches90'])*100
# df['pAdj#OPAPer90'] =(df['#OPAPer90']/(100-df['AvgTeamPoss']))*50
df['Tkl+IntPer600OppTouch'] = df['Tkl+Int'] /(df['OppTouches']*(df['Min']/df['TeamMins']))*600
df['pAdjTouchesPer90'] = (df['TouchesPer90']/(df['AvgTeamPoss']))*50
df['CarriesPer50Touches'] = df['Carries'] / df['Touches'] * 50
df['ProgCarriesPer50Touches'] = df['ProgCarries'] / df['Touches'] * 50
df['ProgPassesPer50CmpPasses'] = df['ProgPasses'] / df['PassesCompleted'] * 50
df['ProgDistancePerCarry'] = (df['ProgCarriesPer90'] / df['ProgCarryDistancePer90']) * 100
df['ProgCarryEfficiency'] = ((df['CarriesToFinalThirdPer90'] * df['CarriesToPenAreaPer90']) / df['CarriesPer90']) * 100
# Convert player for transferMakrt merge
df['PlayerFBref'] = df['Player']
# What % of pass types does a player make
df['ShortPass%'] = (df['ShortPassAttPer90'] / df['PassesAttemptedPer90']) * 100
df['MediumPass%'] = (df['MedPassAttPer90'] / df['PassesAttemptedPer90']) * 100
df['LongPass%'] = (df['LongPassAttPer90'] / df['PassesAttemptedPer90']) * 100
df['ProgPass%'] = (df['ProgPassesPer90'] / df['PassesAttemptedPer90']) * 100
df['Switch%'] = (df['SwitchesPer90'] / df['PassesAttemptedPer90']) * 100
df['KeyPass%'] = (df['KeyPassesPer90'] / df['PassesAttemptedPer90']) * 100
df['Final3rdPass%'] = (df['Final1/3CmpPer90'] / df['PassesAttemptedPer90']) * 100
df['ThroughPass%'] = (df['ThruBallsPer90'] / df['PassesAttemptedPer90']) * 100
# Where does a player touch the ball
df['Def3rdTouch%'] = (df['Def3rdTouchPer90'] / df['LiveTouchPer90']) * 100
df['Mid3rdTouch%'] = (df['Mid3rdTouchPer90'] / df['LiveTouchPer90']) * 100
df['Att3rdTouch%'] = (df['Att3rdTouchPer90'] / df['LiveTouchPer90']) * 100
df['AttPenTouch%'] = (df['AttPenTouchPer90'] / df['LiveTouchPer90']) * 100
df['ActionsPerTouch'] = ((df['PassesAttemptedPer90'] + df['ShotsPer90']) / df['LiveTouchPer90']) * 100
# Where does a player attempt tackles
df['Def3rdTkl%'] = (df['Def3rdTklPer90'] / df['TklPer90']) * 100
df['Mid3rdTkl%'] = (df['Mid3rdTklPer90'] / df['TklPer90']) * 100
df['Att3rdTkl%'] = (df['Att3rdTklPer90'] / df['TklPer90']) * 100

#All of these are aggregated metrics


# Now we'll add the players' actual positions, from @jaseziv, into the file
#tm_pos = pd.read_csv('https://github.com/griffisben/Soccer-Analyses/blob/main/TransfermarktPositions-Jase_Ziv83.csv?raw=true')
tm_pos = pd.read_csv('https://github.com/JaseZiv/worldfootballR_data/raw/master/raw-data/fbref-tm-player-mapping/output/fbref_to_tm_mapping.csv')
df = pd.merge(df, tm_pos, on ='PlayerFBref', how ='left')

for i in range(len(df)):
    if df.Pos[i] == 'GK':
        df['PlayerFBref'][i] = 'Goalkeeper'
df.to_csv("%s%s.csv" %(root, final_nongk), index=False, encoding='utf-8-sig')

df.head()

# Method 1: Convert to string first
unique_values = df['Main Position'].astype(str).unique()
print("Method 1:", unique_values)

# Create datasets for each position

# Filter for Full Backs
df_players_fb = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Left-Back', 'Right-Back']))
                  ].drop_duplicates()

# Filter for Centre Backs
df_players_cb = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Centre-Back']))
                  ].drop_duplicates()

# Filter for Defensive Mids
df_players_dm = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Defensive Midfield']))
                  ].drop_duplicates()

# Filter for Centre Mids
df_players_cm = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Central Midfield']))
                  ].drop_duplicates()

# Filter for Attacking Mids
df_players_am = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Attacking Midfield', 'Second Striker']))
                  ].drop_duplicates()

# Filter for Wingers
df_players_wi = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Left Winger', 'Left Midfield', 'Right Winger', 'Right Midfield']))
                  ].drop_duplicates()

# Filter for Strikers
df_players_st = df[
                    (df['Min'] / df['TeamMins'] >= 0.20) & 
                    (df['Main Position'].isin(['Centre-Forward']))
                  ].drop_duplicates()

def create_percentile_rankings(position_df, metrics_to_rank):
    """
    Creates percentile rankings for specified metrics within a position group
    
    Args:
    position_df: DataFrame containing only players of a specific position
    metrics_to_rank: List of column names to create percentiles for
    
    Returns:
    DataFrame with new percentile columns
    """
    percentile_df = position_df.copy()
    
    for metric in metrics_to_rank:
        # Create the percentile column name
        percentile_col = f'{metric}_PR'
        
        # Calculate percentile rank
        percentile_df[percentile_col] = percentile_df[metric].rank(pct=True) * 100
        
        # Round to 1 decimal place
        percentile_df[percentile_col] = percentile_df[percentile_col].round(1)
    
    return percentile_df

# Example usage for fullbacks
# List the metrics you want to create percentiles for
metrics_to_rank = [
    'Min', 'G+A', 'Glsxx', 'Goals', 'Shots', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 'G/SoT', 'AvgShotDistance', 'FKShots', 'PK', 'PKsAtt', 'xG', 'npxG', 'npxG/Sh', 'G-xG', 'npG-xG', 'PassesCompleted', 'PassesAttempted', 'TotCmp%', 'TotalPassDist', 'ProgPassDist', 'ShortPassCmp', 'ShortPassAtt', 'ShortPassCmp%', 'MedPassCmp', 'MedPassAtt', 'MedPassCmp%', 'LongPassCmp', 'LongPassAtt', 'LongPassCmp%', 'Assists', 'xAG', 'xA', 'A-xAG', 'KeyPasses', 'Final1/3Cmp', 'PenAreaCmp', 'CrsPenAreaCmp', 'ProgPasses', 'LivePass', 'DeadPass', 'FKPasses', 'ThruBalls', 'Switches', 'Crs', 'ThrowIn', 'CK', 'InSwingCK', 'OutSwingCK', 'StrCK', 'Cmpxxx', 'PassesToOff', 'PassesBlocked', 'SCA', 'SCA90', 'SCAPassLive', 'SCAPassDead', 'SCADrib', 'SCASh', 'SCAFld', 'SCADef', 'GCA', 'GCA90', 'GCAPassLive', 'GCAPassDead', 'GCADrib', 'GCASh', 'GCAFld', 'GCADef', 'Tkl', 'TklWinPoss', 'Def3rdTkl', 'Mid3rdTkl', 'Att3rdTkl', 'DrbTkl', 'DrbPastAtt', 'DrbTkl%', 'DrbPast', 'Blocks', 'ShBlocks', 'PassBlocks', 'Int', 'Tkl+Int', 'Clr', 'Err', 'Touches', 'DefPenTouch', 'Def3rdTouch', 'Mid3rdTouch', 'Att3rdTouch', 'AttPenTouch', 'LiveTouch', 'AttDrb', 'SuccDrb', 'DrbSucc%', 'TimesTackled', 'TimesTackled%', 'Carries', 'TotalCarryDistance', 'ProgCarryDistance', 'ProgCarries', 'CarriesToFinalThird', 'CarriesToPenArea', 'CarryMistakes', 'Disposesed', 'ReceivedPass', 'ProgPassesRec', 'Yellows', 'Reds', 'Yellow2', 'Fls', 'Fld', 'Off', 'PKwon', 'PKcon', 'OG', 'Recov', 'AerialWins', 'AerialLoss', 'AerialWin%', 'G+APer90', 'GlsxxPer90', 'GoalsPer90', 'ShotsPer90', 'SoTPer90', 'SoT%Per90', 'Sh/90Per90', 'SoT/90Per90', 'G/ShPer90', 'G/SoTPer90', 'AvgShotDistancePer90', 'FKShotsPer90', 'PKPer90', 'PKsAttPer90', 'xGPer90', 'npxGPer90', 'npxG/ShPer90', 'G-xGPer90', 'npG-xGPer90', 'PassesCompletedPer90', 'PassesAttemptedPer90', 'TotCmp%Per90', 'TotalPassDistPer90', 'ProgPassDistPer90', 'ShortPassCmpPer90', 'ShortPassAttPer90', 'ShortPassCmp%Per90', 'MedPassCmpPer90', 'MedPassAttPer90', 'MedPassCmp%Per90', 'LongPassCmpPer90', 'LongPassAttPer90', 'LongPassCmp%Per90', 'AssistsPer90', 'xAGPer90', 'xAPer90', 'A-xAGPer90', 'KeyPassesPer90', 'Final1/3CmpPer90', 'PenAreaCmpPer90', 'CrsPenAreaCmpPer90', 'ProgPassesPer90', 'LivePassPer90', 'DeadPassPer90', 'FKPassesPer90', 'ThruBallsPer90', 'SwitchesPer90', 'CrsPer90', 'ThrowInPer90', 'CKPer90', 'InSwingCKPer90', 'OutSwingCKPer90', 'StrCKPer90', 'CmpxxxPer90', 'PassesToOffPer90', 'PassesBlockedPer90', 'SCAPer90', 'SCA90Per90', 'SCAPassLivePer90', 'SCAPassDeadPer90', 'SCADribPer90', 'SCAShPer90', 'SCAFldPer90', 'SCADefPer90', 'GCAPer90', 'GCA90Per90', 'GCAPassLivePer90', 'GCAPassDeadPer90', 'GCADribPer90', 'GCAShPer90', 'GCAFldPer90', 'GCADefPer90', 'TklPer90', 'TklWinPossPer90', 'Def3rdTklPer90', 'Mid3rdTklPer90', 'Att3rdTklPer90', 'DrbTklPer90', 'DrbPastAttPer90', 'DrbTkl%Per90', 'DrbPastPer90', 'BlocksPer90', 'ShBlocksPer90', 'PassBlocksPer90', 'IntPer90', 'Tkl+IntPer90', 'ClrPer90', 'ErrPer90', 'TouchesPer90', 'DefPenTouchPer90', 'Def3rdTouchPer90', 'Mid3rdTouchPer90', 'Att3rdTouchPer90', 'AttPenTouchPer90', 'LiveTouchPer90', 'AttDrbPer90', 'SuccDrbPer90', 'DrbSucc%Per90', 'TimesTackledPer90', 'TimesTackled%Per90', 'CarriesPer90', 'TotalCarryDistancePer90', 'ProgCarryDistancePer90', 'ProgCarriesPer90', 'CarriesToFinalThirdPer90', 'CarriesToPenAreaPer90', 'CarryMistakesPer90', 'DisposesedPer90', 'ReceivedPassPer90', 'ProgPassesRecPer90', 'YellowsPer90', 'RedsPer90', 'Yellow2Per90', 'FlsPer90', 'FldPer90', 'OffPer90', 'PKwonPer90', 'PKconPer90', 'OGPer90', 'RecovPer90', 'AerialWinsPer90', 'AerialLossPer90', 'AerialWin%Per90', '90sPer90', 'AvgTeamPoss', 'OppTouches', 'TeamMins', 'TeamTouches90', 'pAdjTkl+IntPer90', 'pAdjClrPer90', 'pAdjShBlocksPer90', 'pAdjPassBlocksPer90', 'pAdjIntPer90', 'pAdjDrbTklPer90', 'pAdjTklWinPossPer90', 'pAdjDrbPastPer90', 'pAdjAerialWinsPer90', 'pAdjAerialLossPer90', 'pAdjDrbPastAttPer90', 'TouchCentrality', 'Tkl+IntPer600OppTouch', 'pAdjTouchesPer90', 'CarriesPer50Touches', 'ProgCarriesPer50Touches', 'ProgPassesPer50CmpPasses'
    # Add more metrics as needed
]

# Create percentile rankings for fullbacks
df_players_fb = create_percentile_rankings(df_players_fb, metrics_to_rank)

# Repeat for other position groups
df_players_cb = create_percentile_rankings(df_players_cb, metrics_to_rank)
df_players_dm = create_percentile_rankings(df_players_dm, metrics_to_rank)
df_players_cm = create_percentile_rankings(df_players_cm, metrics_to_rank)
df_players_am = create_percentile_rankings(df_players_am, metrics_to_rank)
df_players_wi = create_percentile_rankings(df_players_wi, metrics_to_rank)
df_players_st = create_percentile_rankings(df_players_st, metrics_to_rank)

# Example to view results for a specific player
#player_name = "Trent Alexander-Arnold"  # Replace with any player name
#if player_name in df_players_fb['Player'].values:
#    player_percentiles = df_players_fb[df_players_fb['Player'] == player_name]
#    print(f"\nPercentile rankings for {player_name}:")
#    for metric in metrics_to_rank:
#        percentile = player_percentiles[f'{metric}_percentile'].values[0]
#        print(f"{metric}: {percentile:.1f}th percentile")

df_players_fb.head()

# First, concatenate all position DataFrames vertically
df_combined = pd.concat([
    df_players_fb,
    df_players_cb,
    df_players_dm,
    df_players_cm,
    df_players_am,
    df_players_wi,
    df_players_st
], axis=0)

# Reset the index of the combined DataFrame
df_combined = df_combined.reset_index(drop=True)

# Save the combined DataFrame if needed
df_combined.to_csv(f"{root}Combined_Players_With_Percentiles.csv", index=False)

# Verify the merge worked correctly
print("Total players in combined DataFrame:", len(df_combined))
print("Players by position:")
print(df_combined['Main Position'].value_counts())

# First, let's see what columns are actually in the DataFrame
print("Available columns in df_players_fb:")
print(df_players_fb.columns.tolist())

# All of these are aggregated columns
df_combined['Aerial Ability']= (df_combined['AerialWin%Per90_PR']+df_combined['pAdjAerialWinsPer90_PR'])/2
df_combined['Box Defending']= (df_combined['ShBlocksPer90_PR']+df_combined['ClrPer90_PR']+df_combined['pAdjClrPer90_PR']+df_combined['pAdjShBlocksPer90_PR'])/4
df_combined['1v1 Defending']= (df_combined['TklWinPossPer90_PR']+df_combined['DrbTkl%Per90_PR'])/2
df_combined['Defensive Awareness']= (df_combined['IntPer90_PR']+df_combined['PassBlocksPer90_PR']+df_combined['pAdjPassBlocksPer90_PR']+df_combined['pAdjIntPer90_PR'])/4
df_combined['Pass Progression'] = (df_combined['ProgPassesPer90_PR']+df_combined['ProgPassesPer50CmpPasses_PR']+df_combined['ProgPassDistPer90_PR'])/3
df_combined['Pass Retention'] = (df_combined['TotCmp%Per90_PR']+df_combined['ShortPassCmp%Per90_PR']+df_combined['MedPassCmp%Per90_PR']+df_combined['LongPassCmp%Per90_PR'])/4
df_combined['Ball Carrying'] = (df_combined['ProgCarryDistancePer90_PR']+df_combined['ProgCarriesPer90_PR']+df_combined['ProgCarriesPer50Touches_PR'])/3
df_combined['Volume of Take-ons'] = (df_combined['AttDrbPer90_PR'])
df_combined['Retention from Take-ons'] = (df_combined['SuccDrbPer90_PR']+df_combined['DrbSucc%Per90_PR'])/2
df_combined['Chance Creation'] = (df_combined['xAGPer90_PR']+df_combined['xAPer90_PR']+df_combined['KeyPassesPer90_PR']+df_combined['SCAPassLivePer90_PR'])/4
df_combined['Impact in and around box'] = (df_combined['Final1/3CmpPer90_PR']+df_combined['PenAreaCmpPer90_PR']+df_combined['CrsPenAreaCmpPer90_PR']+df_combined['ThruBallsPer90_PR']+df_combined['Att3rdTouchPer90_PR']+df_combined['AttPenTouchPer90_PR'])/6
df_combined['Shot Volume'] = (df_combined['ShotsPer90_PR'])
df_combined['Shot Quality'] = (df_combined['AvgShotDistancePer90_PR']+df_combined['npxG/ShPer90_PR'])/2
df_combined['Self-created Shots'] = (df_combined['SCADribPer90_PR'])

df_combined.head()

# Create a new column 'Position Group' based on Main Position
def map_position_group(position):
    if position in ['Left-Back', 'Right-Back']:
        return 'FB'
    elif position == 'Centre-Back':
        return 'CB'
    elif position == 'Defensive Midfield':
        return 'DM'
    elif position == 'Central Midfield':
        return 'CM'
    elif position in ['Attacking Midfield', 'Second Striker']:
        return 'AM'
    elif position in ['Left Winger', 'Left Midfield', 'Right Winger', 'Right Midfield']:
        return 'W'
    elif position == 'Centre-Forward':
        return 'ST'
    else:
        return 'Other'

# Apply the mapping to create new column
df_combined['Position Group'] = df_combined['Main Position'].apply(map_position_group)

# Verify the results
print("Position Group counts:")
print(df_combined['Position Group'].value_counts())

df_combined = df_combined.sort_values('Min', ascending=False).drop_duplicates(subset=['Player', 'Position Group'], keep='first')

dupe_check = df_combined.query('Player == "Chiquinho"')
dupe_check.head()

from urllib.request import urlopen

import matplotlib.pyplot as plt
from PIL import Image

from mplsoccer import PyPizza, add_image, FontManager

font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Regular.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                          'src/hinted/Roboto-Italic.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                        'RobotoSlab[wght].ttf')

def create_player_pizza(player_name, df=df_combined, save_fig=False):
    """
    Creates a pizza chart for a specified player based on their position group
    
    Args:
    player_name (str): Name of the player
    df (DataFrame): DataFrame containing player data (default: df_combined)
    save_fig (bool): Whether to save the figure (default: False)
    """
    
    # Get player's data and position group
    player_data = df[df['Player'] == player_name].iloc[0]
    position_group = player_data['Position Group']
    squad = player_data['Squad']
    
    # Define metrics for each position group (same as radar chart)
    metrics_by_position = {
        'FB': [
            'Defensive Awareness', 'Box Defending', '1v1 Defending',
            'Pass Progression', 'Pass Retention', 'Ball Carrying',
            'Volume of Take-ons', 'Chance Creation', 'Impact in and around box'
        ],
        'CB': [
            'Aerial Ability', 'Box Defending', '1v1 Defending',
            'Defensive Awareness', 'Pass Retention', 'Pass Progression',
            'Ball Carrying', 'Impact in and around box', 'TouchCentrality'
        ],
        'DM': [
            'Defensive Awareness', '1v1 Defending', 'Pass Retention',
            'Pass Progression', 'Ball Carrying', 'TouchCentrality',
            'Impact in and around box', 'Chance Creation', 'Shot Volume'
        ],
        'CM': [
            'Pass Retention', 'Pass Progression', 'Ball Carrying',
            'TouchCentrality', 'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Defensive Awareness'
        ],
        'AM': [
            'Pass Progression', 'Ball Carrying', 'Volume of Take-ons',
            'Retention from Take-ons', 'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Self-created Shots'
        ],
        'W': [
            'Volume of Take-ons', 'Retention from Take-ons', 'Ball Carrying',
            'Pass Progression', 'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Self-created Shots'
        ],
        'ST': [
            'Shot Volume', 'Shot Quality', 'Self-created Shots',
            'Impact in and around box', 'Aerial Ability', 'Ball Carrying',
            'Volume of Take-ons', 'Chance Creation', 'Pass Retention'
        ]
    }
    
    # Get metrics for player's position
    metrics = metrics_by_position[position_group]
    values = [round(player_data[metric]) for metric in metrics]
    
    # color for the slices and text
    slice_colors = ["#1A78CF"] * 9
    text_colors = ["#000000"] * 9

    # instantiate PyPizza class
    baker = PyPizza(
        params=metrics,                  # list of parameters
        background_color="#EBEBE9",     # background color
        straight_line_color="#EBEBE9",  # color for straight lines
        straight_line_lw=1,             # linewidth for straight lines
        last_circle_lw=0,               # linewidth of last circle
        other_circle_lw=0,              # linewidth for other circles
        inner_circle_size=20            # size of inner circle
    )

    # plot pizza
    fig, ax = baker.make_pizza(
        values,                          # list of values
        figsize=(8, 8.5),                # adjust figsize according to your need
        color_blank_space="same",        # use same color to fill blank space
        slice_colors=slice_colors,       # color for individual slices
        value_colors=text_colors,        # color for the value-text
        value_bck_colors=slice_colors,   # color for the blank spaces
        blank_alpha=0.4,                 # alpha for blank-space colors
        kwargs_slices=dict(
            edgecolor="#F2F2F2", zorder=2, linewidth=1
        ),                               # values to be used when plotting slices
        kwargs_params=dict(
            color="#000000", fontsize=11,
            fontproperties=font_normal.prop, va="center"
        ),                               # values to be used when adding parameter
        kwargs_values=dict(
            color="#000000", fontsize=11,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        )                                # values to be used when adding parameter-values
    )

    # add title
    fig.text(
        0.515, 0.975, f"{player_name} - {squad} | {position_group} Template | 24/25 Season", size=16,
        ha="center", fontproperties=font_bold.prop, color="#000000"
    )

    # add subtitle
    fig.text(
        0.515, 0.953,
        f"Percentile Rank vs Top-Five League {position_group}'s",
        size=13,
        ha="center", fontproperties=font_bold.prop, color="#000000"
    )

    # add credits
    CREDIT_1 = "data: opta viz fbref | using mplsoccer"
    CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"

    fig.text(
        0.99, 0.02, f"{CREDIT_1}\n{CREDIT_2}", size=9,
        fontproperties=font_italic.prop, color="#000000",
        ha="right"
    )

    plt.show()

from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
    
def find_similar_players(player_name, df=df_combined, n_clusters=20, top_n=5):
    """
    Find similar players using KMeans clustering, limited to players in the same position
    """
    # Get player's position
    player_data = df[df['Player'] == player_name]
    if player_data.empty:
        print(f"Player '{player_name}' not found")
        return
    
    player_position = player_data['Main Position'].iloc[0]
    player_position_group = player_data['Position Group'].iloc[0]
    
    # Filter for same position players
    position_df = df[df['Position Group'] == player_position_group]
    
    # Define metrics for each position group (same as radar chart)
    metrics_by_position = {
        'FB': [
            'Aerial Ability', 'Defensive Awareness', 'Defensive Intensity', '1v1 Defending', 
            'Pass Progression', 'Pass Retention', 'Ball Carrying',
            'Volume of Take-ons', 'Chance Creation', 'Impact in and around box'
        ],
        'CB': [
            'Aerial Ability', 'Box Defending', 'Defensive Awareness', '1v1 Defending',
            'Defensive Intensity', 'Pass Progression', 'Pass Retention',
            'Switching Play', 'Ball Carrying', 'Shot Volume'
        ],
        'DM': [
            'Aerial Ability', 'Defensive Awareness', 'Defensive Intensity', '1v1 Defending',
            'Pass Progression', 'Pass Retention', 'Switching Play', 'Volume of Take-ons',
            'Retention from Take-ons', 'Shot Volume'
        ],
        'CM': [
            'Defensive Awareness', 'Defensive Intensity', 'Pass Progression', 'Pass Retention',
            'Ball Carrying', 'Volume of Take-ons', 'Retention from Take-ons',
            'Chance Creation', 'Impact in and around box', 'Shot Volume'
        ],
        'AM': [
            'Defensive Intensity', 'Pass Progression', 'Pass Retention',
            'Volume of Take-ons', 'Retention from Take-ons', 'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Self-created Shots'
        ],
        'W': [
            'Defensive Intensity', 'Pass Retention',
            'Ball Carrying', 'Volume of Take-ons', 'Retention from Take-ons',
            'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Self-created Shots'
        ],
        'ST': [
            'Aerial Ability', 'Defensive Intensity',
            'Pass Retention', 'Ball Carrying', 'Volume of Take-ons',
            'Chance Creation', 'Impact in and around box',
            'Shot Volume', 'Shot Quality', 'Self-created Shots'
        ]
    }
    
    # Get metrics for player's position
    metrics = metrics_by_position[player_position_group]
    values = [round(player_data[metric]) for metric in metrics]
    
    # Create list of metrics for comparison
    #metrics = ['Aerial Ability', 'Box Defending', '1v1 Defending', 'Defensive Awareness', 'Pass Progression', 'Pass Retention', 'Ball Carrying', 'Volume of Take-ons', 'Retention from Take-ons', 'Chance Creation', 'Impact in and around box', 'Shot Volume', 'Shot Quality', 'Self-created Shots', 'Switching Play', 'Defensive Intensity']
    
    # Select only the metrics that exist in the dataframe
    available_metrics = [col for col in metrics if col in position_df.columns]
    
    # Create similarity DataFrame with available metrics
    df_similar = position_df[['Player', 'Main Position', 'Position Group'] + available_metrics].copy()
    
    # Handle missing values
    df_similar = df_similar.fillna(0)
    
    # Store player names and positions
    player_names = df_similar['Player'].tolist()
    player_position = df_similar['Main Position'].tolist()
    player_position_group = df_similar['Position Group'].tolist()
    
    # Drop non-numeric columns
    df_similar = df_similar.drop(['Player', 'Main Position', 'Position Group'], axis=1)
    
    # Scale the features
    scaler = preprocessing.MinMaxScaler()
    x_scaled = scaler.fit_transform(df_similar.values)
    x_norm = pd.DataFrame(x_scaled)
    
    # PCA transformation
    pca = PCA(n_components=2)
    df3 = pd.DataFrame(pca.fit_transform(x_norm))
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(df3)
    
    # Add player info back to DataFrame
    df3['clusters'] = clusters
    df3['name'] = player_names
    df3['position'] = player_position
    df3['position group'] = player_position_group
    df3.columns = ['x', 'y', 'clusters', 'name', 'position', 'position group']
    
    # Create distance matrix
    dist_matrix = pd.DataFrame(index=df3['name'], columns=df3['name'])
    
    # Calculate distances
    for i in range(len(dist_matrix)):
        x_i = df3.iloc[i,0]
        y_i = df3.iloc[i,1]
        for j in range(len(dist_matrix)):
            x_j = df3.iloc[j,0]
            y_j = df3.iloc[j,1]
            dist_matrix.iloc[i,j] = ((((x_i-x_j)**2) + ((y_i-y_j)**2))**(0.5))
    
    # Calculate max distances
    max_euc_dist = list(dist_matrix.max())
    
    # Create similarity matrix
    sim_matrix = pd.DataFrame(index=df3['name'], columns=df3['name'])
    for i in range(len(dist_matrix)):
        for j in range(len(dist_matrix)):
            sim_matrix.iloc[i,j] = ((max_euc_dist[i]-dist_matrix.iloc[i,j])*100/max_euc_dist[i])
    
    # Get similar players
    similar_players = pd.DataFrame({
        'Player': sim_matrix.index,
        'Similarity %': sim_matrix[player_name].values
    })
    
    # Sort by similarity
    similar_players = similar_players.sort_values('Similarity %', ascending=False)
    
    # Add cluster and position information
    similar_players = similar_players.merge(
        df3[['name', 'clusters', 'position', 'position group']],
        left_on='Player',
        right_on='name',
        how='left'
    )
    
    # Remove the target player and get top N
    similar_players = similar_players[similar_players['Player'] != player_name].head(top_n)
    
    # Add team information
    similar_players = similar_players.merge(
        df[['Player', 'Squad']], 
        on='Player', 
        how='left'
    )
    
    # Clean up and reorder columns
    similar_players = similar_players.drop('name', axis=1)
    similar_players = similar_players[['Player', 'Squad', 'position', 'position group', 'Similarity %', 'clusters']]
    similar_players = similar_players.rename(columns={'clusters': 'Cluster'})
    
    return similar_players

import matplotlib.cm as cm

def create_player_bars(player_name, df=df_combined, save_fig=False):
    """
    Creates a bar chart for a specified player based on their position group
    """
    # Get player's data and position group
    player_data = df[df['Player'] == player_name].iloc[0]
    position_group = player_data['Position Group']
    #chart_types = 'Pass Types', 'Touch Areas', 'Tackle Areas', 'Defensive Play', 'Ball Progression and Retention', 'Ball Carrying and Dribbling', 'Creativity and Attacking Play', 'Goal Threat'
    squad = player_data['Squad']
    
    # Define metrics for each position group
    chart_metrics_by_position = {
        'FB': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR',
                'AttPenTouch%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'DrbTkl%_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'RecovPer90_PR',
                'pAdjClrPer90_PR',
                'pAdjShBlocksPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'CarriesToPenAreaPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'PenAreaCmpPer90_PR',
                'ThruBallsPer90_PR',
                'CrsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'npxGPer90_PR',
                'SCAPer90_PR'
            ]
        },
        'CB': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'Final3rdPass%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'DrbTkl%_PR',
                'FlsPer90_PR',
                'PKconPer90_PR',
                'OGPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'RecovPer90_PR',
                'pAdjClrPer90_PR',
                'pAdjShBlocksPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'npxGPer90_PR'
            ]
        },
        'DM': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'DrbTkl%_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'RecovPer90_PR',
                'pAdjClrPer90_PR',
                'pAdjShBlocksPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'ThruBallsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'npxGPer90_PR'
            ]
        },
        'CM': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR',
                'AttPenTouch%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'DrbTkl%_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'RecovPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'CarriesToPenAreaPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'PenAreaCmpPer90_PR',
                'CrsPenAreaCmpPer90_PR',
                'ThruBallsPer90_PR',
                'CrsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'npxGPer90_PR',
                'npxG/ShPer90_PR',
                'SCAPer90_PR',
                'SCADribPer90_PR'
            ]
        },
        'AM': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR',
                'AttPenTouch%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'CarriesToPenAreaPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'ProgCarryEfficiency_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'PenAreaCmpPer90_PR',
                'CrsPenAreaCmpPer90_PR',
                'ThruBallsPer90_PR',
                'CrsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'SoT%Per90',
                'npxGPer90_PR',
                'npxG/ShPer90_PR',
                'SCAPer90_PR',
                'SCADribPer90_PR'
            ]
        },
        'W': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR',
                'AttPenTouch%_PR'
            ],
            'Tackle Areas': [
                'Def3rdTkl%_PR',
                'Mid3rdTkl%_PR',
                'Att3rdTkl%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'CarriesToPenAreaPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'ProgCarryEfficiency_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'PenAreaCmpPer90_PR',
                'CrsPenAreaCmpPer90_PR',
                'ThruBallsPer90_PR',
                'CrsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'SoT%Per90',
                'npxGPer90_PR',
                'npxG/ShPer90_PR',
                'SCAPer90_PR',
                'SCADribPer90_PR'
            ]
        },
        'ST': {
            'Pass Types': [
                'ShortPass%_PR',
                'MediumPass%_PR',
                'LongPass%_PR',
                'ProgPass%_PR',
                'Switch%_PR',
                'KeyPass%_PR',
                'Final3rdPass%_PR',
                'ThroughPass%_PR'
            ],
            'Touch Areas': [
                'TouchesPer90_PR',
                'TouchCentrality_PR',
                'Def3rdTouch%_PR',
                'Mid3rdTouch%_PR',
                'Att3rdTouch%_PR',
                'AttPenTouch%_PR'
            ],
            'Defensive Play': [
                'TklPer90_PR',
                'FlsPer90_PR',
                'PassBlocksPer90_PR',
                'IntPer90_PR',
                'AerialWinsPer90_PR',
                'AerialWin%_PR'
            ],
            'Ball Progression and Retention': [
                'PassesCompletedPer90_PR',
                'TotCmp%_PR',
                'Final1/3CmpPer90_PR',
                'ProgPassesPer90',
                'SwitchesPer90_PR',
                'ReceivedPassPer90_PR',
                'ProgPassesRecPer90_PR'
            ],
            'Ball Carrying and Dribbling': [
                'AttDrbPer90_PR',
                'DrbSucc%_PR',
                'CarriesPer90_PR',
                'CarriesToFinalThirdPer90_PR',
                'CarriesToPenAreaPer90_PR',
                'ProgCarriesPer50Touches_PR',
                'ProgDistancePerCarry_PR',
                'ProgCarryEfficiency_PR',
                'FldPer90_PR'
            ],
            'Creativity and Attacking Play': [
                'AssistsPer90_PR',
                'xAPer90_PR',
                'KeyPassesPer90_PR',
                'PenAreaCmpPer90_PR',
                'CrsPenAreaCmpPer90_PR',
                'ThruBallsPer90_PR',
                'CrsPer90_PR'
            ],
            'Goal Threat': [
                'GoalsPer90_PR',
                'ShotsPer90_PR',
                'SoT%Per90',
                'npxGPer90_PR',
                'npxG/ShPer90_PR',
                'AvgShotDistancePer90_PR',
                'SCAPer90_PR',
                'SCADribPer90_PR'
            ]
        }
    }

        # Get metrics for player's position
    for chart_type in chart_metrics_by_position[position_group]:
        metrics = chart_metrics_by_position[position_group][chart_type]
        values = [round(player_data[metric]) for metric in metrics]
        
        # Normalize values to range from 0 to 100
        normalized_values = np.clip(values, 0, 100)  # Ensure values are within 0-100
        colors = cm.RdYlGn(normalized_values / 100)  # Normalize to [0, 1] for colormap

        fig, ax = plt.subplots(figsize=(16, len(metrics)))
        bars = ax.barh(metrics, values, color=colors)
        
        # Add dashed grey gridlines
        ax.grid(axis='x', color='grey', linestyle='--', linewidth=0.5)
        ax.axvline(x=50, color='black', linewidth=0.8)  # Adjust linewidth as needed
        
        # Remove axes splines
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)
        
        # Show top values 
        ax.invert_yaxis()
            
        # Remove x, y Ticks
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        
        # Add annotation to bars
        for i in ax.patches:
            plt.text(i.get_width()+0.2, i.get_y()+0.5, 
                     str(round((i.get_width()), 2)),
                     fontsize = 10, fontweight ='bold',
                     color ='grey')
            
        # Add Plot Title
        ax.set_title(f"{chart_type} -",
                     loc ='left', pad = 12.0, fontsize = 24, fontweight = 'normal', color = 'black', fontname = 'Arial', style = 'normal')

        # Set x-axis limits from 0 to 100
        ax.set_xlim(0, 100)

        # Show Plot
        plt.show()

        #plt.barh(metrics, values, color ='green', width = 0.5)
        #plt.xlabel("Metrics")
        #plt.ylabel("Percentile Rank")
        #plt.title(f"{chart_type} -")
        #plt.show()



# Example usage:
# similar_players = find_similar_players("Erling Haaland")
# display(similar_players)

from ipywidgets import widgets
from IPython.display import display, HTML
import numpy as np

def create_player_selector(df=df_combined):
    # Get sorted list of unique player names with teams
    player_list = sorted([f"{row['Player']} ({row['Squad']})" 
                         for _, row in df.iterrows()])
    
    # Create the dropdown widget
    player_dropdown = widgets.Combobox(
        placeholder='Search for a player...',
        options=player_list,
        description='Player:',
        ensure_option=True,
        style={'description_width': 'initial'}
    )
    
    # Create output widgets for displaying results
    output_pizza = widgets.Output()
    output_bar = widgets.Output()
    output_similar = widgets.Output()
    
    # Create a function to handle selection
    def on_player_select(change):
        if change['type'] == 'change' and change['name'] == 'value':
            selected = change['new']
            if selected in player_list:
                # Clear previous outputs
                output_pizza.clear_output()
                output_bar.clear_output()
                output_similar.clear_output()
                
                # Extract player name and team from selection
                player_name = selected.split(' (')[0]
                team_name = selected.split('(')[1].rstrip(')')
                
                # Get the specific player row using both name and team
                player_data = df[(df['Player'] == player_name) & 
                               (df['Squad'] == team_name)]
                
                if not player_data.empty:
                    # Display pizza chart
                    with output_pizza:
                        create_player_pizza(player_name)

                    with output_bar:
                        create_player_bars(player_name)
                    
                    # Display similar players
                    with output_similar:
                        similar = find_similar_players(player_name)
                        # Format similarity percentage to 1 decimal place
                        similar['Similarity %'] = similar['Similarity %'].apply(lambda x: np.round(x, 1))
                        display(HTML(f"<h3>Similar Players to {player_name}</h3>"))
                        display(similar)
    
    # Attach the handler to the dropdown
    player_dropdown.observe(on_player_select)
    
    # Create layout
    display(widgets.VBox([
        player_dropdown,
        widgets.HBox([
            output_pizza,
            output_bar,
            output_similar
        ])
    ]))

# Use the selector
create_player_selector()