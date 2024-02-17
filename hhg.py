import streamlit as st
from streamlit_gsheets import GSheetsConnection
from thefuzz import fuzz, process


st.title("Happy Hunting Grounds")

if "player1_name" not in st.session_state:
    st.session_state["player1_name"] = "Player 1"
if "player2_name" not in st.session_state:
    st.session_state["player2_name"] = "Player 2"
if "player1_score" not in st.session_state:
    st.session_state["player1_score"] = 0.0
if "player2_score" not in st.session_state:
    st.session_state["player2_score"] = 0.0
if "current_player" not in st.session_state:
    st.session_state["current_player"] = "player1"
if "difficulty_slider" not in st.session_state:
    st.session_state["difficulty_slider"] = 1
if "season_selection" not in st.session_state:
    st.session_state["season_selection"] = "2022-2023"
if "hunting_ground" not in st.session_state:
    st.session_state["hunting_ground"] = "Team @ Venue"
if "response_disabled" not in st.session_state:
    st.session_state["response_disabled"] = True
if "diff_slider_disabled" not in st.session_state:
    st.session_state["diff_slider_disabled"] = False
if "get_hunting_ground_disabled" not in st.session_state:
    st.session_state["get_hunting_ground_disabled"] = False
if "matched_scorer" not in st.session_state:
    st.session_state["matched_scorer"] = None
if "result_state" not in st.session_state:
    st.session_state["result_state"] = None
if "goal_info" not in st.session_state:
    st.session_state["goal_info"] = None
if "progress_buttons_disabled" not in st.session_state:
    st.session_state["progress_buttons_disabled"] = True


with st.expander("Instructions"):
    st.text("This is how to play.")


