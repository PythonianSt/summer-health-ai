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

st.set_page_config(page_title="AI Campus Health Platform",layout="wide")

VIDEOS=["enjoy.mp4","enjoy2.mp4"]

SCORE_FILE="scores.json"
USER_FILE="users.json"
DATA_FILE="healthdata.json"

topics=[
"ผดร้อน",
"ผิวไหม้แดด",
"ขาดน้ำ",
"เชื้อราผิวหนัง",
"สิวหน้าร้อน",
"ลมแดด",
"แพ้ยุง"
]

quiz_questions=[

("การป้องกันผิวไหม้แดดควรใช้ SPF เท่าไร","30"),
("ควรดื่มน้ำวันละกี่ลิตรในหน้าร้อน","2"),
("ผดร้อนเกิดจากอะไร","เหงื่อ")

]

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
healthdata=load_json(DATA_FILE)

client=None

if "OPENAI_API_KEY" in st.secrets:

    client=OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

mode=st.query_params.get("mode","tv")

# =================================
# TV MODE
# =================================

if mode=="tv":

    st_autorefresh(interval=10000,key="tv")

    st.title("🌞 AI Campus Health Wall")

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

        st.subheader("📱 Join Health Challenge")

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

        st.metric("👥 Students",len(users))

        st.markdown("### 🏆 Top Students")

        top=sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

        for name,score in top:

            st.write(name,score)

        if healthdata:

            st.markdown("### 📊 Skin Problems")

            skins=[v["skin"] for v in healthdata.values()]

            c=Counter(skins)

            for k,v in c.items():

                st.write(k,v)

# =================================
# STUDENT MODE
# =================================

elif mode=="student":

    st.title("📱 AI Health Coach")

    nickname=st.text_input("ชื่อเล่น")

    sweat=st.selectbox("เหงื่อ",["มาก","ปานกลาง","น้อย"])

    skin=st.selectbox("ผิว",["ไม่มี","สิว","ผื่น","เชื้อรา"])

    outdoor=st.selectbox("กิจกรรมกลางแจ้ง",["บ่อย","บางครั้ง","น้อย"])

    topic=random.choice(topics)

    st.subheader("🎯 Topic")

    st.write(topic)

    if st.button("AI Advice"):

        if nickname=="":

            st.warning("กรุณาใส่ชื่อ")

            st.stop()

        users[nickname]=True

        with open(USER_FILE,"w",encoding="utf-8") as f:

            json.dump(users,f)

        if nickname not in scores:

            scores[nickname]=0

        scores[nickname]+=10

        with open(SCORE_FILE,"w",encoding="utf-8") as f:

            json.dump(scores,f)

        healthdata[nickname]={

            "sweat":sweat,
            "skin":skin,
            "outdoor":outdoor

        }

        with open(DATA_FILE,"w",encoding="utf-8") as f:

            json.dump(healthdata,f)

        st.success(f"คะแนน {scores[nickname]}")

        if client:

            prompt=f"""

คุณเป็นแพทย์มหาวิทยาลัย

นักศึกษา
เหงื่อ {sweat}
ผิว {skin}
กิจกรรม {outdoor}

หัวข้อ {topic}

ให้คำแนะนำสุขภาพหน้าร้อน 4 บรรทัด

"""

            res=client.chat.completions.create(

                model="gpt-4.1-mini",

                messages=[{"role":"user","content":prompt}]

            )

            st.write(res.choices[0].message.content)

    st.markdown("## 🎮 Health Quiz")

    q=random.choice(quiz_questions)

    ans=st.text_input(q[0])

    if st.button("Submit Quiz"):

        if ans==q[1]:

            st.success("+5 points")

            scores[nickname]+=5

            with open(SCORE_FILE,"w",encoding="utf-8") as f:

                json.dump(scores,f)

        else:

            st.error("Incorrect")

# =================================
# ADMIN MODE
# =================================

else:

    st.title("📊 Campus Health Dashboard")

    st.metric("Students",len(users))

    st.metric("Total Data",len(healthdata))

    if healthdata:

        skins=[v["skin"] for v in healthdata.values()]

        st.write("Skin problems",Counter(skins))

        sweats=[v["sweat"] for v in healthdata.values()]

        st.write("Sweat pattern",Counter(sweats))












