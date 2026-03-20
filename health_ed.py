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

# Expanded topics including more summer health issues
topics=[
"ผดร้อน",  # Heat rash
"ผิวไหม้แดด",  # Sunburn
"ขาดน้ำ",  # Dehydration
"เชื้อราผิวหนัง",  # Skin fungus
"สิวหน้าร้อน",  # Summer acne
"ลมแดด",  # Heat stroke
"แพ้ยุง",  # Mosquito allergy
"อาหารเป็นพิษ",  # Food poisoning
"โรคลมร้อน",  # Heat exhaustion
"การดื่มน้ำให้เพียงพอ",  # Hydration
"การป้องกันไข้แดด",  # Sunstroke prevention
"การดูแลผิวหลังโดนแดด",  # Post-sun skin care
"อาการเพลียแดด",  # Heat fatigue
"การเลือกครีมกันแดด",  # Sunscreen selection
"การปฐมพยาบาลเมื่อเป็นลมแดด"  # First aid for heat stroke
]

# Expanded quiz questions with more variety
quiz_questions=[

("การป้องกันผิวไหม้แดดควรใช้ SPF เท่าไร","30"),
("ควรดื่มน้ำวันละกี่ลิตรในหน้าร้อน","2"),
("ผดร้อนเกิดจากอะไร","เหงื่อ"),
("อาการของโรคลมแดด (Heat Stroke) คืออะไร","ตัวร้อนจัดไม่มีเหงื่อ"),
("ควรดื่มน้ำประเภทไหนมากที่สุดในหน้าร้อน","น้ำเปล่า"),
("อาหารประเภทไหนเสียง่ายในหน้าร้อน","อาหารทะเล"),
("อาการอาหารเป็นพิษควรทำอย่างไร","ดื่มเกลือแร่"),
("ครีมกันแดดควรทาซ้ำทุกกี่ชั่วโมง","2"),
("การใส่เสื้อผ้าสีไหนช่วยลดความร้อน","สีขาว"),
("ผักผลไม้ชนิดไหนช่วยเพิ่มความชุ่มชื้น","แตงโม"),
("เวลาที่ไม่ควรทำกิจกรรมกลางแจ้งหนักๆ","เที่ยงถึงบ่ายโมง"),
("สัญญาณอันตรายของร่างกายที่ขาดน้ำ","ปัสสาวะสีเข้ม"),
("ควรอาบน้ำกี่ครั้งในหน้าร้อน","2 ครั้ง"),
("ผื่นร้อนควรทาอะไร","แป้งเย็น"),
("การปฐมพยาบาลผู้เป็นลมแดดเบื้องต้น","เช็ดตัวด้วยน้ำเย็น")

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

# Store quiz questions per user session
if 'user_questions' not in st.session_state:
    st.session_state.user_questions = {}

# =================================
# TV MODE
# =================================

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
            st.write(f"**{name}** : {score} คะแนน")

        if healthdata:
            st.markdown("### 📊 Skin Problems")
            skins=[v["skin"] for v in healthdata.values()]
            c=Counter(skins)
            for k,v in c.items():
                st.write(f"{k}: {v}")

# =================================
# STUDENT MODE
# =================================

elif mode=="student":
    st.title("📱 AI Health Coach - หน้าร้อนนี้ปลอดภัยด้วย AI")

    # Initialize session state for user-specific questions
    if 'user_initialized' not in st.session_state:
        st.session_state.user_initialized = False
        st.session_state.current_nickname = ""
        st.session_state.quiz_questions = []
        st.session_state.current_question_index = 0
        st.session_state.quiz_answers = {}
        st.session_state.quiz_completed = False

    nickname=st.text_input("ชื่อเล่น (Nickname)", key="nickname_input")

    if nickname and nickname != st.session_state.current_nickname:
        # New user, generate unique quiz questions for them
        st.session_state.current_nickname = nickname
        st.session_state.quiz_questions = random.sample(quiz_questions, min(5, len(quiz_questions)))  # 5 random questions
        st.session_state.current_question_index = 0
        st.session_state.quiz_answers = {}
        st.session_state.quiz_completed = False
        st.session_state.user_initialized = True
        
        # Store in session state user questions
        st.session_state.user_questions[nickname] = {
            'questions': st.session_state.quiz_questions,
            'answers': {}
        }

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💬 บอกเราหน่อย")
        sweat=st.selectbox("เหงื่อออก", ["มาก", "ปานกลาง", "น้อย"])
        skin=st.selectbox("ปัญหาผิว", ["ไม่มี", "สิว", "ผื่น", "เชื้อรา", "ผิวแห้ง", "ผิวไหม้"])
        outdoor=st.selectbox("ทำกิจกรรมกลางแจ้ง", ["บ่อย", "บางครั้ง", "น้อย"])

    with col2:
        st.markdown("### 🎯 หัวข้อวันนี้")
        topic = random.choice(topics)
        st.info(f"**{topic}**")
        
        # Add health tips based on topic
        if topic == "อาหารเป็นพิษ":
            st.caption("💡 ควรกินร้อน ช้อนกลาง ล้างมือ")
        elif topic == "ลมแดด":
            st.caption("💡 ดื่มน้ำบ่อยๆ หลีกเลี่ยงกลางแจ้งช่วงเที่ยง")
        elif topic == "ขาดน้ำ":
            st.caption("💡 ดื่มน้ำอย่างน้อยวันละ 8-10 แก้ว")

    # AI Advice Button
    if st.button("🤖 ขอคำแนะนำจาก AI", use_container_width=True):
        if nickname == "":
            st.warning("กรุณาใส่ชื่อเล่น")
            st.stop()

        # Update user data
        users[nickname] = True
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f)

        if nickname not in scores:
            scores[nickname] = 0
        scores[nickname] += 10
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f)

        healthdata[nickname] = {
            "sweat": sweat,
            "skin": skin,
            "outdoor": outdoor,
            "timestamp": time.time()
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(healthdata, f)

        st.success(f"✅ ได้รับ 10 คะแนน รวมคะแนน {scores[nickname]}")

        if client:
            prompt = f"""
คุณเป็นแพทย์มหาวิทยาลัย ให้คำแนะนำสุขภาพนักศึกษาในหน้าร้อน

ข้อมูลนักศึกษา:
- เหงื่อ: {sweat}
- ปัญหาผิว: {skin}
- กิจกรรมกลางแจ้ง: {outdoor}

หัวข้อที่สนใจ: {topic}

ให้คำแนะนำสั้นๆ กระชับ 4-5 บรรทัด เป็นภาษาไทย เป็นมิตร น่ารัก
"""
            try:
                res = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 💡 คำแนะนำจาก AI")
                st.success(res.choices[0].message.content)
            except:
                st.info("⚠️ ไม่สามารถเชื่อมต่อ AI ได้ แต่คุณยังได้คะแนนนะ")

    # Quiz Section
    st.markdown("---")
    st.markdown("## 🎮 Health Quiz - ทดสอบความรู้หน้าร้อน")
    
    if nickname and st.session_state.user_initialized and nickname in st.session_state.user_questions:
        questions = st.session_state.user_questions[nickname]['questions']
        
        if not st.session_state.quiz_completed:
            # Show current question
            current_idx = st.session_state.current_question_index
            
            if current_idx < len(questions):
                q_text, correct_ans = questions[current_idx]
                
                st.markdown(f"**คำถามข้อ {current_idx + 1}/{len(questions)}**")
                st.markdown(f"❓ {q_text}")
                
                # Multiple choice answers (randomized)
                if f'answers_{current_idx}' not in st.session_state:
                    # Create multiple choice options
                    wrong_answers = ["ไม่ทราบ", "ไม่แน่ใจ", "ต้องค้นคว้า", "ขอผ่าน"]
                    options = [correct_ans] + random.sample(wrong_answers, 3)
                    random.shuffle(options)
                    st.session_state[f'answers_{current_idx}'] = options
                
                options = st.session_state[f'answers_{current_idx}']
                answer = st.radio("เลือกคำตอบ:", options, key=f"quiz_{current_idx}")
                
                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    if st.button("✅ ส่งคำตอบ", key=f"submit_{current_idx}"):
                        if answer == correct_ans:
                            st.success("🎉 ถูกต้อง! +5 คะแนน")
                            scores[nickname] += 5
                            with open(SCORE_FILE, "w", encoding="utf-8") as f:
                                json.dump(scores, f)
                            st.session_state.quiz_answers[current_idx] = True
                        else:
                            st.error(f"❌ ไม่ถูกต้อง คำตอบที่ถูกคือ: {correct_ans}")
                            st.session_state.quiz_answers[current_idx] = False
                        
                        # Move to next question
                        if current_idx + 1 < len(questions):
                            st.session_state.current_question_index += 1
                            st.rerun()
                        else:
                            st.session_state.quiz_completed = True
                            st.rerun()
                
                with col2:
                    if st.button("⏭️ ข้าม", key=f"skip_{current_idx}"):
                        if current_idx + 1 < len(questions):
                            st.session_state.current_question_index += 1
                            st.rerun()
                        else:
                            st.session_state.quiz_completed = True
                            st.rerun()
            else:
                st.session_state.quiz_completed = True
        else:
            # Quiz completed
            correct_count = sum(1 for v in st.session_state.quiz_answers.values() if v)
            st.balloons()
            st.success(f"🎉 ทำแบบทดสอบเสร็จ! ได้คะแนน {correct_count * 5} จาก {len(questions) * 5} คะแนน")
            
            if st.button("🔄 ทำแบบทดสอบใหม่"):
                # Generate new set of questions
                st.session_state.quiz_questions = random.sample(quiz_questions, min(5, len(quiz_questions)))
                st.session_state.current_question_index = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_completed = False
                st.rerun()
    else:
        st.info("👆 กรุณากรอกชื่อเล่นเพื่อเริ่มทำแบบทดสอบ")

    # Show current score
    if nickname in scores:
        st.sidebar.markdown(f"### 🏅 คะแนนของคุณ: {scores[nickname]}")

# =================================
# ADMIN MODE
# =================================

else:
    st.title("📊 Campus Health Dashboard - ข้อมูลสุขภาพนักศึกษา")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 นักศึกษาทั้งหมด", len(users))
    with col2:
        st.metric("📝 ข้อมูลสุขภาพ", len(healthdata))
    with col3:
        total_score = sum(scores.values()) if scores else 0
        st.metric("🏆 คะแนนรวม", total_score)

    if healthdata:
        st.markdown("### 📊 สถิติปัญหาผิว")
        skins = [v["skin"] for v in healthdata.values()]
        skin_stats = Counter(skins)
        for problem, count in skin_stats.items():
            percentage = (count / len(healthdata)) * 100
            st.write(f"**{problem}**: {count} คน ({percentage:.1f}%)")

        st.markdown("### 💦 สถิติการเหงื่อออก")
        sweats = [v["sweat"] for v in healthdata.values()]
        sweat_stats = Counter(sweats)
        for level, count in sweat_stats.items():
            percentage = (count / len(healthdata)) * 100
            st.write(f"**{level}**: {count} คน ({percentage:.1f}%)")

        st.markdown("### ☀️ สถิติกิจกรรมกลางแจ้ง")
        outdoors = [v["outdoor"] for v in healthdata.values()]
        outdoor_stats = Counter(outdoors)
        for freq, count in outdoor_stats.items():
            percentage = (count / len(healthdata)) * 100
            st.write(f"**{freq}**: {count} คน ({percentage:.1f}%)")

        st.markdown("### 🏆 อันดับคะแนนสูงสุด")
        top_students = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (name, score) in enumerate(top_students, 1):
            st.write(f"{i}. **{name}** - {score} คะแนน")