@st.cache_data
def load_goals():
    url = st.secrets["away_goals_url"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    return data

@st.cache_data
def load_hunting_grounds():
    url = st.secrets["hunting_grounds_url"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    return data

@st.cache_data
def get_unique_goal_scorers(goals_df):
    return goals_df["scorer"].drop_duplicates().sort_values()

# Load the data into the app
# (only loaded once; will be cached)
GOALS_DF = load_goals()
# st.dataframe(GOALS_DF)
HG_DF = load_hunting_grounds()

def select_random_hg(difficulty):
    # Get all records of the desired difficulty.
    possible_hgs = HG_DF.loc[HG_DF["difficulty"] == int(difficulty)]
    # Randomly grab one hunting ground
    selected_hg = possible_hgs.sample(n=1)
    
    if len(selected_hg) != 1:
        raise ValueError(f"Something went wrong when selecting from hunting grounds of difficulty {difficulty}")
    
    # Grab the text
    selected_hg_text = selected_hg["hunting_ground"].iloc[0]

    return selected_hg_text

def get_hunting_ground(difficulty):
    st.session_state["hunting_ground"] = select_random_hg(difficulty=difficulty)
    st.session_state["response_disabled"] = False
    st.session_state["diff_slider_disabled"] = True
    st.session_state["get_hunting_ground_disabled"] = True

def award_points(points):
    if st.session_state["current_player"] == "player1":
        st.session_state["player1_score"] += points
    elif st.session_state["current_player"] == "player2":
        st.session_state["player2_score"] += points

def submit_response(scorer, season, hunting_ground, difficulty):
    # Disable name input and year slider.
    st.session_state["response_disabled"] = True
    # Filter all away goals to only include those for the selected hunting ground.
    valid_goals = GOALS_DF.loc[GOALS_DF["hunting_ground"]==hunting_ground]
    if len(valid_goals) == 0:
        raise ValueError(f"Something went wrong fetching the goals for hunting ground {hunting_ground}.")
    
    # Check if goal scorer text matches goal scorer in df with fuzzyy match.
    valid_scorers = valid_goals["scorer"].tolist()
    
    # N.B. The 'scorer' parameter here refers to the scoring function for the fuzzy match.
    best_name, score = process.extractOne(scorer, valid_scorers, scorer=fuzz.token_set_ratio)
    
    if score < 85:
        # If match is not good enough, award no points.
        st.session_state["result_state"] = "incorrect"
    elif score >= 85:
        st.session_state["matched_scorer"] = best_name
        # Check if they scored in the selected year.
        goals_by_scorer = valid_goals.loc[valid_goals["scorer"] == best_name]
        if season in goals_by_scorer["season"].values:
            st.session_state["result_state"] = "both correct"
            # Add the full points
            points = difficulty
            # Add information about the goal(s).
            st.session_state["goal_info"] = goals_by_scorer.loc[goals_by_scorer["season"] == season]
        else:
            points = difficulty / 2
            st.session_state["result_state"] = "half correct"

        # Award the points to the current player
        award_points(points)

    # Show buttons to move to the next player or start a new game.
    st.session_state["progress_buttons_disabled"] = False

def next_player_reset():
    if st.session_state["current_player"] == "player1":
        st.session_state["current_player"] = "player2"
    elif st.session_state["current_player"] == "player2":
        st.session_state["current_player"] = "player1"

    del st.session_state["hunting_ground"]
    del st.session_state["response_disabled"]
    del st.session_state["diff_slider_disabled"]
    del st.session_state["get_hunting_ground_disabled"]
    del st.session_state["matched_scorer"]
    del st.session_state["result_state"]
    del st.session_state["goal_info"]
    del st.session_state["progress_buttons_disabled"]

    st.session_state["goal_scorer_response"] = None
    st.session_state["season_selection"] = "2022-2023"
    st.session_state["difficulty_slider"] = 1


def new_game_reset():
    for key in st.session_state.keys():
        del st.session_state[key]
    
    st.session_state["goal_scorer_response"] = None

with st.sidebar:
    st.header("Scoreboard")
    player1_col, player2_col = st.columns(2, )
    with player1_col:
        player1_name = st.text_input("Player 1 name", value=None, placeholder=st.session_state["player1_name"], label_visibility="hidden")
        if player1_name is not None:
            st.session_state["player1_name"] = player1_name
        
        st.markdown(f"<h1 style='text-align: center;'>{st.session_state['player1_score']}</h1>", unsafe_allow_html=True)

    with player2_col:
        player2_name = st.text_input("Player 2 name", value=None, placeholder=st.session_state["player2_name"], label_visibility="hidden")
        if player2_name is not None:
            st.session_state["player2_name"] = player2_name
        
        st.markdown(f"<h1 style='text-align: center;'>{st.session_state['player2_score']}</h1>", unsafe_allow_html=True)

SEASONS = [f"{yy}-{yy+1}" for yy in range(1992, 2023)]

if st.session_state["current_player"] == "player1":
    st.subheader(f"{st.session_state['player1_name']}, select a difficulty", anchor=False)
if st.session_state["current_player"] == "player2":
    st.subheader(f"{st.session_state['player2_name']}, select a difficulty", anchor=False)

difficulty_slider = st.select_slider(
    label="Difficulty", 
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    disabled=st.session_state["diff_slider_disabled"],
    key="difficulty_slider",
)

# on_click 
#   - pick random hunting ground with difficulty = player1_difficulty
#   - disable select_slider
#   - print the hunting ground in the subheader
#   - activate the form widgets
hunting_ground = st.button(
    "Get hunting ground", 
    on_click=get_hunting_ground, 
    kwargs={"difficulty": difficulty_slider}, 
    type="primary",
    use_container_width=True,
    disabled=st.session_state["get_hunting_ground_disabled"]
)

st.subheader(st.session_state["hunting_ground"])

goal_scorer_response = st.text_input(
    "Goal scorer", 
    help="""
        Responses are fuzzy-matched with the correct answers, so perfect spelling is not required, 
        but the closer you are, the better. 
        
        For best results, use both first and last names. This is especially true for players whose names
        include accented characters or other characters not part of the standard English alphabet. 
        For example, if you want to guess 'İlkay Gündoğan', entering 'gundogan' will NOT meet the threshold for a correct answer, 
        but 'ilkay gundogan' will be a successful match.
    """,
    disabled=st.session_state["response_disabled"],
    key="goal_scorer_response",
)

# st.selectbox("Goal scorer", options=SCORERS, index=None, disabled=st.session_state["response_disabled"])

season_selection = st.select_slider(
    "Season", 
    options=SEASONS, 
    disabled=st.session_state["response_disabled"],
    key="season_selection",
)

st.button(
    "Submit", 
    on_click=submit_response,
    kwargs={
        "scorer": goal_scorer_response, 
        "season": season_selection, 
        "hunting_ground": st.session_state["hunting_ground"], 
        "difficulty": difficulty_slider,
    },
    type="primary",
    disabled=st.session_state["response_disabled"],
    use_container_width=True,
)

if st.session_state["result_state"] == "incorrect":
    st.success(f"'{goal_scorer_response}' is incorrect.", icon="❌")
elif st.session_state["result_state"] == "half correct":
    st.success(f"""'{st.session_state["matched_scorer"]}' has scored for {st.session_state['hunting_ground']}, but not in the '{season_selection}' season.""", icon="〰️")
elif st.session_state["result_state"] == "both correct":
    st.success(f"""'{st.session_state["matched_scorer"]}' in '{season_selection}' is correct!""", icon="✅")
    for goal_row in st.session_state["goal_info"].itertuples():
        st.markdown(
            f"""{goal_row.date}  
            {goal_row.minute}'  
            [Match report](https://fbref.com/{goal_row.match_report_url})
            """
        )

st.divider()

next_button_col, new_button_col = st.columns(2)
with next_button_col:
    st.button(
        "Next player", 
        on_click=next_player_reset, 
        disabled=st.session_state["progress_buttons_disabled"],
        type="primary",
        use_container_width=True,
    )
with new_button_col:
    st.button(
        "New game", 
        on_click=new_game_reset, 
        # disabled=st.session_state["progress_buttons_disabled"],
        use_container_width=True,
    )