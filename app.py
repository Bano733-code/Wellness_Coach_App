import streamlit as st
import pandas as pd
import random
import datetime
import altair as alt
from groq import Groq
from deep_translator import GoogleTranslator

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Wellness Coach", page_icon="🌸", layout="wide")

# ========== GLOBAL STYLES ==========
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
/* Chat bubbles */
.chat-bubble-user {
    background:#fce7f3; padding:10px 15px; border-radius:15px;
    margin:5px; text-align:right; color:#831843; font-weight:500;
}
.chat-bubble-coach {
    background:#e0f2fe; padding:10px 15px; border-radius:15px;
    margin:5px; text-align:left; color:#075985; font-weight:500;
}
/* Gradient Cards */
.section-card {
    background: linear-gradient(135deg, #faf5ff, #f0f9ff);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    border: 2px solid transparent;
    border-image: linear-gradient(90deg, #a78bfa, #f472b6) 1;
}
/* Weekly habit streak badges */
.streak-badge {
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    font-weight: 600;
    color: white;
    margin: 5px;
}
.streak-green { background: #22c55e; }
.streak-orange { background: #f59e0b; }
.streak-red { background: #ef4444; }
/* Buttons Glow */
button {
    background: linear-gradient(90deg, #a5b4fc, #fbcfe8);
    color: #1e293b !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    border: none !important;
    transition: all 0.2s ease-in-out;
}
button:hover {
    background: linear-gradient(90deg, #818cf8, #f472b6);
    box-shadow: 0 0 12px rgba(244,114,182,0.6);
    transform: scale(1.04);
}
</style>
""", unsafe_allow_html=True)

# ========== CONFIG ==========
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

if "history" not in st.session_state: st.session_state.history = []
if "weekly_data" not in st.session_state: st.session_state.weekly_data = []

# ========== SIDEBAR ==========
st.sidebar.title("⚙️ App Settings")

# Language selection
LANGS = {
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi",
    "Punjabi": "pa",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko"
}

lang_choice = st.sidebar.selectbox("🌍 Select Language", list(LANGS.keys()))
target_lang = LANGS[lang_choice]

# User personalization
st.sidebar.subheader("🧑 Personal Info")
name = st.sidebar.text_input("Your Name")
goal = st.sidebar.selectbox("Your Goal", ["Weight Loss", "Stress Relief", "Better Sleep"])

# Quick action button
if st.sidebar.button("✨ Get Daily Motivation"):
    st.sidebar.success("🌸 You are stronger than you think!")

# ========== TRANSLATION ==========
def translate_text(text, target):
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except:
        return text

# ========== CHATBOT ==========
def chatbot_response(user_msg: str, lang="en") -> str:
    if client is None:
        return "⚠️ Missing GROQ_API_KEY."
    eng_msg = translate_text(user_msg, "en") if lang != "en" else user_msg
    messages = [{"role": "system", "content": "You are a friendly wellness coach. Track and guide the user on sleep, steps, water, stress, "
                "nutrition, mindfulness, screen time, social connection, reflection, exercise, and sunlight. "
                "Be supportive and interactive. Keep answers concise (5-7 sentences) and ask a small follow-up."
                },
                {"role": "user", "content": eng_msg}]
    try:
        resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages,
                                              temperature=0.7, max_tokens=200)
        reply = resp.choices[0].message.content
        return translate_text(reply, lang) if lang != "en" else reply
    except Exception as e:
        return f"❌ Error: {e}"

# ========== MAIN APP ==========
st.markdown("""
<div style="text-align:center; padding:20px; 
            background: linear-gradient(120deg, #fdf2f8, #f0f9ff);
            border-radius:15px;">
    <h1 style="color:#000000;">🌸 Wellness Coach App</h1>
    <p style="color:#475569; font-size:18px;">
        Track your health, get AI advice, and stay motivated!
    </p>
</div>
""", unsafe_allow_html=True)

# Navigation
tabs = [
    translate_text("📋 Daily Input", target_lang),
    translate_text("💬 AI Chatbot", target_lang),
    translate_text("📝 Mood Journal", target_lang),
    translate_text("📊 Weekly Tracker", target_lang)
]
tab_choice = st.radio(translate_text("Navigation", target_lang), tabs, horizontal=True)

# ---- DAILY INPUT ----
if tab_choice == tabs[0]:
    st.subheader(translate_text("📋 Daily Wellness Check-in", target_lang))
    sleep = st.number_input("Hours of Sleep", 0, 24, 7)
    steps = st.number_input("Steps Walked", 0, 50000, 5000)
    water = st.number_input("Glasses of Water", 0, 20, 6)
    stress = st.slider("Stress Level (1=low, 10=high)", 1, 10, 5)
    nutrition = st.slider("🍎 Nutrition (1=poor, 10=excellent)", 1, 10, 6)
    mindfulness = st.checkbox("🧘 Did you do mindfulness today?")
    screen_time = st.number_input("📱 Screen Time (hours)", 0, 24, 4)
    social = st.checkbox("🤝 Did you connect with friends/family?")
    exercise = st.checkbox("💪 Did you do strength/stretching today?")
    sunlight = st.checkbox("🌞 Did you spend time outdoors?")
    reflection = st.text_area("✍️ Daily Reflection (optional)")

    if st.button("Get Recommendation"):
        recs = []
        if sleep < 7: recs.append("😴 Try to sleep at least 7–8 hours tonight.")
        else: recs.append("✅ Great job on your sleep!")
        if steps < 8000: recs.append("🚶 Add a short walk to increase your steps.")
        else: recs.append("👏 You hit your step goal!")
        if water < 8: recs.append("💧 Drink more water to stay hydrated.")
        else: recs.append("🌊 Hydration level is great!")
        if stress > 6: recs.append("🧘 Try 5 min deep breathing or journaling.")
        else: recs.append("✨ Stress level is under control.")
        if nutrition < 7: recs.append("🍎 Try to add more fruits & veggies in your meals.")
        else: recs.append("✅ Nutrition on point today!")
        if not mindfulness: recs.append("🧘 Take 2 mins to breathe mindfully.")
        else: recs.append("🌸 Great job practicing mindfulness!")
        if screen_time > 6: recs.append("📱 Reduce late-night screen time for better sleep.")
        else: recs.append("✨ Healthy screen balance today!")
        if not social: recs.append("🤝 Call or message a loved one today.")
        else: recs.append("❤️ You nurtured your social connection!")
        if not exercise: recs.append("💪 Try 10 mins of stretching or push-ups.")
        else: recs.append("🔥 Strong body = strong mind!")
        if not sunlight: recs.append("🌞 Get 5–10 mins of natural sunlight.")
        else: recs.append("🌿 Fresh air does wonders, great job!")
        st.success(translate_text("✅ Your Recommendations:", target_lang))
        for r in recs: 
            st.write(translate_text(r, target_lang))
            
    
    
        today = datetime.date.today().strftime("%Y-%m-%d")
        entry={
            "date": today,
            "sleep": sleep,
            "steps": steps,
            "water": water,
            "stress": stress,
            "nutrition": nutrition,
            "mindfulness": mindfulness,
            "screen_time": screen_time,
            "social": social,
            "exercise": exercise,
            "sunlight": sunlight
        }
        st.session_state.weekly_data = [d for d in st.session_state.weekly_data if d["date"] != today]
        st.session_state.weekly_data.append(entry)

# ---- AI Chatbot ----
elif tab_choice == tabs[1]:
    st.subheader(translate_text("💬 Chat with Your Wellness Coach", target_lang))
    user_msg = st.text_input(translate_text("Ask me anything about your wellness 👇",target_lang))
    if st.button("Send") and user_msg:
        reply = chatbot_response(user_msg)
        st.session_state.history.append(("You", user_msg))
        st.session_state.history.append(("Coach", reply))

    for speaker, msg in st.session_state.history:
        if speaker == "You":
            st.markdown(f"<div class='chat-bubble-user'>{translate_text(msg, target_lang)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-coach'>{translate_text(msg, target_lang)}</div>", unsafe_allow_html=True)

# ---- Mood Journal ----
elif tab_choice == tabs[2]:
    st.subheader(translate_text("📝 Daily Mood Journal",target_lang))
    mood = st.text_area(translate_text("How are you feeling today?",target_lang))
    if st.button(translate_text("Reflect",target_lang)):
        if mood.strip():
            reflection_resp = chatbot_response(
                f"My mood today: {mood}. Give me a short supportive reflection and one tiny action."
            )
            st.markdown(f"<div class='chat-bubble-coach'>{reflection_resp}</div>", unsafe_allow_html=True)
        else:
            st.warning(translate_text("Please enter your mood first.",target_lang))

# ---- Weekly Tracker ----
elif tab_choice == tabs[2]:
    st.subheader("### " + translate_text("📊 Weekly Progress",target_lang))
    if st.session_state.weekly_data:
        df = pd.DataFrame(st.session_state.weekly_data).drop_duplicates(subset=["date"], keep="last")
        df = df.sort_values("date")

        # Section card for recent data
        with st.container():
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.write("### " + translate_text("📅 Your recent data:",target_lang))
            st.dataframe(df)
            st.markdown("</div>", unsafe_allow_html=True)

        # Numeric charts
        numeric_cols = ["sleep", "steps", "water", "stress", "nutrition", "screen_time"]
        existing_numeric = [c for c in numeric_cols if c in df.columns]

        if existing_numeric:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            chart = alt.Chart(df).transform_fold(
                existing_numeric,
                as_=["metric", "value"]
            ).mark_line(point=True).encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("value:Q", title="Value"),
                color=alt.Color("metric:N", title="Metric", scale=alt.Scale(scheme="set2"))
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Weekly streak badges
        bool_cols = ["mindfulness", "social", "exercise", "sunlight"]
        present_bool = [c for c in bool_cols if c in df.columns]
        if present_bool:
            st.markdown("### " + translate_text("### ✅ Weekly Habit Streaks",target_lang))
            last7 = df.tail(7)
            cols = st.columns(len(present_bool))
            for i, c in enumerate(present_bool):
                completed = int(last7[c].sum() if last7[c].dtype == 'bool' else last7[c].astype(bool).sum())
                color = "streak-green" if completed >= 5 else "streak-orange" if completed >= 3 else "streak-red"
                cols[i].markdown(
                    f"<div class='streak-badge {color}'>{c.capitalize()}<br>{completed}/7</div>",
                    unsafe_allow_html=True
                )
    else:
        st.info("### " + translate_text("No weekly data yet. Fill your daily input to start tracking!",target_lang))
 
