import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path

from ai_module import generate_itinerary
from map_utils import geocode_location, fetch_nearby_attractions
from pdf_generator import generate_pdf


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Yatra Saarthi",
    layout="wide"
)


# =========================================================
# LOAD EXTERNAL CSS
# =========================================================

css_path = Path(__file__).with_name("style.css")

with open(css_path, encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =========================================================
# INPUT VALIDATION
# =========================================================

def validate_input(destination, interests):

    if not destination:
        st.error("Please enter a destination.")
        st.stop()

    if not interests:
        st.warning(
            "Select at least one interest for better recommendations."
        )


# =========================================================
# SESSION STATE
# =========================================================

if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

if "travel_details" not in st.session_state:
    st.session_state.travel_details = None


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <h1 class="app-title">
        Yatra Saarthi
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="app-description" style="font-size:1.25rem; padding-left:10%; padding-right:10%;">
        Plan smarter journeys with AI — generate personalized,
        budget-friendly student itineraries powered by
        real-time location data and interactive maps.
        <br>
        <span class="demo-note" style="font-size: 1.1rem;">
            This is currently a demo version — limited to 3 uses per session.
        </span>
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TRAVEL INPUT FORM
# =========================================================

left, center, right = st.columns([1, 2, 1])

with center:

    with st.form("my_form"):

        destination = st.text_input(
            "Destination"
        )

        duration = st.number_input(
            "Duration of trip (in days)",
            min_value=1
        )

        budget = st.number_input(
            "Total Budget (in INR)",
            min_value=1000,
            step=500
        )

        people = st.number_input(
            "Number of People in Group",
            min_value=1
        )

        interests = st.multiselect(
            "Select your interests",
            [
                "Adventure",
                "Nature",
                "Food",
                "History",
                "Nightlife",
                "Shopping",
                "Spiritual",
                "Photography"
            ]
        )

        accommodation = st.selectbox(
            "Accommodation Type",
            [
                "Hotel",
                "AirBnB",
                "Budget Hotel",
                "Luxury"
            ]
        )

        submitted = st.form_submit_button(
            "Generate Travel Plan",
            use_container_width=True
        )


# =========================================================
# GENERATE TRAVEL PLAN
# =========================================================

if submitted:

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    validate_input(destination, interests)


    # -----------------------------------------------------
    # Demo usage limit
    # -----------------------------------------------------

    if st.session_state.usage_count >= 3:

        st.warning(
            "Demo Usage Limit Reached! (3 uses)"
        )

        st.stop()


    # -----------------------------------------------------
    # Geocode destination
    # -----------------------------------------------------

    lat, lon, country_code = geocode_location(destination)

    if lat is None:

        st.error(
            "Cannot find the location! "
            "Please enter a valid location."
        )

        st.stop()

    # -----------------------------------------------------
    # Budget feasibility check
    # -----------------------------------------------------

    DOMESTIC_THRESHOLD = 5000
    INTERNATIONAL_THRESHOLD = 12000

    budget_per_person_per_day = (
        budget / people / duration
    )

    if country_code == "in":
        minimum_budget = DOMESTIC_THRESHOLD

    else:
        minimum_budget = INTERNATIONAL_THRESHOLD

    if budget_per_person_per_day < minimum_budget:
        st.warning(
            f"Your budget is below the recommended minimum "
            f"of INR {minimum_budget:,} per person per day "
            f"for this destination. Please increase your "
            f"budget to generate a realistic itinerary."
        )
        st.stop()

    # -----------------------------------------------------
    # Find nearby attractions
    # -----------------------------------------------------

    with st.spinner("Finding nearby locations..."):

        attractions, used_radius = fetch_nearby_attractions(
            lat,
            lon,
            interests
        )

    st.success(
        f"Found {len(attractions)} locations "
        f"within {used_radius / 1000} km"
    )

    
    # Prepare travel details
    travel_details = {

        "destination": destination,

        "duration": duration,

        "budget": budget,

        "people": people,

        "interests": interests,

        "accomodation": accommodation,

        "nearby_attractions": attractions
    }
    

    st.session_state.travel_details = travel_details


    # =====================================================
    # NEARBY LOCATIONS
    # =====================================================

    st.divider()

    st.markdown(
        """
        <h2 class="section-heading">
            Nearby Locations
        </h2>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([2, 1])


    # -----------------------------------------------------
    # MAP
    # -----------------------------------------------------

    with left:

        locations = pd.DataFrame(attractions)

        if not locations.empty:

            layer = pdk.Layer(
                "ScatterplotLayer",

                data=locations,

                get_position="[lon, lat]",

                get_color="[255, 0, 0, 160]",

                get_radius=120,

                pickable=True,
            )

            view_state = pdk.ViewState(

                latitude=locations["lat"].mean(),

                longitude=locations["lon"].mean(),

                zoom=12,
            )

            tooltip = {

                "html": "<b>{name}</b>",

                "style": {
                    "color": "white"
                }
            }

            deck = pdk.Deck(

                layers=[layer],

                initial_view_state=view_state,

                tooltip=tooltip
            )

            st.pydeck_chart(deck)

        else:

            st.info(
                "No nearby locations were found."
            )


    # -----------------------------------------------------
    # ATTRACTION LIST
    # -----------------------------------------------------

    with right:

        st.subheader(
            "Nearby Attractions"
        )

        if attractions:

            for place in attractions[:10]:

                st.markdown(
                    f"""
                    <div class="attraction-item">
                        → {place["name"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.write(
                "No attractions available."
            )


    # =====================================================
    # AI ITINERARY GENERATION
    # =====================================================

    with st.spinner(
        "Generating your travel plan..."
    ):

        itinerary = generate_itinerary(
            travel_details
        )

        if itinerary:

            st.session_state.itinerary = itinerary

            st.session_state.usage_count += 1


# =========================================================
# DISPLAY GENERATED ITINERARY
# =========================================================

if st.session_state.itinerary:

    st.markdown(
        """
        <h2 class="section-heading">
            Your Day-wise Itinerary
        </h2>
        """,
        unsafe_allow_html=True
    )


    left, center, right = st.columns(
        [1, 3, 1]
    )


    with center:

        for day in st.session_state.itinerary["days"]:

            with st.expander(
                f"Day {day['day']}"
            ):

                for activity in day["activities"]:

                    # Activity time
                    st.markdown(
                        f"""
                        <h3 class="activity-time">
                            {activity["time"]}
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )


                    # Activity name
                    st.markdown(
                        f"""
                        <h4 class="activity-name">
                            {activity["activity"]}
                        </h4>
                        """,
                        unsafe_allow_html=True
                    )


                    # Activity details
                    st.markdown(
                        f"""
                        <div class="activity-details">
                            <div>
                                <b>Location:</b>
                                {activity["location"]}
                            </div>
                            <div>
                                <b>Estimated Cost:</b>
                                INR {activity["estimated_cost"]}
                            </div>
                            <div>
                                <b>Food Recommendation:</b>
                                {activity["food_recommendation"]}
                            </div>
                            <div>
                                <b>Transport:</b>
                                {activity["transport_suggestion"]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("---")


                # Daily total
                st.markdown(
                    f"""
                    <h4 class="daily-total">
                        Daily Estimated Total:
                        INR {day["daily_estimated_total"]}
                    </h4>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # BUDGET BREAKDOWN
    # =====================================================

    with center:

        st.divider()

        st.markdown(
            """
            <h2 class="section-heading">
                Budget Breakdown
            </h2>
            """,
            unsafe_allow_html=True
        )


        budget_details = (
            st.session_state.itinerary[
                "budget_breakdown"
            ]
        )


        estimated_trip_cost = (

            budget_details[
                "accommodation_total"
            ]

            +

            budget_details[
                "food_total"
            ]

            +

            budget_details[
                "transport_total"
            ]

            +

            budget_details[
                "activities_total"
            ]

            +

            budget_details[
                "miscellaneous"
            ]
        )


        st.markdown(
            f"""
            <div class="budget-card">
                <div class="budget-row">
                    <span>Accommodation</span>
                    <span>
                        INR {budget_details["accommodation_total"]}
                    </span>
                </div>
                <div class="budget-row">
                    <span>Food</span>
                    <span>
                        INR {budget_details["food_total"]}
                    </span>
                </div>
                <div class="budget-row">
                    <span>Transport</span>
                    <span>
                        INR {budget_details["transport_total"]}
                    </span>
                </div>
                <div class="budget-row">
                    <span>Activities</span>
                    <span>
                        INR {budget_details["activities_total"]}
                    </span>
                </div>
                <div class="budget-row">
                    <span>Miscellaneous</span>
                    <span>
                        INR {budget_details["miscellaneous"]}
                    </span>
                </div>
                <div class="budget-total">
                    <span>Total Expense</span>
                    <span>
                        INR {estimated_trip_cost}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # BUDGET MESSAGE
        # =================================================

        st.markdown("<br>", unsafe_allow_html=True)


        user_budget = (
            st.session_state.travel_details[
                "budget"
            ]
        )


        if estimated_trip_cost <= user_budget:
            st.success(
                f"✅ The estimated trip cost of INR {estimated_trip_cost:,} "
                f"is within your budget of INR {budget:,}."
            )
        else :
            st.warning(
                f"⚠️ The estimated trip cost of INR {estimated_trip_cost:,} "
                f"exceeds your budget of INR {budget:,}."
            )
            


        # =================================================
        # PDF DOWNLOAD
        # =================================================

        st.divider()

        st.markdown(
            """
            <h3 class="download-heading">
                Download Your Travel Plan
            </h3>
            """,
            unsafe_allow_html=True
        )


        pdf_bytes = generate_pdf(
            st.session_state.itinerary
        )


        st.download_button(

            label="Download Travel Plan as PDF",

            data=pdf_bytes,

            file_name=(
                f"{st.session_state.travel_details['destination']}"
                "_travel_plan.pdf"
            ),

            mime="application/pdf",

            use_container_width=True
        )