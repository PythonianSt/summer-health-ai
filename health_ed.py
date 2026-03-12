import streamlit as st
import uuid
import qrcode
import random
import io
import os
import json
from openai import OpenAI

st.set_page_config(page_title="AI สุขภาพหน้าร้อน", layout="wide")

# ---------------- OpenAI ----------------
client = None
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- Score Database ----------------
SCORE_FILE = "scores.json"

if os.path.exists(SCORE_FILE):
    with open(SCORE_FILE,"r") as f:
        scores = json.load(f)
else:
    scores = {}

# ---------------- Health Topics ----------------
topics = [
    "ผดร้อน",
    "ผิวไหม้แดด",
    "การขาดน้ำ",
    "เชื้อราผิวหนัง",
    "สิวในหน้าร้อน",
    "ภาวะลมแดด",
    "แพ้ยุง"
]

# ---------------- Mode ----------------
mode = st.query_params.get("mode","tv")

# =================================================
# SMART TV MODE
# =================================================
if mode == "tv":

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    st.markdown("### 📱 สแกน QR Code เพื่อเรียนรู้สุขภาพหน้าร้อนแบบเฉพาะบุคคล")

    # -------- Random Video --------
    videos = ["enjoy.mp4","enjoy2.mp4"]
    video_choice = random.choice(videos)

    if os.path.exists(video_choice):

        video_bytes = open(video_choice,"rb").read()

        video_html = f"""
        <video autoplay loop muted width="900">
        <source src="data:video/mp4;base64,{video_bytes.hex()}" type="video/mp4">
        </video>
        """

        st.video(video_bytes)

    else:
        st.warning("กรุณาวางไฟล์ enjoy.mp4 และ enjoy2.mp4 ในโฟลเดอร์เดียวกัน")

    st.divider()

    # -------- QR CODE --------
    if "APP_URL" in st.secrets:
        base_url = st.secrets["APP_URL"]
    else:
        base_url = "http://localhost:8501"

    link = f"{base_url}?mode=learn"

    qr = qrcode.QRCode(version=1,box_size=10,border=4)
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black",back_color="white")

    buf = io.BytesIO()
    img.save(buf,format="PNG")

    st.image(buf.getvalue(),width=320)

    st.markdown("### 🧠 หัวข้อสุขภาพที่ AI อาจสุ่มให้คุณ")

    st.write("""
    🥵 ผดร้อน  
    🌞 ผิวไหม้แดด  
    💧 การขาดน้ำ  
    🍄 เชื้อราผิวหนัง  
    😓 สิวหน้าร้อน  
    ☀️ ภาวะลมแดด  
    🦟 แพ้ยุง
    """)

    st.success("นักศึกษาแต่ละคนจะได้รับหัวข้อที่แตกต่างกัน")

# =================================================
# STUDENT MODE
# =================================================
else:

    st.title("📱 AI สุขภาพหน้าร้อนสำหรับนักศึกษา")

    st.markdown("### 🌴 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    # -------- Session --------
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "topic" not in st.session_state:
        st.session_state.topic = random.choice(topics)

    topic = st.session_state.topic

    st.subheader(f"🎯 หัวข้อของคุณวันนี้: {topic}")

    # -------- Student Info --------
    nickname = st.text_input("ชื่อเล่นของคุณ")

    sweat = st.selectbox(
        "💦 คุณเหงื่อออกง่ายหรือไม่",
        ["มาก","ปานกลาง","น้อย"]
    )

    skin = st.selectbox(
        "🧴 ปัญหาผิวที่พบบ่อย",
        ["ไม่มี","ผื่นคัน","สิว","เชื้อรา"]
    )

    outdoor = st.selectbox(
        "🏃 ทำกิจกรรมกลางแจ้ง",
        ["บ่อย","บางครั้ง","น้อย"]
    )

    # -------- Generate AI Advice --------
    if st.button("✨ รับคำแนะนำจาก AI"):

        if nickname == "":
            st.warning("กรุณาใส่ชื่อเล่น")
            st.stop()

        if nickname not in scores:
            scores[nickname] = 0

        scores[nickname] += 10

        with open(SCORE_FILE,"w") as f:
            json.dump(scores,f)

        st.success(f"🏆 คะแนนสะสมของคุณ: {scores[nickname]}")

        if client is None:

            st.warning("ยังไม่ได้ตั้งค่า OpenAI API")

        else:

            prompt = f"""
คุณเป็นแพทย์ประจำคลินิกมหาวิทยาลัย

ข้อมูลนักศึกษา
เหงื่อ: {sweat}
ปัญหาผิว: {skin}
กิจกรรมกลางแจ้ง: {outdoor}

หัวข้อสุขภาพ: {topic}

ให้คำแนะนำการดูแลสุขภาพหน้าร้อนแบบสั้น
สำหรับนักศึกษาไทย
และหลีกเลี่ยงการใช้ยาปฏิชีวนะโดยไม่จำเป็น
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role":"user","content":prompt}]
            )

            advice = response.choices[0].message.content

            st.markdown("### 🧠 คำแนะนำสุขภาพจาก AI")

            st.write(advice)

        st.divider()

        tips = [
            "💧 ดื่มน้ำอย่างน้อยวันละ 6-8 แก้ว",
            "🚿 อาบน้ำหลังออกกำลังกาย",
            "👕 ใส่เสื้อผ้าระบายอากาศ",
            "💊 หลีกเลี่ยงการใช้ยาปฏิชีวนะเอง",
            "🌤 หลีกเลี่ยงแดดช่วง 11-15 น."
        ]

        st.info(random.choice(tips))



