import streamlit as st
import random
import os
import json
import qrcode
import io
import base64
import time
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="AI Health Wall",layout="wide")

VIDEOS=["enjoy.mp4","enjoy2.mp4"]

SCORE_FILE="scores.json"
USER_FILE="users.json"

topics=[

"ผดร้อน",
"ผิวไหม้แดด",
"ขาดน้ำ",
"เชื้อราผิวหนัง",
"สิวหน้าร้อน",
"ลมแดด",
"แพ้ยุง",
"ตะคริวจากการเสียเหงื่อ",
"ผิวแห้งจากแดด",
"การป้องกัน Heat Stroke"

]

# =========================
# QUIZ DATABASE
# =========================

quiz_db={

"Heat Stroke":{

"question":"อาการใดเป็นสัญญาณอันตรายของ Heat Stroke",

"options":[

"เหงื่อออกมาก",

"ตัวร้อน >40°C และสับสน",

"ปวดเมื่อยกล้ามเนื้อ",

"ง่วงนอน"

],

"answer":"ตัวร้อน >40°C และสับสน",

"score":10,

"ref":"WHO Heat and Health Guidelines"

},

"Dehydration":{

"question":"วิธีป้องกันภาวะขาดน้ำที่ดีที่สุดคืออะไร",

"options":[

"ดื่มน้ำเฉพาะเวลาหิว",

"ดื่มน้ำสม่ำเสมอ",

"ดื่มกาแฟ",

"ดื่มน้ำอัดลม"

],

"answer":"ดื่มน้ำสม่ำเสมอ",

"score":8,

"ref":"CDC Hydration Guidance"

},

"Sunburn":{

"question":"ค่า SPF ที่แนะนำสำหรับการป้องกันแดดคือเท่าใด",

"options":[

"SPF 10",

"SPF 15",

"SPF 30 ขึ้นไป",

"ไม่จำเป็น"

],

"answer":"SPF 30 ขึ้นไป",

"score":6,

"ref":"American Academy of Dermatology"

},

"Mosquito":{

"question":"โรคใดมียุงเป็นพาหะ",

"options":[

"ไข้เลือดออก",

"ไข้หวัด",

"วัณโรค",

"COVID"

],

"answer":"ไข้เลือดออก",

"score":5,

"ref":"WHO Dengue Control"

}

}

# =========================

def load_json(file):

    if os.path.exists(file):

        try:

            with open(file,"r",encoding="utf-8") as f:

                return json.load(f)

        except:

            return {}

    return {}

scores=load_json(SCORE_FILE)
users=load_json(USER_FILE)

client=None

if "OPENAI_API_KEY" in st.secrets:

    client=OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

mode=st.query_params.get("mode","tv")

# =========================================
# TV MODE
# =========================================

if mode=="tv":

    st_autorefresh(interval=10000,key="tv")

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    col1,col2=st.columns([2,1])

    with col1:

        available=[v for v in VIDEOS if os.path.exists(v)]

        if available:

            video=available[int(time.time()/30)%len(available)]

            with open(video,"rb") as f:

                video_bytes=f.read()

            video_base64=base64.b64encode(video_bytes).decode()

            video_html=f"""

            <video autoplay muted loop playsinline width="900">

            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">

            </video>

            """

            st.markdown(video_html,unsafe_allow_html=True)

    with col2:

        st.subheader("📱 Scan QR เพื่อเรียนรู้สุขภาพ")

        base_url="http://localhost:8501"

        if "APP_URL" in st.secrets:

            base_url=st.secrets["APP_URL"]

        link=f"{base_url}?mode=student"

        qr=qrcode.QRCode(box_size=8,border=2)

        qr.add_data(link)

        qr.make()

        img=qr.make_image()

        buf=io.BytesIO()

        img.save(buf)

        st.image(buf.getvalue(),width=220)

        st.metric("👥 ผู้เข้าร่วม",len(users))

        st.markdown("### 🏆 Leaderboard")

        top=sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

        for name,score in top:

            st.write(f"👤 {name} : {score}")

# =========================================
# STUDENT MODE
# =========================================

else:

    st.title("📱 AI สุขภาพหน้าร้อนสำหรับนักศึกษา")

    nickname=st.text_input("ชื่อเล่น")

    sweat=st.selectbox("💦 เหงื่อออก",["มาก","ปานกลาง","น้อย"])

    skin=st.selectbox("🧴 ปัญหาผิว",["ไม่มี","สิว","ผื่น","เชื้อรา"])

    outdoor=st.selectbox("🏃 กิจกรรมกลางแจ้ง",["บ่อย","บางครั้ง","น้อย"])

    if "topic" not in st.session_state:

        st.session_state.topic=random.choice(topics)

    topic=st.session_state.topic

    st.subheader(f"🎯 หัวข้อของคุณ : {topic}")

    if st.button("รับคำแนะนำจาก AI"):

        if nickname=="":

            st.warning("กรุณาใส่ชื่อเล่น")

            st.stop()

        users[nickname]=True

        with open(USER_FILE,"w",encoding="utf-8") as f:

            json.dump(users,f)

        if nickname not in scores:

            scores[nickname]=0

        scores[nickname]+=10

        with open(SCORE_FILE,"w",encoding="utf-8") as f:

            json.dump(scores,f)

        st.success(f"คะแนนสะสม {scores[nickname]}")

        if client:

            prompt=f"""

คุณเป็นแพทย์มหาวิทยาลัย

ข้อมูลนักศึกษา

เหงื่อ {sweat}
ผิว {skin}
กิจกรรม {outdoor}

หัวข้อ {topic}

ให้คำแนะนำสุขภาพหน้าร้อน
สั้นๆ 4 บรรทัด
ภาษาไทยง่าย

"""

            res=client.chat.completions.create(

                model="gpt-4.1-mini",

                messages=[{"role":"user","content":prompt}]

            )

            advice=res.choices[0].message.content

            st.markdown("### 🧠 AI แนะนำ")

            st.write(advice)

    # =========================
    # QUIZ SECTION
    # =========================

    st.markdown("---")
    st.subheader("🧠 Health Quiz")

    quiz_topic=st.selectbox("เลือกหัวข้อ Quiz",list(quiz_db.keys()))

    q=quiz_db[quiz_topic]

    answer=st.radio(q["question"],q["options"])

    if st.button("ส่งคำตอบ"):

        if answer==q["answer"]:

            st.success("✅ ถูกต้อง!")

            scores[nickname]+=q["score"]

            st.write(f"+{q['score']} คะแนน")

        else:

            st.error("❌ ตอบไม่ถูก")

            st.info(f"เฉลย: {q['answer']}")

        st.write("📚 Reference:",q["ref"])

        with open(SCORE_FILE,"w",encoding="utf-8") as f:

            json.dump(scores,f)

        st.write("คะแนนรวม:",scores[nickname])














