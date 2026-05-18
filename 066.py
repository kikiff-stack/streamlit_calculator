import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, date, timedelta
import os  # 파일이 있는지 확인하기 위해 필요합니다.

st.markdown(
    """
    <style>
    .stApp {
        background-color: #FEFEEB; 
    }
    [data-testid="stSidebar"] {
        background-color: #F0FFF0;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFB6C1 !important;
    }
    .stMetric label, .stMetric div {
        color: #FFB6C1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True  
)


# 0. 설정 및 데이터 불러오기
st.set_page_config(page_title="개인 맞춤형 건강-일정 관리기", layout="wide")
SAVE_FILE = "godsaeng_data.csv"

# 세션 상태 초기화 (파일이 있으면 자동으로 불러옴)
if 'tasks' not in st.session_state:
    if os.path.exists(SAVE_FILE):
        try:
            # 파일 읽기
            loaded_df = pd.read_csv(SAVE_FILE)
            # 텍스트로 저장된 리스트를 다시 파이썬 리스트로 변환
            st.session_state.tasks = loaded_df.to_dict('records')
            for t in st.session_state.tasks:
                if isinstance(t['분배'], str):
                    t['분배'] = eval(t['분배'])
        except:
            st.session_state.tasks = []
    else:
        st.session_state.tasks = []

if 'diet_df' not in st.session_state:
    st.session_state.diet_df = pd.DataFrame()

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 이동", ["1. 건강 진단 & 식단", "2. 체중 예측 시뮬레이션", "3. 스마트 일정 분배", "4. 최종 일주일 리포트"])
days = ["월", "화", "수", "목", "금", "토", "일"]


# PAGE 1: 건강 진단 & 식단
if menu == "1. 건강 진단 & 식단":
    st.title("🥗 건강 진단 및 맞춤 식단")
    with st.form("health_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            h = st.number_input("키 (cm)", value=180.0)
            w = st.number_input("현재 체중 (kg)", value=100.0)
        with c2:
            a = st.number_input("나이", value=30)
            intensity = st.select_slider("운동 강도", options=["저강도", "중강도", "고강도"])
        with c3:
            p = st.number_input("목표 기간 (주)", min_value=1, value=4)
        submit_health = st.form_submit_button("진단 및 식단 생성")

    if submit_health:
        # 1. BMI 지수 계산 ($체중 / 키(m)^2$)
        bmi = w / ((h / 100) ** 2)
        
        # 2. BMI 판정 로직
        if bmi < 18.5:
            bmi_result = "저체중"
            bmi_color = "blue"
        elif 18.5 <= bmi < 23:
            bmi_result = "정상"
            bmi_color = "green"
        elif 23 <= bmi < 25:
            bmi_result = "과체중"
            bmi_color = "orange"
        else:
            bmi_result = "비만"
            bmi_color = "red"

        # 3. 하루 권장 칼로리 계산
        # 기초대사량(BMR) 계산
        base_bmr = (10 * w) + (6.25 * h) - (5 * a) + 5
        # 활동 계수 적용
        activity_multiplier = {"저강도": 1.2, "중강도": 1.5, "고강도": 1.8}
        recommend_kcal = int(base_bmr * activity_multiplier[intensity])
        
        # 세션 상태에 저장
        st.session_state.weight = w
        st.session_state.user_bmi = bmi
        st.session_state.user_kcal = recommend_kcal

        # 4. 결과 출력 (Metric 사용)
        st.divider()
        st.subheader("📊 나의 건강 분석 결과")
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.metric("나의 BMI 지수", f"{bmi:.1f}")
            st.write(f"현재 사용자님은 **:{bmi_color}[{bmi_result}]** 상태입니다.")
            
        with col_res2:
            st.metric("하루 권장 칼로리", f"{recommend_kcal} kcal")
            st.write(f"목표 달성을 위해 하루에 **{recommend_kcal} kcal** 섭취를 권장합니다.")

        # 5. 랜덤 식단 생성 
        menu_pool = [
            "닭가슴살 샐러드 & 견과류", "훈제오리 월남쌈", "두부 스테이크 & 구운 채소", 
            "연어 파피요트", "통밀 샌드위치 & 저지방 우유", "현미 비빔밥 (나물 위주)", 
            "소고기 샤브샤브", "그릭 요거트 & 그래놀라 볼", "곤약 떡볶이 & 삶은 달걀",
            "고등어 구이 & 잡곡밥", "버섯 들깨탕", "아보카도 명란 비빔밥",
            "닭안심 장조림 & 쌈채소", "오징어 숙회 & 미역줄기볶음", "연두부 샐러드 & 바나나"
        ]
        
        selected_menus = random.sample(menu_pool, 7)
        
        st.session_state.diet_df = pd.DataFrame({
            "요일": days,
            "추천 식단": selected_menus,
            "음식 칼로리": [f"{recommend_kcal + random.randint(-100, 100)}kcal" for _ in range(7)],
            "운동 소모": [f"{random.randint(300, 600)}kcal" if i < 6 else "휴식" for i in range(7)]
        })
        
        st.divider()
        st.subheader("🗓️ 나만의 일주일 식단표")
        st.table(st.session_state.diet_df)

# PAGE 2: 체중 예측
elif menu == "2. 체중 예측 시뮬레이션":
    st.title("📉 체중 변화 예측")
    current_w = st.session_state.get('weight', 100.0)
    target_w = st.number_input("목표 체중 (kg)", value=current_w - 5.0)
    target_period = st.number_input("감량 기간 (주)", min_value=1, value=8)
    
    total_days = target_period * 7
    x = np.arange(total_days)
    y = current_w - (current_w - target_w) * (x / total_days)
    st.line_chart(pd.DataFrame({"일수": x, "예상체중": y}).set_index("일수"))

# PAGE 3: 스마트 일정 분배
elif menu == "3. 스마트 일정 분배":
    st.title("📅 AI 스케줄 분배기")
    with st.form("task_form"):
        t_name = st.text_input("일의 종류 (제목)")
        t_due = st.date_input("마감 기한", value=date.today() + timedelta(days=7))
        t_amount = st.slider("일의 양 (1~10)", 1, 10, 5)
        submit_task = st.form_submit_button("일정 등록 및 분배")

    if submit_task:
        dist = []
        rem = t_amount
        for d in days:
            if rem > 0:
                take = min(rem, 2)
                dist.append(f"{t_name}({take})")
                rem -= take
            else:
                dist.append("-")
        st.session_state.tasks.append({"이름": t_name, "분배": dist})
        st.success(f"'{t_name}' 일정이 추가되었습니다")

    if st.session_state.tasks:
        st.table(pd.DataFrame([t['분배'] for t in st.session_state.tasks], columns=days))

# PAGE 4: 최종 리포트 

elif menu == "4. 최종 일주일 리포트":
    st.title("📋 이번 주 건강 및 일정관리 종합 리포트")
    
    if not st.session_state.diet_df.empty and st.session_state.tasks:
        final_df = st.session_state.diet_df.copy()
        weekly_tasks = []
        for i in range(7):
            day_t = [t['분배'][i] for t in st.session_state.tasks if t['분배'][i] != "-"]
            weekly_tasks.append(", ".join(day_t) if day_t else "개인 정비")
        final_df["오늘의 할 일"] = weekly_tasks
        
        st.dataframe(final_df, use_container_width=True)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 데이터 파일로 저장하기"):
                pd.DataFrame(st.session_state.tasks).to_csv(SAVE_FILE, index=False)
                st.success("컴퓨터에 데이터가 저장되었습니다. 다시 접속해도 유지됩니다!")
        with col2:
            if st.button("🧹 데이터 초기화"):
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                st.session_state.tasks = []
                st.warning("저장된 파일과 데이터가 모두 삭제되었습니다.")
                st.rerun()
    else:
        st.warning("데이터를 먼저 입력해 주세요!")
