import streamlit as st
import random
import os
import json
import qrcode
import io
import base64
import time
from collections import Counter
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh
import pandas as pd

st.set_page_config(page_title="AI Campus Health Platform", layout="wide")

VIDEOS = ["enjoy.mp4", "enjoy2.mp4"]

SCORE_FILE = "scores.json"
USER_FILE = "users.json"
DATA_FILE = "healthdata.json"

topics = [
    "ผดร้อน", "ผิวไหม้แดด", "ขาดน้ำ", "เชื้อราผิวหนัง", "สิวหน้าร้อน",
    "ลมแดด", "แพ้ยุง", "อาหารเป็นพิษ", "โรคลมร้อน",
    "การดื่มน้ำให้เพียงพอ", "การป้องกันไข้แดด",
    "การดูแลผิวหลังโดนแดด", "อาการเพลียแดด",
    "การเลือกครีมกันแดด", "การปฐมพยาบาลเมื่อเป็นลมแดด"
]

quiz_questions = [
    ("การป้องกันผิวไหม้แดดควรใช้ SPF เท่าไร", "30"),
    ("ควรดื่มน้ำวันละกี่ลิตรในหน้าร้อน", "2"),
    ("ผดร้อนเกิดจากอะไร", "เหงื่อ"),
    ("อาการของโรคลมแดดคืออะไร", "ตัวร้อนจัดไม่มีเหงื่อ"),
    ("ควรดื่มน้ำประเภทไหนมากที่สุด", "น้ำเปล่า"),
    ("อาหารประเภทไหนเสียง่าย", "อาหารทะเล"),
    ("อาการอาหารเป็นพิษควรทำอย่างไร", "ดื่มเกลือแร่"),
    ("ครีมกันแดดควรทาซ้ำทุกกี่ชั่วโมง", "2"),
    ("การใส่เสื้อผ้าสีไหนช่วยลดความร้อน", "สีขาว"),
    ("ผักผลไม้ช่วยเพิ่มน้ำในร่างกาย", "แตงโม")
]

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_all_data():
    json.dump(scores, open(SCORE_FILE, "w", encoding="utf-8"))
    json.dump(users, open(USER_FILE, "w", encoding="utf-8"))
    json.dump(healthdata, open(DATA_FILE, "w", encoding="utf-8"))

scores = load_json(SCORE_FILE)
users = load_json(USER_FILE)
healthdata = load_json(DATA_FILE)

client = None
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

mode = st.query_params.get("mode", "tv")


# =========================
# SCORE DASHBOARD COMPONENT
# =========================
def render_score_dashboard():
    """Render a prominent live score dashboard."""
    st.markdown("### 🏆 Live Score Dashboard")

    if not scores:
        st.info("No scores yet — be the first to play!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Top 3 podium
    top3 = sorted_scores[:3]
    medals = ["🥇", "🥈", "🥉"]
    podium_cols = st.columns(len(top3))
    for i, (name, score) in enumerate(top3):
        with podium_cols[i]:
            bg = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32"
            st.markdown(f"""
            <div style="text-align:center;padding:16px 8px;border-radius:12px;
                        background:{bg}22;border:2px solid {bg};margin-bottom:8px;">
                <div style="font-size:2rem;">{medals[i]}</div>
                <div style="font-weight:700;font-size:1.1rem;">{name}</div>
                <div style="font-size:1.5rem;font-weight:800;">{score}</div>
                <div style="font-size:0.75rem;color:#888;">pts</div>
            </div>
            """, unsafe_allow_html=True)

    # Full leaderboard table using native Streamlit (no raw HTML leaking)
    if len(sorted_scores) > 0:
        st.markdown("#### 📋 Full Rankings")
        medals = ["🥇", "🥈", "🥉"]
        rows = []
        for i, (name, score) in enumerate(sorted_scores, 1):
            rank_label = medals[i - 1] if i <= 3 else f"#{i}"
            rows.append({"Rank": rank_label, "Player": name, "Score": score})
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank":   st.column_config.TextColumn("Rank",   width="small"),
                "Player": st.column_config.TextColumn("Player", width="medium"),
                "Score":  st.column_config.NumberColumn("Score (pts)", format="%d"),
            }
        )


