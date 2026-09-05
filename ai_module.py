from groq import Groq
import streamlit as st
import json

def generate_itinerary(travel_details):
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            st.warning("⚠️ GROQ_API_KEY not found in secrets.")
            st.info("To generate your itinerary, please add `GROQ_API_KEY` in Streamlit Cloud Settings → Secrets (or `.streamlit/secrets.toml` locally).")
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
    Estimate the actual realistic expenditure for the itinerary.
    Do not attempt to match any user budget.
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
        "duration_days": number
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
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": 
            """
                You are a professional travel planning assistant specializing in
                realistic and budget-conscious travel planning.

                IMPORTANT BUDGET RULES:

                1. The user's budget is a spending LIMIT, not a spending TARGET.

                2. NEVER artificially increase expenses just because the user's
                available budget is high.

                3. NEVER artificially decrease expenses just because the user's
                available budget is low.

                4. Estimate expenses based on what the recommended itinerary would
                realistically cost for the specified destination, duration,
                number of people, accommodation type, transportation and activities.

                5. If the user's budget is insufficient, DO NOT change or reduce
                realistic expenses merely to make the itinerary fit the budget.

                6. If the realistic estimated cost exceeds the user's budget, return
                the realistic estimated cost even though it exceeds the budget.

                7. If the user's budget is much higher than the realistic estimated
                cost, DO NOT add unnecessary activities, luxury services, or
                arbitrary expenses simply to use the remaining budget.

                8. The estimated cost must represent the expected cost of the
                recommended trip, NOT the amount of money the user has available.

                9. Do not claim that an extremely low budget is sufficient for an
                expensive destination.

                10. All expenditure values must be plausible for the destination and
                    must be expressed in INR.

                11. Never manipulate individual expense categories to force their sum
                    to equal the user's budget.

                12. Prioritize realism over satisfying the user's stated budget.

                You should still try to recommend affordable options where possible,
                but affordability must come from realistic choices such as budget
                accommodation, public transportation, free attractions, or inexpensive
                food — NOT from inventing unrealistic prices.
                """
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.6,
    max_completion_tokens=8192,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "travel_itinerary",
            "strict": False,
            "schema": {
                "type": "object",
                "properties": {
                    "trip_summary": {
                        "type": "object",
                        "properties": {
                            "destination": {"type": "string"},
                            "duration_days": {"type": "number"},
                        },
                        "required": [
                            "destination",
                            "duration_days",
                        ],
                        "additionalProperties": False
                    },

                    "days": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "day": {"type": "number"},
                                "activities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "time": {"type": "string"},
                                            "activity": {"type": "string"},
                                            "location": {"type": "string"},
                                            "estimated_cost": {"type": "number"},
                                            "food_recommendation": {"type": "string"},
                                            "transport_suggestion": {"type": "string"}
                                        },
                                        "required": [
                                            "time",
                                            "activity",
                                            "location",
                                            "estimated_cost",
                                            "food_recommendation",
                                            "transport_suggestion"
                                        ],
                                        "additionalProperties": False
                                    }
                                },
                                "daily_estimated_total": {"type": "number"}
                            },
                            "required": [
                                "day",
                                "activities",
                                "daily_estimated_total"
                            ],
                            "additionalProperties": False
                        }
                    },

                    "budget_breakdown": {
                        "type": "object",
                        "properties": {
                            "accommodation_total": {"type": "number"},
                            "food_total": {"type": "number"},
                            "transport_total": {"type": "number"},
                            "activities_total": {"type": "number"},
                            "miscellaneous": {"type": "number"}
                        },
                        "required": [
                            "accommodation_total",
                            "food_total",
                            "transport_total",
                            "activities_total",
                            "miscellaneous"
                        ],
                        "additionalProperties": False
                    },

                    "travel_tips": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },

                "required": [
                    "trip_summary",
                    "days",
                    "budget_breakdown",
                    "travel_tips"
                ],

                "additionalProperties": False
            }
        }
    }
)

        content = response.choices[0].message.content
        
        # Strip markdown code fences if present
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
            st.error(f"❌ AI returned invalid JSON: {json_err}")
            st.code(content[:2000])
            return None
    
    except Exception as e:
        st.error(f"⚠️ AI Generation Error: {str(e)}")
        return None