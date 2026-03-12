import streamlit as st
import random
import qrcode
from PIL import Image
import io
import json
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Summer Health AI", layout="wide")

# -----------------------
# DATABASE FILE
# -----------------------
USER_FILE="users.json"

if os.path.exists(USER_FILE):
    with open(USER_FILE,"r") as f:
        data=json.load(f)
else:
    data={"scores":{},"users":[]}

scores=data["scores"]
users=data["users"]

# -----------------------
# HEALTH TOPICS
# -----------------------

topics=[

"🌞 การป้องกันผิวไหม้แดด (Sunburn)",
"🧴 วิธีใช้ครีมกันแดดให้ถูกต้อง",
"💧 การดื่มน้ำเพื่อป้องกันผิวแห้ง",
"🧢 การป้องกันฝ้า กระ จากแดด",
"👕 เสื้อผ้าที่เหมาะกับหน้าร้อน",
"🌴 การดูแลผิวหลังว่ายน้ำ",
"🏖 วิธีป้องกันผื่นจากเหงื่อ",
"🌡 การป้องกัน Heat Rash",
"🍉 อาหารที่ช่วยบำรุงผิวในหน้าร้อน",
"🚿 การอาบน้ำดูแลผิวในหน้าร้อน"

]

# -----------------------
# QR GENERATOR
# -----------------------

def make_qr(url):

    qr=qrcode.make(url)
    buf=io.BytesIO()
    qr.save(buf,format="PNG")
    buf.seek(0)

    return Image.open(buf)


# -----------------------
# MODE
# -----------------------

mode=st.sidebar.selectbox("Mode",["TV","Student"])

# -----------------------
# TV SCREEN MODE
# -----------------------

if mode=="TV":

    st_autorefresh(interval=10000,key="tv")

    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    col1,col2=st.columns([2,1])

    # RANDOM VIDEO
    video=random.choice(["enjoy.mp4","enjoy2.mp4"])

    with col1:

        st.video(video, autoplay=True)

    with col2:

        st.subheader("📱 Scan QR เพื่อร่วมกิจกรรม")

        url="https://YOUR_STREAMLIT_APP_URL/?mode=student"

        qr=make_qr(url)

        st.image(qr,width=300)

        st.metric("👥 ผู้เข้าร่วม",len(users))

        st.subheader("🏆 Leaderboard")

        top=sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

        for name,score in top:

            st.write("😀",name,"คะแนน",score)

# -----------------------
# STUDENT MODE
# -----------------------

if mode=="Student":

    st.title("🌴 AI สุขภาพหน้าร้อน")

    nickname=st.text_input("ใส่ชื่อเล่น")

    if nickname:

        if nickname not in users:
            users.append(nickname)

        if nickname not in scores:
            scores[nickname]=0

        st.success("ยินดีต้อนรับ "+nickname)

        avatar=random.choice(["😎","🌞","🏖","🍉","🌴"])

        st.header(avatar+" หัวข้อของคุณ")

        topic=random.choice(topics)

        st.write(topic)

        if st.button("ฉันได้เรียนรู้แล้ว"):

            scores[nickname]+=1

            st.success("🎉 ได้รับ 1 คะแนน")

            data={"scores":scores,"users":users}

            with open(USER_FILE,"w") as f:
                json.dump(data,f)

            st.balloons()

    st.write("🏆 คะแนนของคุณ:",scores.get(nickname,0))










