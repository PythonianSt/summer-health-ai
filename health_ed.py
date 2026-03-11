import streamlit as st
import uuid
import qrcode
import random
import io
import os
from openai import OpenAI

st.set_page_config(page_title="Summer Health AI Learning", layout="wide")

# ---------- OpenAI ----------
client = None
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- Health Topics ----------
topics = [
    "heat rash",
    "sunburn",
    "dehydration",
    "fungal skin infection",
    "acne in hot weather",
    "heat exhaustion",
    "mosquito bite allergy"
]

# ---------- Mode ----------
mode = st.query_params.get("mode", "tv")

# =====================================================
# SMART TV MODE
# =====================================================
if mode == "tv":

    st.title("🌞 Summer Health AI Learning")

    st.subheader("Scan QR Code for Personalized Health Learning")

    # -------- Random Video --------
    videos = ["enjoy.mp4", "enjoy2.mp4"]
    video_choice = random.choice(videos)

    if os.path.exists(video_choice):
        video_file = open(video_choice, "rb")
        st.video(video_file.read())
    else:
        st.warning("Place enjoy.mp4 and enjoy2.mp4 in the same folder.")

    st.divider()

    # -------- QR Code --------
    if "APP_URL" in st.secrets:
        base_url = st.secrets["APP_URL"]
    else:
        base_url = "http://localhost:8501"

    link = f"{base_url}?mode=learn"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)

    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    st.image(buf.getvalue(), width=350)

    st.markdown("### Possible Health Topics")

    st.write("""
    • Heat rash  
    • Sunburn  
    • Dehydration  
    • Fungal infection  
    • Acne in hot weather  
    • Heat exhaustion  
    • Mosquito bite allergy  
    """)

    st.info("Each student will receive a different personalized topic.")

# =====================================================
# STUDENT MODE
# =====================================================
else:

    st.title("📱 Personalized Summer Health Education")

    # Unique session
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Random topic per student
    if "topic" not in st.session_state:
        st.session_state.topic = random.choice(topics)

    topic = st.session_state.topic

    st.subheader(f"Your Topic Today: {topic}")

    # ---------- Student Inputs ----------
    name = st.text_input("Nickname (optional)")

    sweat = st.selectbox(
        "Do you sweat easily?",
        ["มาก", "ปานกลาง", "น้อย"]
    )

    skin = st.selectbox(
        "Common skin problem",
        ["ไม่มี", "ผื่นคัน", "สิว", "เชื้อรา"]
    )

    outdoor = st.selectbox(
        "Outdoor activity level",
        ["บ่อย", "บางครั้ง", "น้อย"]
    )

    # ---------- AI Advice ----------
    if st.button("Generate AI Health Advice"):

        if client is None:
            st.warning("OpenAI API key not configured")

        else:

            prompt = f"""
You are a university clinic doctor.

Student profile:
Sweat level: {sweat}
Skin problem: {skin}
Outdoor activity: {outdoor}

Health topic: {topic}

Provide short personalized summer health advice for this student.
Avoid recommending antibiotics unless necessary.
"""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            advice = response.choices[0].message.content

            st.success("AI Personalized Advice")

            st.write(advice)

            st.divider()

            tips = [
                "Drink 6–8 glasses of water daily",
                "Shower after exercise",
                "Wear breathable clothing",
                "Avoid unnecessary antibiotic use",
                "Avoid strong sunlight 11:00–15:00",
                "Use sunscreen when outdoors"
            ]

            st.subheader("Extra Summer Tip")

            st.info(random.choice(tips))


