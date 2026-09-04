from groq import Groq
import streamlit as st
import json

def generate_itinerary(travel_details):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            st.warning("⚠️ GROQ_API_KEY not found in secrets.")
            st.info("To generate your itinerary, please add `GROQ_API_KEY` in Streamlit Cloud Settings → Secrets (or `.streamlit/secrets.toml` locally).")
            st.stop()
    except Exception as e:
        st.error(f"Error accessing secrets: {str(e)}")
        st.stop()

    client = Groq(api_key=api_key)

    prompt = f"""
    Create a {travel_details["duration"]} day itinerary for a group of {travel_details["people"]} people.
    Plan as a professional travel planner specializing in budget-friendly student trips. Plan according to the time of the day - morning, afternoon, and evening.
    For each time (morning, afternoon or evening) add the estimated cost for the activity.  
    Moreover add a few tips at the end to make the trip more enjoyable. 

    Destination: {travel_details["destination"]}
    Total budget: INR {travel_details["budget"]}
    Budget per day: INR {travel_details["budget_per_day"]}
    Budget per person: INR {travel_details["budget_per_person"]}
    Interested activities: {travel_details["interests"]}
    Accommodation: {travel_details["accomodation"]}

    IMPORTANT:
    - Return ONLY valid JSON
    - No markdown
    - No explanation text
    - Do NOT use backticks
    - Do NOT add text before or after JSON

    JSON Format -
    Return JSON strictly in this format:

    {{
    "trip_summary": {{
        "destination": "string",
        "duration_days": number,
        "total_budget": number,
        "budget_per_day": number,
        "budget_per_person": number
    }},
    "days": [
        {{
        "day": 1,
        "activities": [
            {{
            "time": "Morning / Afternoon / Evening / Night",
            "activity": "Detailed description of activity",
            "location": "Place name",
            "estimated_cost": number,
            "food_recommendation": "Food or restaurant suggestion",
            "transport_suggestion": "How to reach / travel suggestion"
            }}
        ],
        "daily_estimated_total": number
        }}
    ],
    "budget_breakdown": {{
        "accommodation_total": number,
        "food_total": number,
        "transport_total": number,
        "activities_total": number,
        "miscellaneous": number
    }},
    "travel_tips": [
        "Tip 1",
        "Tip 2"
    ]
    }}
    """

    try :
        response = client.chat.completions.create(
            model = "mixtral-8x7b-32768",
            messages=[
                {"role" : "system", "content" : "You are a travel planning assistant."},
                {"role" : "user", "content" : prompt}
            ],
            temperature=0.6
        )

        content = response.choices[0].message.content
        
        # Strip markdown code fences if present (Groq sometimes adds them despite instructions)
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        
        if content.endswith("```"):
            content = content[:-3]  # Remove closing ```
        
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as json_err:
            st.error(f"❌ AI returned invalid JSON. Details: {str(json_err)}")
            st.debug(f"Raw response: {content[:200]}...")  # Show first 200 chars for debugging
            return None
    
    except Exception as e:
        st.error(f"⚠️ AI Generation Error: {str(e)}")
        st.debug(f"Error type: {type(e).__name__}")  # Help debug the specific error
        return None