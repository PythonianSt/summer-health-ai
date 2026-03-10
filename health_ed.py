import streamlit as st
import uuid
import qrcode
from PIL import Image
import random
from openai import OpenAI

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Summer Health AI Learning",
    layout="wide"
)

# ---------- OPENAI ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- HEALTH TOPICS ----------
topics = [
    "heat rash",
    "sunburn",
    "dehydration",
    "fungal skin infection",
    "acne in hot weather",
    "heat exhaustion",
    "mosquito bite allergy"
]

# ---------- MODE SELECT ----------
query = st.query_params
mode = query.get("mode", "tv")

# ======================================
# TV MODE (SMART TV DISPLAY)
# ======================================
if mode == "tv":

    st.title("🌞 Summer Health AI Learning")

    st.markdown("### Scan QR Code เพื่อเรียนรู้การดูแลสุขภาพหน้าร้อนแบบเฉพาะบุคคล")

    base_url = st.secrets["APP_URL"]
    link = f"{base_url}?mode=learn"

    import qrcode
    import io

    base_url = st.secrets["APP_URL"]
    link = f"{base_url}?mode=learn"

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # convert to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    st.image(buf.getvalue(), width=350)

    st.markdown("---")

    st.markdown(
    """
    นักศึกษาสามารถเรียนรู้เรื่อง

    • ผดร้อน  
    • ผื่นเชื้อรา  
    • ผิวไหม้แดด  
    • การขาดน้ำ  

    ระบบ AI จะให้คำแนะนำ **ไม่เหมือนกันในแต่ละคน**
    """
    )

    st.info("Scan QR ด้วยมือถือเพื่อเริ่มเรียนรู้")

# ======================================
# STUDENT MODE
# ======================================
else:

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    st.title("📱 Personalized Summer Health Education")

    st.write("Session:", st.session_state.session_id)

    name = st.text_input("ชื่อเล่น (optional)")

    sweat = st.selectbox(
        "คุณเหงื่อออกง่ายหรือไม่",
        ["มาก", "ปานกลาง", "น้อย"]
    )

    skin = st.selectbox(
        "ปัญหาผิวที่พบบ่อย",
        ["ไม่มี", "ผื่นคัน", "สิว", "เชื้อรา"]
    )

    outdoor = st.selectbox(
        "ทำกิจกรรมกลางแจ้ง",
        ["บ่อย", "บางครั้ง", "น้อย"]
    )

    if st.button("Generate AI Health Advice"):

        topic = random.choice(topics)

        prompt = f"""
        You are a university clinic doctor.

        Student profile:
        sweat: {sweat}
        skin problem: {skin}
        outdoor activity: {outdoor}

        Topic: {topic}

        Give short personalized summer health advice for students.
        Avoid recommending antibiotics unless necessary.
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role":"user","content":prompt}
            ]
        )

        advice = response.choices[0].message.content

        st.success("AI Personalized Advice")

        st.write(advice)

        st.markdown("---")

        st.subheader("Summer Self-Care Tips")

        tips = [
            "ดื่มน้ำวันละ 6-8 แก้ว",
            "อาบน้ำหลังออกกำลังกาย",
            "ใส่เสื้อผ้าระบายอากาศ",
            "หลีกเลี่ยงการใช้ยาปฏิชีวนะเอง"
        ]

        st.write(random.choice(tips))

