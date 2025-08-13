import pandas as pd
from . import helpers as h
from datetime import datetime


def load_lovb_schedule(seasons = None):
    """
    Load cleaned lovb schedule data from the volleydata repository.
    
    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        season                             int
        date                               string
        round                              string
        home_team                          string
        away_team                          string
        home_team_set_wins                 int
        away_team_set_wins                 int
        match_link                         string
        secondary_link                     string
        match_id                           int
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_schedule(2025)
    >>> load_lovb_schedule()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    schedule = pd.read_csv('https://github.com/awosoga/volleydata/releases/download/lovb-schedule/lovb_schedule.csv')
    schedule = schedule[schedule['season'].isin(seasons)]
    return schedule


def load_lovb_officials(seasons = None):
    """
    Load cleaned lovb officials data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        match_id                           int
        season                             int
        match_datetime                     string
        officials_type                     string
        full_name                          string
        first_name                         string
        last_name                          string
        level                              string
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_officials(2025)
    >>> load_lovb_officials()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    officials = pd.read_csv('https://github.com/awosoga/volleydata/releases/download/lovb-officials/lovb_officials.csv')
    officials = officials[officials['season'].isin(seasons)]
    return officials


def load_lovb_player_boxscore(seasons = None):
    """
    Load cleaned lovb player boxscore data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        match_id                           int
        season                             int
        match_datetime                     string
        player_id                          int
        player_name                        string
        first_name                         string
        last_name                          string
        jersey_number                      int
        primary_position                   int
        roster_status                      string
        is_foreign                         bool
        is_confederation                   bool
        is_captain                         bool
        is_libero                          bool
        set_1_is_starter                   bool
        set_1_starting_position            int
        set_2_is_starter                   bool
        set_2_starting_position            int
        set_3_is_starter                   bool
        set_3_starting_position            int
        set_4_is_starter                   bool
        set_4_starting_position            int
        set_5_is_starter                   bool
        set_5_starting_position            int
        team_name                          string
        team_short_name                    string
        team_code                          string
        team_color                         string              
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_pbp(2025)
    >>> load_lovb_pbp()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    player_boxscore = pd.read_csv('https://github.com/awosoga/volleydata/releases/download/lovb-player-boxscore/lovb_player_boxscore.csv')
    player_boxscore = player_boxscore[player_boxscore['season'].isin(seasons)]
    return player_boxscore


def load_lovb_team_staff(seasons = None):
    """
    Load cleaned lovb team staff data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        match_id                           int
        season                             int
        match_datetime                     string
        team_name                          string
        staff_type                         string
        full_name                          string
        first_name                         string
        last_name                          string        
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_team_staff(2025)
    >>> load_lovb_team_staff()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    team_staff = pd.read_csv('https://github.com/awosoga/volleydata/releases/download/lovb-team-staff/lovb_team_staff.csv')
    team_staff = team_staff[team_staff['season'].isin(seasons)]
    return team_staff


def load_lovb_pbp(seasons = None):
    """
    Load cleaned lovb pbp data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        match_id                           int
        season                             int
        match_datetime                     string
        home_team_name                     string
        away_team_name                     string
        team_involved                      string
        jersey_number                      int         
        action                             string
        outcome                            string
        set                                int
        point_number                       int
        point_winner                       string
        home_score                         int
        away_score                         int                           
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_points_log(2025)
    >>> load_lovb_points_log()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    pbp = pd.DataFrame()
    for season in seasons:
        pbp = pd.concat([pbp, pd.read_csv(f'https://github.com/awosoga/volleydata/releases/download/lovb-pbp/lovb_pbp_{season}.csv')])
    return pbp


def load_lovb_events_log(seasons = None):
    """
    Load cleaned lovb events log data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2025)
        - list of int : Multiple seasons (e.g., [2024, 2025])
        - None : Load all available seasons

        All years must be 2025 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        ================================  ===========
        Column Name                        Type
        ================================  ===========
        match_id                           int
        season                             int
        match_datetime                     string
        set                                int
        set_start_time                     string
        set_end_time                       string
        set_duration                       int
        set_final_home_score               int
        set_final_away_score               int
        event_type                         string
        event_time                         string
        libero_enters                      bool
        team_involved                      string
        libero_jersey_number               int
        libero_subsitute_jersey_number     int
        rally_start_time                   string
        rally_end_time                     string
        rally_point_winner                 string
        substitute_in_jersey_number        int
        substitute_out_jersey_number       int
        challenge_approved                 string
        challenge_reason                   string
        challenge_method                   string
        challenge_response                 string
        challenge_at_home_score            float
        challenge_at_away_score            float
        challenge_score_change             string
        serving_team                       string
        current_home_score                 float
        current_away_score                 float
        home_team_p1                       float
        home_team_p2                       float
        home_team_p3                       float
        home_team_p4                       float
        home_team_p5                       float
        home_team_p6                       float
        away_team_p1                       float
        away_team_p2                       float
        away_team_p3                       float
        away_team_p4                       float
        away_team_p5                       float
        away_team_p6                       float
        verified_time                      string
        verified_method                    string
        sanction_type                      string
        sanction_remark                    float
        staff_first_name                   string
        staff_last_name                    string
        staff_type                         string
        ================================  ===========
    
    Examples
    --------
    >>> load_lovb_events_log(2025)
    >>> load_lovb_events_log()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, league_start_year=2025)
    elif seasons is None:
        seasons = list(range(2025, datetime.now().year + 1))
    else:
        raise TypeError(f'Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}')
    
    events_log = pd.DataFrame()
    for season in seasons:
        events_log = pd.concat([events_log, pd.read_csv(f'https://github.com/awosoga/volleydata/releases/download/lovb-events-log/lovb_events_log_{season}.csv')])
    return events_log