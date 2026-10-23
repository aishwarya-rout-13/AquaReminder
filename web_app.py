import streamlit as st
import pandas as pd
from datetime import date, datetime
import time

from streamlit import components

st.set_page_config(page_title="AquaReminder", page_icon="💧", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #eff9ff 0%, #ffffff 55%, #e8f6ff 100%); }
.block-container { max-width: 1050px; padding-top: 2rem; }
.hero { padding: 1.4rem 1.6rem; border-radius: 22px; background: linear-gradient(120deg,#087fbd,#42b9e8); color: white; }
.hero h1 { color: white; margin: 0; }
.hero p { color: #eefaff; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

if "entries" not in st.session_state:
    st.session_state.entries = []
if "goal" not in st.session_state:
    st.session_state.goal = 2000
if "interval" not in st.session_state:
    st.session_state.interval = 30
if "reminders_on" not in st.session_state:
    st.session_state.reminders_on = False
if "last_reminder" not in st.session_state:
    st.session_state.last_reminder = time.time()
if "web_alert" not in st.session_state:
    st.session_state.web_alert = ""

today = date.today()
today_entries = [e for e in st.session_state.entries if e["date"] == today.isoformat()]
total = sum(e["ml"] for e in today_entries)
goal = int(st.session_state.goal)
remaining = max(goal - total, 0)
progress = min(total / goal, 1.0) if goal else 0

st.markdown("""
<div class="hero">
  <h1>💧 AquaReminder</h1>
  <p>Your friendly hydration companion. Small sips, healthier habits.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.goal = st.number_input(
        "Daily water goal (ml)", min_value=250, max_value=6000, step=250,
        value=int(st.session_state.goal), key="goal_input"
    )
    intervals = [1, 15, 30, 45, 60, 90, 120]
    st.session_state.interval = st.selectbox(
        "Reminder interval (minutes)", intervals,
        index=intervals.index(st.session_state.interval), key="interval_input"
    )
    st.caption("The 1-minute option is useful for testing.")
    if st.button("▶️ Start reminders", use_container_width=True):
        st.session_state.reminders_on = True
        st.session_state.last_reminder = time.time()
        st.session_state.web_alert = ""
        st.success("Reminders started while this page remains open.")
    if st.button("⏸️ Pause reminders", use_container_width=True):
        st.session_state.reminders_on = False
        st.info("Reminders paused.")
    st.divider()
    st.caption("Web reminders appear inside this page. A hosted website cannot use Plyer to send Windows notifications to each visitor.")

# A timed Streamlit fragment checks for reminders while the page is open.
if hasattr(st, "fragment"):
    @st.fragment(run_every="10s")
    def reminder_checker():
        if st.session_state.get("reminders_on", False):
            elapsed = time.time() - st.session_state.get("last_reminder", time.time())
            if elapsed >= int(st.session_state.interval) * 60:
                st.session_state.last_reminder = time.time()
                st.session_state.web_alert = datetime.now().strftime("%I:%M %p")
                st.warning("🔔 Time to drink some water! Take a short break and hydrate.")
                import streamlit.components.v1 as components

                components.html("""<audio autoplay>
             <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
              type="audio/ogg"> </audio>""", height=0)
            elif st.session_state.get("web_alert"):
                st.info(f"💧 Last reminder: {st.session_state.web_alert}")
            else:
                st.success("Reminders are active. Keep this page open.")
        else:
            st.caption("Reminder status: paused")
    reminder_checker()
else:
    st.info("Timed reminders require a recent Streamlit version. Upgrade Streamlit if this message appears.")

st.write("")
left, right = st.columns([1.3, 1])
with left:
    st.subheader("Today's hydration")
    st.metric("Water consumed", f"{total:,} ml", f"{total / 250:.0f} glasses of 250 ml")
    st.progress(progress, text=f"{progress * 100:.0f}% of your {goal:,} ml goal")
    st.write(f"**{remaining:,} ml** remaining to reach your goal.")
    amount = st.selectbox(
        "Choose amount to log", [150, 200, 250, 300, 350, 500],
        index=2, format_func=lambda x: f"{x} ml"
    )
    if st.button("💧 I drank water", type="primary", use_container_width=True):
        st.session_state.entries.append({
            "date": today.isoformat(),
            "time": datetime.now().strftime("%H:%M:%S"),
            "ml": int(amount)
        })
        st.rerun()
    if total >= goal:
        st.balloons()
        st.success("🎉 Daily goal reached. Great job!")

with right:
    st.subheader("Quick tips")
    st.markdown("""
    - Keep a water bottle nearby.
    - Take small breaks between tasks.
    - Use reminders as a prompt, not a strict medical target.
    - Individual hydration needs can vary.
    """)
    st.info("This starter version keeps entries in the current browser session. Download your history to save a copy.")

st.divider()
st.subheader("📈 Daily progress")
if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries)
    daily = df.groupby("date", as_index=False)["ml"].sum().sort_values("date")
    st.bar_chart(daily.set_index("date")["ml"])
    history = df.sort_values(["date", "time"], ascending=False).copy()
    history.columns = ["Date", "Time", "Amount (ml)"]
    st.dataframe(history, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download history as CSV", csv, "aquareminder_history.csv", "text/csv")
else:
    st.write("Your logged water entries will appear here after you add water.")

st.caption("AquaReminder • Built with Python and Streamlit • Portfolio project")
