import pandas as pd
from . import helpers as h
from datetime import datetime


def load_aupvb_player_info(seasons=None):
    """
    Load cleaned aupvb player info data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2024)
        - list of int : Multiple seasons (e.g., [2022, 2024])
        - None : Load all available seasons

        All years must be 2021 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        =====================================  ===========
        Column Name                             Type
        =====================================  ===========
        season                                  int
        week_number                             int
        game_number                             int
        game_date                               string
        rank                                    int
        rank_change                             int
        cumulative_points                       int
        points_this_match                       int
        played_this_match                       bool
        first_name                              string
        last_name                               string
        uniform_number                          int
        sets_played                             int
        kills                                   int
        kill_per_set                            float
        attack_attempts                         int
        attack_errors                           int
        attack_percentage                       float
        assists                                 int
        assists_per_set                         float
        setting_errors                          int
        service_aces                            int
        service_aces_per_set                    float
        service_errors                          int
        total_reception_attempts                int
        reception_errors                        int
        positive_reception_pct                  float
        digs                                    int
        digs_per_set                            float
        blocks                                  int
        blocks_per_set                          float
        block_assists                           int
        block_assists_per_set                   float
        primary_position_position_lk            string
        primary_position_description            string
        primary_position_short_description      string
        secondary_position_position_lk          string
        secondary_position_description          string
        secondary_position_short_description    string
        current_roster_status_lk                string
        current_roster_status_description       string
        is_home_team                            bool
        team_color                              string
        home_team_name                          string
        away_team_name                          string
        season_id                               int
        season_type                             string
        player_id                               int
        player_slug                             string
        uniform_number_display                  string
        team_id                                 int
        type                                    string
        stat_type                               string
        =====================================  ===========
    
    Examples
    --------
    >>> load_aupvb_player_info(2024)
    >>> load_aupvb_player_info([2022, 2024])
    >>> load_aupvb_player_info()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, 2021)
    elif seasons is None:
        seasons = list(range(2021, datetime.now().year + 1))
    else:
        raise TypeError(f"Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}")
    
    player_info = pd.read_csv("https://github.com/awosoga/volleydata/releases/download/aupvb-player-info/aupvb_player_info.csv")
    player_info = player_info[player_info['season'].isin(seasons)]
    return player_info


def load_aupvb_leaderboards(seasons=None):
    """
    Load cleaned aupvb leaderboards data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2024)
        - list of int : Multiple seasons (e.g., [2022, 2024])
        - None : Load all available seasons

        All years must be 2021 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        =====================================  ===========
        Column Name                             Type
        =====================================  ===========
        season                                  int
        week_number                             int
        game_number                             int
        game_rank                               int
        first_name                              string
        last_name                               string
        uniform_number                          int
        total_points                            int
        mvp_points                              int
        win_points                              int
        stat_points                             int
        first_place_mvp                         bool
        first_place_total_points                int
        second_place_mvp                        bool
        second_place_total_points               int
        third_place_mvp                         bool
        third_place_total_points                int
        defensive_mvp                           bool
        defensive_mvp_total_points              int
        set_wins                                int
        set_wins_total_points                   int
        match_win                               int
        match_win_total_points                  int
        service_aces                            int
        service_ace_points                      int
        service_errors                          int
        service_error_points                    int
        attack_kills                            int
        attack_kill_points                      int
        attack_errors                           int
        attack_error_points                     int
        set_assists                             int
        set_assist_points                       int
        set_errors                              int
        set_error_points                        int
        digs                                    int
        dig_points                              int
        good_receptions                         int
        good_reception_points                   int
        reception_errors                        int
        reception_error_points                  int
        block_assists                           int
        block_assist_points                     int
        block_stuffs                            int
        block_stuff_points                      int
        points_behind                           int
        has_extra_inning_stats                  bool
        is_captain                              bool
        roster_status                           string
        primary_position_position_lk            string
        primary_position_description            string
        primary_position_short_description      string
        team_name                               string
        team_color                              string
        team_seed                               int
        season_id                               int
        competitor_id                           int
        player_id                               int
        player_slug                             string
        uniform_number_display                  int
        overall_rank                            int
        overall_rank_change                     int
        total_au_points                         int
        percent_change                          float
        position_change                         int
        updated_flg                             bool
        tie_flg                                 bool
        missed_games_flg                        bool
        previous_seqno                          int
        has_game_experience                     int
        =====================================  ===========
    
    Examples
    --------
    >>> load_aupvb_leaderboards(2024)
    >>> load_aupvb_leaderboards([2022, 2024])
    >>> load_aupvb_leaderboards()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, 2021)
    elif seasons is None:
        seasons = list(range(2021, datetime.now().year + 1))
    else:
        raise TypeError(f"Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}")
    
    leaderboards = pd.read_csv("https://github.com/awosoga/volleydata/releases/download/aupvb-leaderboards/aupvb_leaderboards.csv")
    leaderboards = leaderboards[leaderboards['season'].isin(seasons)]
    return leaderboards


def load_aupvb_pbp(seasons=None):
    """
    Load cleaned aupvb pbp data from the volleydata repository.

    Parameters
    ----------
    seasons : int, list of int, or None, optional
        Season(s) to load. By default, None loads all available seasons.
        - int : Single season year (e.g., 2024)
        - list of int : Multiple seasons (e.g., [2022, 2024])
        - None : Load all available seasons

        All years must be 2021 or later.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the schedule with the following columns:

        =====================================  ===========
        Column Name                             Type
        =====================================  ===========
        season                                  int
        week_number                             int
        game_number                             int
        play_sequence_number                    int
        set_number                              int
        rally_number                            int
        play_code                               string
        narrative_formatted                     string
        played_id                               int
        serve_ace                               bool
        serve_error                             bool
        serve_continue                          bool
        attack_kill                             bool
        attack_error                            bool
        attack_continue                         bool
        pass_good                               bool
        pass_error                              bool
        pass_continue                           bool
        dig_success                             bool
        dig_continue                            bool
        block_stuff                             bool
        block_assist                            bool
        block_continue                          bool
        set_assist                              bool
        set_error                               bool
        set_continue                            bool
        home_team_score                         int
        away_team_score                         int
        scoring_team_id                         int
        home_team_id                            int
        away_team_id                            int
        set_status_lk                           string
        season_id                               int
        game_id                                 int
        play_text                               string
        start_time                              float
        end_time                                float
        video_minutes                           int
        video_seconds                           int
        alternate_video_seconds                 int
        date_time_file_received                 string
        =====================================  ===========
    
    Examples
    --------
    >>> load_aupvb_pbp(2024)
    >>> load_aupvb_pbp([2022, 2024])
    >>> load_aupvb_pbp()
    """

    if isinstance(seasons, int):
        seasons = [seasons]
    if isinstance(seasons, list):
        h.validate_seasons(seasons, 2021)
    elif seasons is None:
        seasons = list(range(2021, datetime.now().year + 1))
    else:
        raise TypeError(f"Expected seasons to be an int, list of ints, or None, got {type(seasons).__name__}")
    
    # Since there is no 2025 pbp url yet in releases!
    if seasons and seasons[-1] == datetime.now().year: 
        seasons.pop()
    
    pbp = pd.DataFrame()
    for season in seasons:
        pbp = pd.concat([pbp, pd.read_csv(f"https://github.com/awosoga/volleydata/releases/download/aupvb-pbp/aupvb_pbp_{season}.csv")])
    return pbp