# =========================
# 🎮 SPINNER GAME FUNCTION
# =========================
def spinner_game(nickname):
    st.markdown("### 🧠 เกม: หาตัวที่หมุนต่างกัน (จับเวลา)")

    if "game_odd" not in st.session_state:
        st.session_state.game_odd = random.randint(0, 5)
        st.session_state.game_start = time.time()
        st.session_state.game_done = False

    st.markdown("""
    <style>
    @keyframes spin {
        from {transform:rotate(0deg);}
        to {transform:rotate(360deg);}
    }
    .box{
        width:70px;height:70px;margin:10px;
        border-radius:12px;background:white;
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 10px rgba(0,0,0,0.2);
        cursor:pointer;
    }
    .box:hover{
        transform:scale(1.05);
        transition:transform 0.2s;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    clicked = None

    for i in range(6):
        with cols[i % 3]:
            if i == st.session_state.game_odd:
                style = "animation:spin 1s linear infinite reverse;"
            else:
                style = "animation:spin 1s linear infinite;"

            if st.button(" ", key=f"g{i}"):
                clicked = i

            st.markdown(f'<div class="box" style="{style}">🟧</div>', unsafe_allow_html=True)

    if clicked is not None and not st.session_state.game_done:
        rt = int((time.time() - st.session_state.game_start) * 1000)

        if clicked == st.session_state.game_odd:
            st.success(f"🎉 ถูกต้อง! ⏱️ {rt} ms")
            bonus = 5 if rt < 800 else 0
            scores[nickname] = scores.get(nickname, 0) + 10 + bonus
            if bonus:
                st.info("⚡ เร็วมาก +5 คะแนน")
        else:
            st.error(f"❌ ผิด ⏱️ {rt} ms")

        if nickname not in healthdata:
            healthdata[nickname] = {}

        healthdata[nickname]["reaction_time_ms"] = rt
        healthdata[nickname]["timestamp"] = time.time()

        save_all_data()
        st.session_state.game_done = True

    return st.session_state.get("game_done", False)


# =========================
# TV MODE
# =========================
if mode == "tv":
    st_autorefresh(interval=5000, key="tv")

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    tab1, tab2, tab3 = st.tabs(["📺 Live Feed", "📊 Scoreboard", "👥 User Stats"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🎬 Health Education Video")
            available = [v for v in VIDEOS if os.path.exists(v)]
            if available:
                video_idx = int(time.time() / 30) % len(available)
                video_path = available[video_idx]

                # Read and encode the video for autoplay via HTML5
                with open(video_path, "rb") as vf:
                    video_bytes = vf.read()
                video_b64 = base64.b64encode(video_bytes).decode()

                st.markdown(f"""
                <video width="100%" autoplay muted loop playsinline
                       style="border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.15);">
                    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                </video>
                <p style="font-size:0.8rem;color:#888;margin-top:4px;">
                    ▶️ Auto-playing: {video_path}
                </p>
                """, unsafe_allow_html=True)
            else:
                st.warning("No videos found. Please add enjoy.mp4 or enjoy2.mp4")

        with col2:
            st.subheader("📱 Join Session")
            base_url = "http://localhost:8501"
            if "APP_URL" in st.secrets:
                base_url = st.secrets["APP_URL"]
            link = f"{base_url}?mode=student"

            qr = qrcode.make(link)
            buf = io.BytesIO()
            qr.save(buf)
            st.image(buf.getvalue())

            st.metric("👥 Active Students", len(users))
            st.caption(f"Session ID: {int(time.time())}")

        # Score dashboard below video
        st.markdown("---")
        render_score_dashboard()

    with tab2:
        st.subheader("🏆 Live Scoreboard")
        render_score_dashboard()

        if scores:
            st.markdown("### 📈 Score Distribution")
            score_df = pd.DataFrame(list(scores.items()), columns=['User', 'Score'])
            score_df = score_df.sort_values('Score', ascending=False).reset_index(drop=True)
            st.bar_chart(score_df.set_index('User')['Score'])
        else:
            st.info("No scores yet. Waiting for students to join...")

    with tab3:
        st.subheader("👥 User Statistics")

        if users:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Registered", len(users))
            with col2:
                active_users = len([u for u in users if users[u] is True])
                st.metric("Active Today", active_users)
            with col3:
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    st.metric("Average Score", f"{avg_score:.1f}")

            st.markdown("### 📋 Registered Users")
            user_list = pd.DataFrame(list(users.keys()), columns=['Username'])
            st.dataframe(user_list, use_container_width=True)

            if healthdata:
                reaction_times = [v.get("reaction_time_ms", 0) for v in healthdata.values() if "reaction_time_ms" in v]
                if reaction_times:
                    st.markdown("### ⏱️ Reaction Time Analytics")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Average RT", f"{int(sum(reaction_times)/len(reaction_times))} ms")
                    with col2:
                        st.metric("Fastest RT", f"{min(reaction_times)} ms")
        else:
            st.info("No users registered yet")

    st.sidebar.info("🔄 Dashboard auto-refreshes every 5 seconds")


# =========================
# STUDENT MODE
# =========================
elif mode == "student":
    st.title("📱 AI Health Coach")

    if "game_session_active" not in st.session_state:
        st.session_state.game_session_active = False

    nickname = st.text_input("ชื่อเล่น / Nickname")

    if nickname:
        if nickname not in users:
            users[nickname] = True
            if nickname not in scores:
                scores[nickname] = 0
            save_all_data()
            st.success(f"✅ Welcome {nickname}! Your journey begins now.")

        st.sidebar.markdown(f"### 👤 {nickname}")
        st.sidebar.metric("🏆 Your Score", scores.get(nickname, 0))

        if scores:
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            rank = next((i+1 for i, (name, _) in enumerate(sorted_scores) if name == nickname), None)
            if rank:
                st.sidebar.metric("📊 Your Rank", f"#{rank} / {len(scores)}")
                # Removed redundant balloons here — only shown on quiz completion

    st.markdown("---")
    st.markdown("## 🎮 Health Quiz Challenge")

    general_topics = topics.copy()
    skin_topics = ["การดูแลผิว", "ผดร้อน", "เชื้อราผิวหนัง", "สิวหน้าร้อน"]
    outdoor_topics = ["ลมแดด", "ผิวไหม้แดด", "การป้องกันไข้แดด", "โรคลมร้อน"]
    lifestyle_topics = ["การนอนหลับ", "ความเครียด", "การดื่มน้ำ", "อาหารการกิน"]

    with st.expander("📋 Health Self-Assessment", expanded=False):
        sweat = st.selectbox("💧 เหงื่อ", ["มาก", "ปานกลาง", "น้อย"])
        skin = st.selectbox("🧴 ผิว", ["ไม่มี", "สิว", "ผื่น", "เชื้อรา"])
        outdoor = st.selectbox("☀️ กิจกรรมกลางแจ้ง", ["บ่อย", "บางครั้ง", "น้อย"])
        sleep = st.selectbox("😴 การนอน", ["พอ", "น้อย", "ดึก"])
        water = st.selectbox("💦 การดื่มน้ำ", ["เพียงพอ", "น้อย"])
        stress = st.selectbox("😰 ความเครียด", ["น้อย", "ปานกลาง", "สูง"])

        topic_pool = general_topics.copy()
        if skin != "ไม่มี":
            topic_pool += skin_topics
        if outdoor == "บ่อย":
            topic_pool += outdoor_topics
        if sleep != "พอ" or stress == "สูง":
            topic_pool += lifestyle_topics

        topic = random.choice(topic_pool)

        st.subheader("🎯 Today's Health Topic")
        st.info(f"**{topic}**")

        if st.button("🤖 Get AI Health Advice"):
            if nickname == "":
                st.warning("Please enter your nickname first")
                st.stop()

            scores[nickname] = scores.get(nickname, 0) + 10

            healthdata[nickname] = {
                "sweat": sweat, "skin": skin, "outdoor": outdoor,
                "sleep": sleep, "water": water, "stress": stress,
                "topic": topic, "timestamp": time.time()
            }

            save_all_data()
            st.success(f"✨ +10 points! Total: {scores[nickname]} points")

            if client:
                prompt = f"""
คุณเป็นแพทย์มหาวิทยาลัย

ข้อมูล:
เหงื่อ {sweat}
ผิว {skin}
กิจกรรม {outdoor}
นอน {sleep}
น้ำ {water}
เครียด {stress}

หัวข้อ {topic}

ให้คำแนะนำสั้นๆ 4 บรรทัด
"""
                try:
                    res = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.success("💡 Health Advice:")
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.info("AI advice available with OpenAI API key")

    if nickname:
        if "qset" not in st.session_state:
            st.session_state.qset = random.sample(quiz_questions, 5)
            st.session_state.qidx = 0
            st.session_state.done = False
            st.session_state.quiz_score = 0

        if not st.session_state.done:
            idx = st.session_state.qidx

            st.progress(idx / len(st.session_state.qset), text=f"Question {idx + 1} of {len(st.session_state.qset)}")

            if idx < len(st.session_state.qset):
                if idx == len(st.session_state.qset) - 1:
                    st.markdown("### 🎮 Bonus Game!")
                    st.info("Complete the reaction game to earn bonus points!")
                    if spinner_game(nickname):
                        st.session_state.qidx += 1
                        st.rerun()
                else:
                    q, a = st.session_state.qset[idx]
                    st.markdown(f"### Question {idx+1}")
                    st.write(f"**{q}**")

                    choices = [a, "ไม่รู้", "ไม่แน่ใจ", "ข้าม"]
                    random.shuffle(choices)

                    ans = st.radio("เลือกคำตอบ:", choices, key=f"q{idx}", index=None)

                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("✅ Submit Answer", type="primary"):
                            if ans is None:
                                st.warning("Please select an answer")
                            else:
                                if ans == a:
                                    st.success("🎉 Correct! +5 points")
                                    scores[nickname] = scores.get(nickname, 0) + 5
                                    st.session_state.quiz_score += 5
                                else:
                                    st.error(f"❌ Wrong! The correct answer is: {a}")

                                save_all_data()
                                st.session_state.qidx += 1
                                st.rerun()

                    with col2:
                        if st.button("⏭️ Skip Question"):
                            st.session_state.qidx += 1
                            st.rerun()
            else:
                st.session_state.done = True
                save_all_data()

        if st.session_state.done:
            st.balloons()  # ✅ Single balloon — only on quiz completion
            st.success(f"🎉 Congratulations {nickname}! You completed the challenge!")
            st.metric("Quiz Score", st.session_state.get("quiz_score", 0))
            st.metric("Total Score", scores.get(nickname, 0))

            # Inline leaderboard on completion
            render_score_dashboard()

            if st.button("🔄 Play Again", type="primary"):
                for k in ["qset", "qidx", "done", "quiz_score", "game_odd", "game_done", "game_start"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # Live leaderboard in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏆 Live Leaderboard")
    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for i, (name, score) in enumerate(sorted_scores[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
            st.sidebar.write(f"{medal} **{name}**: {score} pts")
        if len(scores) > 5:
            st.sidebar.write(f"... and {len(scores)-5} more players")
    else:
        st.sidebar.info("No players yet")


# =========================
# ADMIN MODE
# =========================
else:
    st.title("📊 Admin Dashboard")

    if st.button("🔄 Refresh Data"):
        st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Total Users", len(users))
    with col2:
        if scores:
            st.metric("🏆 Total Points", sum(scores.values()))
    with col3:
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            st.metric("📊 Average Score", f"{avg_score:.1f}")

    st.markdown("---")
    render_score_dashboard()
    st.markdown("---")

    st.markdown("### 📋 User Data")

    if users:
        user_data = []
        for user in users:
            user_data.append({
                "Username": user,
                "Score": scores.get(user, 0),
                "Registered": "✅" if users[user] else "❌",
                "Last Activity": time.strftime("%Y-%m-%d %H:%M", time.localtime(healthdata.get(user, {}).get("timestamp", 0))) if user in healthdata else "N/A",
                "Reaction Time": f"{healthdata.get(user, {}).get('reaction_time_ms', 'N/A')} ms" if user in healthdata and "reaction_time_ms" in healthdata[user] else "N/A"
            })

        df = pd.DataFrame(user_data)
        df = df.sort_values('Score', ascending=False)

        st.dataframe(df, use_container_width=True, height=400)

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export Data as CSV",
            data=csv,
            file_name=f"health_platform_data_{int(time.time())}.csv",
            mime="text/csv"
        )

        st.markdown("### 📈 Score Distribution")
        score_df = pd.DataFrame([(u, scores.get(u, 0)) for u in users], columns=['User', 'Score'])
        st.bar_chart(score_df.set_index('User'))

        if healthdata:
            st.markdown("### ⏱️ Reaction Time Analysis")
            reaction_data = []
            for user, data in healthdata.items():
                if "reaction_time_ms" in data:
                    reaction_data.append({
                        "User": user,
                        "Reaction Time (ms)": data["reaction_time_ms"],
                        "Score": scores.get(user, 0)
                    })

            if reaction_data:
                rt_df = pd.DataFrame(reaction_data)
                st.dataframe(rt_df, use_container_width=True)
                st.metric("Average Reaction Time", f"{int(rt_df['Reaction Time (ms)'].mean())} ms")
                st.line_chart(rt_df.set_index('User')["Reaction Time (ms)"])
    else:
        st.info("No users registered yet")


import atexit
atexit.register(save_all_data)














