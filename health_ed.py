import streamlit as st
import random
import os
import json
import uuid
import qrcode
import io
import time
from openai import OpenAI

st.set_page_config(page_title="AI Health Wall", layout="wide")

VIDEOS = ["enjoy.mp4", "enjoy2.mp4"]

SCORE_FILE = "scores.json"
USER_FILE = "users.json"
TOPIC_FILE = "topics.json"

topics = [
"ผดร้อน",
"ผิวไหม้แดด",
"ขาดน้ำ",
"เชื้อราผิวหนัง",
"สิวหน้าร้อน",
"ลมแดด",
"แพ้ยุง"
]

def load_json(file):
    if os.path.exists(file):
        with open(file,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

scores = load_json(SCORE_FILE)
users = load_json(USER_FILE)
topic_count = load_json(TOPIC_FILE)

client = None
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

mode = st.query_params.get("mode","tv")

# ================================
# TV MODE
# ================================

if mode == "tv":

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    col1,col2 = st.columns([2,1])

    with col1:

        available_videos = [v for v in VIDEOS if os.path.exists(v)]

        if available_videos:

            if "video_index" not in st.session_state:
                st.session_state.video_index = random.randint(0,len(available_videos)-1)

            video_file = available_videos[st.session_state.video_index]

            st.video(video_file, autoplay=True)

        else:
            st.error("ไม่พบไฟล์ enjoy.mp4 หรือ enjoy2.mp4")

    with col2:

        st.subheader("📱 Scan เพื่อเรียนรู้สุขภาพ")

        base_url = "http://localhost:8501"

        if "APP_URL" in st.secrets:
            base_url = st.secrets["APP_URL"]

        link = f"{base_url}?mode=student"

        qr = qrcode.QRCode(box_size=8,border=2)
        qr.add_data(link)
        qr.make()

        img = qr.make_image()

        buf = io.BytesIO()
        img.save(buf)

        st.image(buf.getvalue(),width=220)

        st.metric("👥 ผู้เข้าร่วม",len(users))

        st.markdown("### 🏆 Leaderboard")

        if scores:

            top = sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

            for name,score in top:
                st.write(f"👤 {name} : {score}")

    st.divider()

    st.subheader("📊 ความสนใจด้านสุขภาพ")

    if topic_count:
        st.bar_chart(topic_count)

    st.info("🤖 AI Doctor: ดื่มน้ำมากขึ้นและหลีกเลี่ยงแดดช่วงเที่ยง")

    time.sleep(30)

    if available_videos:
        st.session_state.video_index = random.randint(0,len(available_videos)-1)

    st.rerun()

# ================================
# STUDENT MODE
# ================================

else:

    st.title("📱 AI สุขภาพหน้าร้อนสำหรับนักศึกษา")

    st.markdown("### 🌴 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "topic" not in st.session_state:
        st.session_state.topic = random.choice(topics)

    topic = st.session_state.topic

    st.subheader(f"🎯 หัวข้อของคุณ : {topic}")

    nickname = st.text_input("ชื่อเล่น")

    sweat = st.selectbox("💦 เหงื่อออก",["มาก","ปานกลาง","น้อย"])

    skin = st.selectbox("🧴 ปัญหาผิว",["ไม่มี","สิว","ผื่น","เชื้อรา"])

    outdoor = st.selectbox("🏃 กิจกรรมกลางแจ้ง",["บ่อย","บางครั้ง","น้อย"])

    if st.button("✨ รับคำแนะนำ AI"):

        if nickname == "":
            st.warning("กรุณาใส่ชื่อเล่น")
            st.stop()

        users[nickname] = True

        with open(USER_FILE,"w",encoding="utf-8") as f:
            json.dump(users,f)

        if nickname not in scores:
            scores[nickname] = 0

        scores[nickname] += 10

        with open(SCORE_FILE,"w",encoding="utf-8") as f:
            json.dump(scores,f)

        topic_count[topic] = topic_count.get(topic,0)+1

        with open(TOPIC_FILE,"w",encoding="utf-8") as f:
            json.dump(topic_count,f)

        st.success(f"🏆 คะแนนสะสม {scores[nickname]}")

        if client:

            prompt = f"""
คุณเป็นแพทย์มหาวิทยาลัย

ข้อมูลนักศึกษา
เหงื่อ {sweat}
ผิว {skin}
กิจกรรม {outdoor}

หัวข้อ {topic}

ให้คำแนะนำสุขภาพหน้าร้อนแบบสั้น
สำหรับนักศึกษาไทย
"""

            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role":"user","content":prompt}]
            )

            advice = res.choices[0].message.content

            st.markdown("### 🧠 AI แนะนำ")

            st.write(advice)

        tips = [
        "💧 ดื่มน้ำวันละ 6-8 แก้ว",
        "🚿 อาบน้ำหลังออกกำลังกาย",
        "👕 ใส่เสื้อผ้าระบายอากาศ",
        "🌤 หลีกเลี่ยงแดด 11-15 น.",
        "💊 ไม่ใช้ยาปฏิชีวนะเอง"
        ]

        st.info(random.choice(tips))

        st.balloons()






