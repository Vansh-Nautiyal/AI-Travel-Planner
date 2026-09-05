# Yatra Saarthi 🧭

**Yatra Saarthi** is an AI-powered travel planning application built as
a student project. It generates personalized, budget-conscious travel
itineraries based on a destination, trip duration, group size,
interests, and accommodation preference.

The application combines **Generative AI**, **OpenStreetMap location
data**, and an interactive map to provide a simple end-to-end travel
planning experience.

> **Demo:** This project is currently configured as a demo application
> with a limit of 3 itinerary generations per session.

## ✨ Features

- **AI-generated itineraries** using Groq and `openai/gpt-oss-20b`
- **Day-wise trip planning** with morning, afternoon, evening, and
    night activities
- **Nearby attraction discovery** based on selected interests
- **Interactive map** displaying nearby locations
- **Budget breakdown** for:
    -   Accommodation
    -   Food
    -   Transport
    -   Activities
    -   Miscellaneous expenses
- **Budget feasibility checking**
    - Domestic destinations use a recommended minimum of INR 5,000 per
        person per day
    - International destinations use a recommended minimum of INR
        12,000 per person per day
- **Travel tips** generated along with the itinerary
- **PDF export** of the generated travel plan
- **Custom CSS-based UI** for a cleaner Streamlit interface
- **Session-based usage limit** for the demo

## 🛠️ Tech Stack

  Technology                  Purpose
  --------------------------- -------------------------------
  Python                      Core application logic
  Streamlit                   Web application and UI
  Groq                        LLM API
  `openai/gpt-oss-20b`        Itinerary generation
  OpenStreetMap / Nominatim   Destination geocoding
  Overpass API                Nearby attraction discovery
  PyDeck                      Interactive map visualization
  ReportLab                   PDF generation
  Pandas                      Location data handling
  Custom CSS                  UI styling

## 🏗️ How It Works

``` text
User Input
    │
    ├── Destination
    ├── Duration
    ├── Budget
    ├── Number of People
    ├── Interests
    └── Accommodation
    │
    ▼
Destination Geocoding
(Nominatim / OpenStreetMap)
    │
    ▼
Country Detection
    │
    ▼
Budget Feasibility Check
    │
    ├── Budget too low ──► Show warning and stop
    │
    └── Budget acceptable
            │
            ▼
Nearby Attraction Search
(Overpass API)
            │
            ▼
Interactive Map
(PyDeck)
            │
            ▼
AI Itinerary Generation
(Groq + GPT OSS)
            │
            ▼
Structured JSON Itinerary
            │
            ├── Day-wise activities
            ├── Activity costs
            ├── Budget breakdown
            └── Travel tips
            │
            ▼
Python Calculates Estimated Trip Cost
            │
            ▼
Compare Estimated Cost
with User Budget
            │
            ▼
Display Itinerary + Budget + PDF
```

## 💰 Budget Logic

A key design decision in Yatra Saarthi is that the user's budget is
treated as a **spending limit**, not a target.

The AI is instructed to estimate the cost of the recommended itinerary
realistically rather than trying to spend the entire amount entered by
the user.

The application first performs a Python-side feasibility check:

``` text
Budget per person per day =
Total Budget / Number of People / Duration
```

The current recommended minimums are:

``` text
Domestic destination       → INR 5,000 / person / day
International destination  → INR 12,000 / person / day
```

If the budget falls below the applicable threshold, itinerary generation
is stopped before making the AI request.

After the itinerary is generated, Python calculates the estimated trip
cost from the returned budget categories:

``` text
Estimated Trip Cost =
Accommodation
+ Food
+ Transport
+ Activities
+ Miscellaneous
```

The calculated amount is then compared with the user's budget.

This separation prevents a high user budget from automatically causing
the AI to inflate the estimated expenses.

## 📂 Project Structure

``` text
Yatra-Saarthi/
│
├── app.py                 # Main Streamlit application
├── ai_module.py           # AI itinerary generation
├── map_utils.py           # Geocoding and nearby attraction search
├── pdf_generator.py       # PDF travel-plan generation
├── style.css              # Custom application styling
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── .streamlit/
│   └── secrets.toml       # Local secrets (not committed)
│
└── .gitignore
```

## 🚀 Getting Started

### 1. Clone the repository

``` bash
git clone https://github.com/Vansh-Nautiyal/Yatra-Saarthi.git
cd Yatra-Saarthi
```

### 2. Create a virtual environment

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create:

``` text
.streamlit/secrets.toml
```

and add:

``` toml
GROQ_API_KEY = "your_groq_api_key"
```

Do **not** commit your API key to GitHub.

### 5. Run the application

``` bash
streamlit run app.py
```

The application will open in your browser.

## 🔑 API / External Services

Yatra Saarthi uses the following external services:

### Groq

Used to generate structured travel itineraries with the
`openai/gpt-oss-20b` model.

### OpenStreetMap Nominatim

Used to convert the user's destination into geographic coordinates and
identify the destination's country.

### Overpass API

Used to search OpenStreetMap data for nearby places matching the user's
selected interests.

The application attempts multiple Overpass servers so that attraction
discovery can continue if one server is unavailable.

## 🗺️ Interest-Based Location Search

Nearby locations are selected according to the user's interests.

Examples include:

- **Nature** → peaks, waterfalls, hills
- **Adventure** → attractions, natural reserves, peaks
- **Food** → cafés and restaurants
- **History** → monuments, archaeological sites, museums
- **Photography** → viewpoints and peaks
- **Nightlife** → bars, pubs, nightclubs
- **Shopping** → malls, supermarkets, clothing stores, department
   stores
- **Spiritual** → temples, churches, shrines

The search radius expands progressively from approximately **5 km → 10
km → 20 km** until enough locations are found or the available results
are returned.

## 📄 PDF Export

After generating an itinerary, users can export the travel plan as a
PDF.

The PDF contains the generated itinerary and budget information and is
created using **ReportLab**.

## 🎓 Project Purpose

Yatra Saarthi was developed as a **student learning project** to explore
practical applications of:

- Generative AI
- Prompt engineering
- Structured LLM responses
- REST APIs
- Geocoding
- OpenStreetMap data
- Data visualization
- Streamlit application development
- PDF generation
- Frontend customization with CSS

The project focuses on demonstrating how multiple APIs and technologies
can be combined into a practical AI-powered application.

## ⚠️ Limitations

Yatra Saarthi is a student/demo project and should not be treated as a
professional travel booking or pricing platform.

Some limitations include:

- AI-generated costs are **estimates**, not live quotations.
- Transportation, accommodation, food, and activity prices can change.
- OpenStreetMap coverage varies by location.
- Nearby attraction availability depends on Overpass API responses.
- AI recommendations may occasionally contain inaccurate or outdated
   information.
- The current application does not directly book hotels, transport, or
    activities.
- The demo currently limits users to 3 itinerary generations per
    session.

## 🔮 Future Improvements

Possible future improvements include:

- Live hotel and transport price integration
- Weather-aware itinerary planning
- Real-time travel alerts
- More accurate destination-specific cost estimation
- User accounts and saved itineraries
- Improved recommendation ranking
- More robust API error handling
- Multi-destination trip planning
- Calendar integration
- Mobile-focused UI improvements
- More detailed travel analytics

## 👨‍💻 Author

**Vansh Nautiyal**

GitHub: https://github.com/Vansh-Nautiyal

## 📜 License

This project is licensed under the terms specified in the repository's
`LICENSE` file.
