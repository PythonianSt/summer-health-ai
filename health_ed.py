import streamlit as st
import random
import qrcode
from PIL import Image
import io
import json
import os
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Summer Health AI", layout="wide")

# -----------------------------
# DATABASE FILE
# -----------------------------

DB_FILE="users.json"

def load_data():

    if os.path.exists(DB_FILE):

        with open(DB_FILE,"r") as f:

            try:
                data=json.load(f)
            except:
                data={}

    else:
        data={}

    scores=data.get("scores",{})
    users=data.get("users",[])

    return scores,users


def save_data(scores,users):

    data={
        "scores":scores,
        "users":users
    }

    with open(DB_FILE,"w") as f:
        json.dump(data,f,indent=2)


scores,users=load_data()

# -----------------------------
# HEALTH TOPICS (SKIN)
# -----------------------------

topics=[

"🌞 วิธีป้องกันผิวไหม้แดด (Sunburn)",
"🧴 วิธีใช้ครีมกันแดด SPF ให้ถูกต้อง",
"💧 การดื่มน้ำเพื่อป้องกันผิวแห้ง",
"🧢 วิธีป้องกันฝ้า กระ จากแดด",
"👕 เสื้อผ้าที่เหมาะกับหน้าร้อน",
"🏖 การดูแลผิวหลังว่ายน้ำ",
"🌡 วิธีป้องกันผดร้อน Heat Rash",
"🍉 อาหารที่ช่วยบำรุงผิวหน้าร้อน",
"🚿 การอาบน้ำดูแลผิวหน้าร้อน",
"🌴 วิธีป้องกันผื่นแพ้เหงื่อ"

]

# -----------------------------
# QR CODE
# -----------------------------

def generate_qr(url):

    qr=qrcode.make(url)

    buf=io.BytesIO()

    qr.save(buf,format="PNG")

    buf.seek(0)

    return Image.open(buf)

# -----------------------------
# MODE
# -----------------------------

mode=st.sidebar.selectbox("Mode",["TV","Student"])

# -----------------------------
# TV SCREEN MODE
# -----------------------------

if mode=="TV":

    st_autorefresh(interval=10000,key="tv")

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    col1,col2=st.columns([2,1])

    with col1:

        # VIDEO SWITCH EVERY 30 SEC

        videos=["enjoy.mp4","enjoy2.mp4"]

        t=int(time.time()/30)

        video=videos[t%len(videos)]

        st.video(video, autoplay=True)

    with col2:

        st.subheader("📱 Scan QR เพื่อเรียนรู้สุขภาพ")

        app_url="https://YOUR_STREAMLIT_URL/?mode=Student"

        qr=generate_qr(app_url)

        st.image(qr,width=320)

        st.metric("👥 ผู้เข้าร่วม",len(users))

        st.subheader("🏆 Leaderboard")

        top=sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

        for name,score in top:

            st.write("😀",name,"คะแนน",score)

# -----------------------------
# STUDENT MODE
# -----------------------------

if mode=="Student":

    st.title("🌴 AI การดูแลผิวในหน้าร้อน")

    nickname=st.text_input("ใส่ชื่อเล่นของคุณ")

    if nickname:

        if nickname not in users:

            users.append(nickname)

        if nickname not in scores:

            scores[nickname]=0

        st.success("ยินดีต้อนรับ "+nickname)

        avatar=random.choice(["😎","🌞","🏖","🍉","🌴","🧴"])

        st.header(avatar+" หัวข้อสุขภาพของคุณ")

        topic=random.choice(topics)

        st.write(topic)

        if st.button("ฉันได้เรียนรู้แล้ว"):

            scores[nickname]+=1

            save_data(scores,users)

            st.success("🎉 คุณได้รับ 1 คะแนน")

            st.balloons()

        st.write("🏆 คะแนนของคุณ:",scores.get(nickname,0))









