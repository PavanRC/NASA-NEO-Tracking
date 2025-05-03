import streamlit as st
import pymysql
import pandas as pd

# MySQL connection settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345",
    "database": "nasa_asteroids"
}

# Establish DB connection
def get_connection():
    return pymysql.connect(**DB_CONFIG)

# Query options
query_options = {
    "1. Count how many times each asteroid has approached Earth": """
        SELECT neo_reference_id, COUNT(*) AS approach_count
        FROM close_approach
        GROUP BY neo_reference_id
    """,
    "2. Average velocity of each asteroid": """
        SELECT neo_reference_id, AVG(relative_velocity_kmph) AS avg_velocity
        FROM close_approach
        GROUP BY neo_reference_id
    """,
    "3. Top 10 fastest asteroids": """
        SELECT name, MAX(relative_velocity_kmph) AS max_velocity
        FROM asteroids
        JOIN close_approach ON asteroids.id = close_approach.neo_reference_id
        GROUP BY name
        ORDER BY max_velocity DESC
        LIMIT 10
    """,
    "4. Hazardous asteroids that approached more than 3 times": """
        SELECT a.name, COUNT(*) AS approach_count
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE a.is_potentially_hazardous_asteroid = TRUE
        GROUP BY a.name
        HAVING approach_count > 3
    """,
    "5. Month with most asteroid approaches": """
        SELECT MONTH(close_approach_date) AS month, COUNT(*) AS total_approaches
        FROM close_approach
        GROUP BY month
        ORDER BY total_approaches DESC
        LIMIT 1
    """,
    "6. Fastest ever approach": """
        SELECT name, close_approach_date, relative_velocity_kmph
        FROM asteroids
        JOIN close_approach ON asteroids.id = close_approach.neo_reference_id
        ORDER BY relative_velocity_kmph DESC
        LIMIT 1;
    """,

    "7. Sort asteroids by max estimated diameter": """
        SELECT name, estimated_diameter_max_km
        FROM asteroids
        ORDER BY estimated_diameter_max_km DESC;
    """,

    "8. Asteroids getting closer over time": """
        SELECT neo_reference_id, close_approach_date, miss_distance_km
        FROM close_approach
        ORDER BY neo_reference_id, close_approach_date;
    """,

    "9. Closest approach per asteroid": """
        SELECT a.name, c.close_approach_date, MIN(c.miss_distance_km) AS closest_distance
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        GROUP BY a.name;
    """,

    "10. Asteroids with velocity > 50,000 km/h": """
        SELECT DISTINCT a.name, c.relative_velocity_kmph
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.relative_velocity_kmph > 50000;
    """,

    "11. Count of approaches per month": """
        SELECT MONTH(close_approach_date) AS month, COUNT(*) AS approach_count
        FROM close_approach
        GROUP BY month;
    """,

    "12. Asteroid with highest brightness (lowest magnitude)": """
        SELECT name, absolute_magnitude_h
        FROM asteroids
        ORDER BY absolute_magnitude_h ASC
        LIMIT 1;
    """,

    "13. Hazardous vs non-hazardous asteroid count": """
        SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count
        FROM asteroids
        GROUP BY is_potentially_hazardous_asteroid;
    """,

    "14. Asteroids passed closer than the Moon (<1 LD)": """
        SELECT name, close_approach_date, miss_distance_lunar
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE miss_distance_lunar < 1;
    """,

    "15. Asteroids that came within 0.05 AU": """
        SELECT name, close_approach_date, astronomical
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE astronomical < 0.05;
    """
    # You can extend up to 15 here...
}

st.title("☄️ NASA NEO Dashboard - Streamlit")

# Predefined query selector
st.sidebar.header("🔍 Explore Predefined Insights")
query_choice = st.sidebar.selectbox("Choose a query", list(query_options.keys()))

if st.sidebar.button("Run Query"):
    with get_connection().cursor() as cursor:
        cursor.execute(query_options[query_choice])
        data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.subheader("📊 Query Result")
        st.dataframe(df)

# Filters section
st.sidebar.header("🎛️ Filter-Based Search")

# Slider: velocity
min_velocity = st.sidebar.slider("Minimum Velocity (km/h)", 0, 100000, 50000)
# Date picker
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")


if st.sidebar.button("Apply Filters"):
    query = f"""
        SELECT a.name, c.close_approach_date, c.relative_velocity_kmph, 
               c.miss_distance_km, c.orbiting_body
        FROM asteroids a
        JOIN close_approach c ON a.id = c.neo_reference_id
        WHERE c.relative_velocity_kmph > {min_velocity}
          AND c.close_approach_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY c.relative_velocity_kmph DESC
        LIMIT 100
    """
    with get_connection().cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data)
        st.subheader("📌 Filtered Asteroids Data")
        st.dataframe(df)