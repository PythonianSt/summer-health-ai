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
"ผดร้อน","ผิวไหม้แดด","ขาดน้ำ","เชื้อราผิวหนัง","สิวหน้าร้อน",
"ลมแดด","แพ้ยุง","อาหารเป็นพิษ","โรคลมร้อน",
"การดื่มน้ำให้เพียงพอ","การป้องกันไข้แดด",
"การดูแลผิวหลังโดนแดด","อาการเพลียแดด",
"การเลือกครีมกันแดด","การปฐมพยาบาลเมื่อเป็นลมแดด"
]

quiz_questions=[
("การป้องกันผิวไหม้แดดควรใช้ SPF เท่าไร","30"),
("ควรดื่มน้ำวันละกี่ลิตรในหน้าร้อน","2"),
("ผดร้อนเกิดจากอะไร","เหงื่อ"),
("อาการของโรคลมแดดคืออะไร","ตัวร้อนจัดไม่มีเหงื่อ"),
("ควรดื่มน้ำประเภทไหนมากที่สุด","น้ำเปล่า"),
("อาหารประเภทไหนเสียง่าย","อาหารทะเล"),
("อาการอาหารเป็นพิษควรทำอย่างไร","ดื่มเกลือแร่"),
("ครีมกันแดดควรทาซ้ำทุกกี่ชั่วโมง","2"),
("การใส่เสื้อผ้าสีไหนช่วยลดความร้อน","สีขาว"),
("ผักผลไม้ช่วยเพิ่มน้ำในร่างกาย","แตงโม")
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
    }
    </style>
    """,unsafe_allow_html=True)

    cols=st.columns(3)
    clicked=None

    for i in range(6):
        with cols[i%3]:
            if i==st.session_state.game_odd:
                style="animation:spin 1s linear infinite reverse;"
            else:
                style="animation:spin 1s linear infinite;"

            if st.button(" ",key=f"g{i}"):
                clicked=i

            st.markdown(f'<div class="box" style="{style}">🟧</div>',unsafe_allow_html=True)

    if clicked is not None and not st.session_state.game_done:
        rt=int((time.time()-st.session_state.game_start)*1000)

        if clicked==st.session_state.game_odd:
            st.success(f"🎉 ถูกต้อง! ⏱️ {rt} ms")
            bonus=5 if rt<800 else 0
            scores[nickname]+=10+bonus
            if bonus:
                st.info("⚡ เร็วมาก +5 คะแนน")
        else:
            st.error(f"❌ ผิด ⏱️ {rt} ms")

        if nickname not in healthdata:
            healthdata[nickname]={}

        healthdata[nickname]["reaction_time_ms"]=rt
        healthdata[nickname]["timestamp"]=time.time()

        json.dump(scores,open(SCORE_FILE,"w",encoding="utf-8"))
        json.dump(healthdata,open(DATA_FILE,"w",encoding="utf-8"))

        st.session_state.game_done=True

    return st.session_state.get("game_done",False)

# =========================
# TV MODE
# =========================
if mode=="tv":
    st_autorefresh(interval=10000,key="tv")
    st.title("🌞 สนุกกับหน้าร้อนนี้เมื่อสุขภาพของท่านพร้อม")

    col1,col2=st.columns([2,1])

    with col1:
        available=[v for v in VIDEOS if os.path.exists(v)]
        if available:
            video=available[int(time.time()/30)%len(available)]
            st.video(video)

    with col2:
        st.subheader("📱 Join")
        base_url="http://localhost:8501"
        if "APP_URL" in st.secrets:
            base_url=st.secrets["APP_URL"]
        link=f"{base_url}?mode=student"

        qr=qrcode.make(link)
        buf=io.BytesIO()
        qr.save(buf)
        st.image(buf.getvalue())

        st.metric("👥 Students",len(users))

# =========================
# STUDENT MODE
# =========================
elif mode=="student":
    st.title("📱 AI Health Coach")

    nickname=st.text_input("ชื่อเล่น")

    if nickname:
        users[nickname]=True
        json.dump(users,open(USER_FILE,"w",encoding="utf-8"))

    st.markdown("---")
    st.markdown("## 🎮 Quiz + Game")

    if nickname:
        if "qset" not in st.session_state:
            st.session_state.qset=random.sample(quiz_questions,5)
            st.session_state.qidx=0
            st.session_state.done=False

        if not st.session_state.done:
            idx=st.session_state.qidx

            if idx < len(st.session_state.qset)+1:

                # 🎮 GAME LAST
                if idx==len(st.session_state.qset):
                    if spinner_game(nickname):
                        st.session_state.qidx+=1
                        st.rerun()

                else:
                    q,a=st.session_state.qset[idx]
                    st.write(f"Q{idx+1}: {q}")

                    choices=[a,"ไม่รู้","ไม่แน่ใจ","ข้าม"]
                    random.shuffle(choices)

                    ans=st.radio("เลือก:",choices,key=f"q{idx}")

                    if st.button("ตอบ"):
                        if ans==a:
                            st.success("ถูก +5")
                            scores[nickname]=scores.get(nickname,0)+5
                        else:
                            st.error(f"ผิด: {a}")

                        json.dump(scores,open(SCORE_FILE,"w",encoding="utf-8"))

                        st.session_state.qidx+=1
                        st.rerun()

            else:
                st.session_state.done=True

        else:
            st.balloons()
            st.success("🎉 เสร็จแล้ว")

            if st.button("เล่นใหม่"):
                for k in ["qset","qidx","done","game_odd","game_done","game_start"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    if nickname in scores:
        st.sidebar.write(f"คะแนน: {scores[nickname]}")

# =========================
# ADMIN MODE
# =========================
else:
    st.title("📊 Dashboard")

    st.metric("Users",len(users))

    if healthdata:
        st.markdown("### ⏱️ Reaction Time")
        times=[v.get("reaction_time_ms",0) for v in healthdata.values() if "reaction_time_ms" in v]

        if times:
            avg=sum(times)/len(times)
            st.write(f"Average: {int(avg)} ms")

            slow=[t for t in times if t>2000]
            fast=[t for t in times if t<800]

            st.write(f"⚠️ Slow: {len(slow)}")
            st.write(f"⚡ Fast: {len(fast)}")














