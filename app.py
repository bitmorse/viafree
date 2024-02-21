import requests
import datetime
import streamlit as st
import pytz
from streamlit_autorefresh import st_autorefresh

# Function to fetch multiple connections between two points
def fetch_connections(from_station, to_station, departure_time, num_connections=3):
    """Fetch multiple connections based on a given departure time."""
    base_url = "https://search.ch/timetable/api/route.json"
    params = {
        "from": from_station,
        "to": to_station,
        "date": departure_time.strftime("%m/%d/%Y"),
        "time": departure_time.strftime("%H:%M"),
        "time_type": "depart",
        "num": num_connections  # Fetching multiple connections
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['connections']  # Return all fetched connections
    else:
        return None

# Function to calculate the adjusted time after walking
def calculate_adjusted_time(arrival_time_str, duration_minutes=10):
    arrival_time = datetime.datetime.strptime(arrival_time_str, '%Y-%m-%d %H:%M:%S')
    adjusted_time = arrival_time + datetime.timedelta(minutes=duration_minutes)
    return adjusted_time

# Function to format connections into a table-friendly format
def format_connections_for_table(leg1_connections, leg2_connection):
    # Prepare data for display
    data = []
    for leg1 in leg1_connections:
        arrival1 = leg1['arrival']
        leg1 = leg1['legs'][0]
        track1 = "(Track " + leg1['track']+")" if 'track' in leg1 else ""
        vehicle1 = "🚎" if leg1['type'] == 'bus' else "🚈"
        
        adjusted_departure = calculate_adjusted_time(arrival1, st.session_state['walking_time'])
        leg2 = fetch_connections(st.session_state['leg2_from'], st.session_state['leg2_to'], adjusted_departure, num_connections=1)[0]
        arrival2 = leg2['arrival']
        leg2 = leg2['legs'][0]
        track2 = "(Track " + leg2['track']+")" if 'track' in leg2 else ""
        vehicle2 = "🚎" if leg2['type'] == 'bus' else "🚈"
    
        #format for table
        #format all times to be hours and minutes only with strftime
        arrival1 = datetime.strptime(arrival1, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        departure1 = datetime.strptime(leg1['departure'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        arrival2 = datetime.strptime(arrival2, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        departure2 = datetime.strptime(leg2['departure'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')        
        
        data.append({
            "#1": vehicle1 + " " + leg1['line'] + " " + track1,
            st.session_state['leg1_from']: departure1,
            st.session_state['leg1_to']: arrival1,
            "#2": vehicle2  + " " +  leg2['line'] + " " + track2,
            st.session_state['leg2_from']: departure2,
            st.session_state['leg2_to']: arrival2
            
        })
    return data

count = st_autorefresh(interval=1000*30*60, limit=100, key="viafree")

st.markdown("""
<style>
.big-font {
    font-size:30px !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'loaded_connections' not in st.session_state:
    st.session_state.loaded_connections = 3  # Initial number of connections to display
else:
    # Increment the number of connections if "Load More" is triggered
    if 'load_more' in st.session_state and st.session_state.load_more:
        st.session_state.loaded_connections += 3
        st.session_state.load_more = False  # Reset load more trigger
        
        
if 'leg1_from' not in st.session_state:
    st.session_state['leg1_from'] = "Zürich, Schlyfi"
if 'leg1_to' not in st.session_state:
    st.session_state['leg1_to'] = "Zürich, Kreuzplatz"
if 'walking_time' not in st.session_state:
    st.session_state['walking_time'] = 7
if 'leg2_from' not in st.session_state:
    st.session_state['leg2_from'] = "Zürich Stadelhofen"
if 'leg2_to' not in st.session_state:
    st.session_state['leg2_to'] = "Glattbrugg"


# Sidebar inputs for journey parameters with session state
st.sidebar.text_input("Leg 1 From", key='leg1_from')
st.sidebar.text_input("Leg 1 To", key='leg1_to')
st.sidebar.number_input("Walking Time (minutes)", key='walking_time')
st.sidebar.text_input("Leg 2 From", key='leg2_from')
st.sidebar.text_input("Leg 2 To", key='leg2_to')

# Reverse journey button logic
def reverse_journey():
    st.session_state['leg1_from'], st.session_state['leg2_to'] = st.session_state['leg2_to'], st.session_state['leg1_from']
    st.session_state['leg1_to'], st.session_state['leg2_from'] = st.session_state['leg2_from'], st.session_state['leg1_to']

#use CET timezone
now = datetime.datetime.now(datetime.timezone.utc)
cet = pytz.timezone('CET')
now = now.astimezone(cet)

# Fetch initial connections
leg1_connections = fetch_connections(st.session_state['leg1_from'], st.session_state['leg1_to'], now, num_connections=st.session_state.loaded_connections)
# Continue from the previous adjusted code setup

if leg1_connections:
    for idx, connection in enumerate(leg1_connections, start=1):
        arrival1 = connection['arrival']
        leg1 = connection['legs'][0]
        track1 = "(Track " + leg1['track'] + ")" if 'track' in leg1 else ""
        vehicle1 = "🚎" if leg1['type'] == 'bus' else "🚈"
        terminal1 = leg1['terminal']
        
        adjusted_departure = calculate_adjusted_time(arrival1, st.session_state['walking_time'])
        leg2 = fetch_connections(st.session_state['leg2_from'], st.session_state['leg2_to'], adjusted_departure, num_connections=1)[0]
        arrival2 = leg2['arrival']
        leg2 = leg2['legs'][0]
        track2 = "(Track " + leg2['track'] + ")" if 'track' in leg2 else ""
        vehicle2 = "🚎" if leg2['type'] == 'bus' else "🚈"
        terminal2 = leg2['terminal']
        
        # Format times to HH:mm
        arrival1_time = datetime.datetime.strptime(arrival1, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        departure1_time = datetime.datetime.strptime(leg1['departure'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        arrival2_time = datetime.datetime.strptime(arrival2, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        departure2_time = datetime.datetime.strptime(leg2['departure'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')

        # Use st.expander to group each connection's details
        with st.expander(f"Connection {idx}", expanded=True):
            col1, col2, col3 = st.columns([3, 0.5, 3])
            with col1:
                st.caption(f"{vehicle1} {leg1['line']} to {terminal1} {track1}")
                st.markdown(f'<span class="big-font">{departure1_time}</span><br>{st.session_state['leg1_from']} ',unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">{arrival1_time}</span><br>{st.session_state['leg1_to']} ',unsafe_allow_html=True)
                
            with col2:
                st.markdown("→")
                
            with col3:
                st.caption(f"{vehicle2} {leg2['line']} to {terminal2} {track2}")
                st.markdown(f'<span class="big-font">{departure2_time}</span><br>{st.session_state['leg2_from']} ',unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">{arrival2_time}</span><br>{st.session_state['leg2_to']} ',unsafe_allow_html=True)
else:
    st.error("Unable to fetch connections. Please check your inputs and try again.")


# Button to trigger loading more connections
#center the below buttons
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Load More"):
        st.session_state.load_more = True

with col2:
    # Button to reverse the journey
    if st.button("Reverse Journey", on_click=reverse_journey):
        pass  # The swapping is handled by the on_click function