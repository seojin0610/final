import streamlit as st
import pandas as pd
import requests

# -----------------------------------------------------------------------------
# 1. 페이지 레이아웃 및 CSS 커스텀 스타일 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="글로벌 맞춤형 재생에너지 추천 시스템",
    page_icon="🌱",
    layout="wide"
)

# 시각적 강조를 위한 커스텀 CSS 적용
# - 추천 목록 글씨체 대폭 확대 (제목 24px, 설명 17px)
# - 파란색/녹색 계열 시각적 카드 및 제언 카드 디자인
st.markdown("""
    <style>
    /* 지도 영역 높이 조절 */
    .stMap {
        margin-bottom: 25px;
    }
    
    /* 추천 재생에너지 카드 (파란색/녹색 계열 그라데이션) */
    .recommend-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%);
        border-left: 6px solid #0284c7;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }
    .recommend-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #0369a1 !important;
        margin-bottom: 10px !important;
    }
    .recommend-desc {
        font-size: 17px !important;
        color: #1e293b !important;
        line-height: 1.6 !important;
    }

    /* 1줄 요약 제언 카드 디자인 */
    .proposal-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .proposal-icon {
        font-size: 28px;
        margin-bottom: 6px;
    }
    .proposal-title {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
    }
    .proposal-text {
        font-size: 15px;
        color: #334155;
        font-weight: 500;
        line-height: 1.4;
    }

    /* 출처 하이퍼링크 박스 */
    .source-box {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 30px;
        font-size: 14px;
        color: #475569;
    }
    .source-box a {
        color: #2563eb;
        text-decoration: none;
        font-weight: bold;
    }
    .source-box a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 전 세계 대륙별/국가별 80개 이상 세부 지역 데이터베이스
# -----------------------------------------------------------------------------
LOCATION_DATA = {
    "아시아": {
        "대한민국 - 서울": {"lat": 37.5665, "lon": 126.9780, "geothermal": False, "coastal": False},
        "대한민국 - 제주": {"lat": 33.4996, "lon": 126.5312, "geothermal": False, "coastal": True},
        "대한민국 - 부산": {"lat": 35.1796, "lon": 129.0756, "geothermal": False, "coastal": True},
        "대한민국 - 포항": {"lat": 36.0190, "lon": 129.3435, "geothermal": True, "coastal": True},
        "일본 - 도쿄": {"lat": 35.6762, "lon": 139.6503, "geothermal": True, "coastal": True},
        "일본 - 삿포로": {"lat": 43.0618, "lon": 141.3545, "geothermal": True, "coastal": False},
        "일본 - 벳푸": {"lat": 33.2846, "lon": 131.4912, "geothermal": True, "coastal": True},
        "중국 - 베이징": {"lat": 39.9042, "lon": 116.4074, "geothermal": False, "coastal": False},
        "중국 - 상하이": {"lat": 31.2304, "lon": 121.4737, "geothermal": False, "coastal": True},
        "중국 - 라싸(티베트)": {"lat": 29.6524, "lon": 91.1721, "geothermal": True, "coastal": False},
        "중국 - 우루무치": {"lat": 43.8256, "lon": 87.6168, "geothermal": False, "coastal": False},
        "인도 - 뉴델리": {"lat": 28.6139, "lon": 77.2090, "geothermal": False, "coastal": False},
        "인도 - 뭄바이": {"lat": 19.0760, "lon": 72.8777, "geothermal": False, "coastal": True},
        "인도 - 자이살메르": {"lat": 26.9157, "lon": 70.9083, "geothermal": False, "coastal": False},
        "인도네시아 - 자카르타": {"lat": -6.2088, "lon": 106.8456, "geothermal": True, "coastal": True},
        "인도네시아 - 반둥": {"lat": -6.9175, "lon": 107.6191, "geothermal": True, "coastal": False},
        "베트남 - 하노이": {"lat": 21.0285, "lon": 105.8542, "geothermal": False, "coastal": False},
        "베트남 - 다낭": {"lat": 16.0544, "lon": 108.2022, "geothermal": False, "coastal": True},
        "태국 - 방콕": {"lat": 13.7563, "lon": 100.5018, "geothermal": False, "coastal": True},
        "필리핀 - 마닐라": {"lat": 14.5995, "lon": 120.9842, "geothermal": True, "coastal": True},
        "필리핀 - 티위": {"lat": 13.4583, "lon": 123.6822, "geothermal": True, "coastal": True},
        "사우디아라비아 - 리야드": {"lat": 24.7136, "lon": 46.6753, "geothermal": False, "coastal": False},
        "UAE - 두바이": {"lat": 25.2048, "lon": 55.2708, "geothermal": False, "coastal": True},
        "터키 - 이스탄불": {"lat": 41.0082, "lon": 28.9784, "geothermal": True, "coastal": True},
        "터키 - 이즈미르": {"lat": 38.4237, "lon": 27.1428, "geothermal": True, "coastal": True},
    },
    "유럽": {
        "영국 - 런던": {"lat": 51.5074, "lon": -0.1278, "geothermal": False, "coastal": True},
        "영국 - 에든버러": {"lat": 55.9533, "lon": -3.1883, "geothermal": False, "coastal": True},
        "독일 - 베를린": {"lat": 52.5200, "lon": 13.4050, "geothermal": False, "coastal": False},
        "독일 - 함부르크": {"lat": 53.5511, "lon": 9.9937, "geothermal": False, "coastal": True},
        "프랑스 - 파리": {"lat": 48.8566, "lon": 2.3522, "geothermal": False, "coastal": False},
        "프랑스 - 마르세유": {"lat": 43.2965, "lon": 5.3698, "geothermal": False, "coastal": True},
        "아이슬란드 - 레이캬비크": {"lat": 64.1466, "lon": -21.9426, "geothermal": True, "coastal": True},
        "스페인 - 마드리드": {"lat": 40.4168, "lon": -3.7038, "geothermal": False, "coastal": False},
        "스페인 - 세비야": {"lat": 37.3891, "lon": -5.9845, "geothermal": False, "coastal": False},
        "이탈리아 - 로마": {"lat": 41.9028, "lon": 12.4964, "geothermal": True, "coastal": True},
        "이탈리아 - 라르데렐로": {"lat": 43.2389, "lon": 10.8672, "geothermal": True, "coastal": False},
        "그리스 - 아테네": {"lat": 37.9838, "lon": 23.7275, "geothermal": True, "coastal": True},
        "노르웨이 - 오슬로": {"lat": 59.9139, "lon": 10.7522, "geothermal": False, "coastal": True},
        "노르웨이 - 베르겐": {"lat": 60.3913, "lon": 5.3221, "geothermal": False, "coastal": True},
        "네덜란드 - 암스테르담": {"lat": 52.3676, "lon": 4.9041, "geothermal": False, "coastal": True},
        "덴마크 - 코펜하겐": {"lat": 55.6761, "lon": 12.5683, "geothermal": False, "coastal": True},
        "폴란드 - 바르샤바": {"lat": 52.2297, "lon": 21.0122, "geothermal": False, "coastal": False},
        "스위스 - 취리히": {"lat": 47.3769, "lon": 8.5417, "geothermal": False, "coastal": False},
    },
    "북아메리카": {
        "미국 - 뉴욕": {"lat": 40.7128, "lon": -74.0060, "geothermal": False, "coastal": True},
        "미국 - 로스앤젤레스": {"lat": 34.0522, "lon": -118.2437, "geothermal": True, "coastal": True},
        "미국 - 시카고": {"lat": 41.8781, "lon": -87.6298, "geothermal": False, "coastal": True},
        "미국 - 피닉스": {"lat": 33.4484, "lon": -112.0740, "geothermal": False, "coastal": False},
        "미국 - 샌프란시스코": {"lat": 37.7749, "lon": -122.4194, "geothermal": True, "coastal": True},
        "미국 - 게이저스": {"lat": 38.7844, "lon": -122.7569, "geothermal": True, "coastal": False},
        "미국 - 호놀룰루": {"lat": 21.3069, "lon": -157.8583, "geothermal": True, "coastal": True},
        "캐나다 - 토론토": {"lat": 43.6532, "lon": -79.3832, "geothermal": False, "coastal": True},
        "캐나다 - 밴쿠버": {"lat": 49.2827, "lon": -123.1207, "geothermal": False, "coastal": True},
        "캐나다 - 캘거리": {"lat": 51.0447, "lon": -114.0719, "geothermal": False, "coastal": False},
        "멕시코 - 멕시코시티": {"lat": 19.4326, "lon": -99.1332, "geothermal": True, "coastal": False},
        "멕시코 - 칸쿤": {"lat": 21.1619, "lon": -86.8515, "geothermal": False, "coastal": True},
        "멕시코 - 세로프리에토": {"lat": 32.4241, "lon": -115.2425, "geothermal": True, "coastal": False},
    },
    "남아메리카": {
        "브라질 - 상파울루": {"lat": -23.5505, "lon": -46.6333, "geothermal": False, "coastal": False},
        "브라질 - 리우데자네이루": {"lat": -22.9068, "lon": -43.1729, "geothermal": False, "coastal": True},
        "브라질 - 브라질리아": {"lat": -15.7975, "lon": -47.8919, "geothermal": False, "coastal": False},
        "아르헨티나 - 부에노스아이레스": {"lat": -34.6037, "lon": -58.3816, "geothermal": False, "coastal": True},
        "아르헨티나 - 우수아이아": {"lat": -54.8019, "lon": -68.3030, "geothermal": False, "coastal": True},
        "칠레 - 산티아고": {"lat": -33.4489, "lon": -70.6693, "geothermal": True, "coastal": False},
        "칠레 - 아타카마": {"lat": -23.8634, "lon": -69.1328, "geothermal": False, "coastal": False},
        "칠레 - 엘타티오": {"lat": -22.3353, "lon": -68.0142, "geothermal": True, "coastal": False},
        "콜롬비아 - 보고타": {"lat": 4.7110, "lon": -74.0721, "geothermal": True, "coastal": False},
        "페루 - 리마": {"lat": -12.0463, "lon": -77.0428, "geothermal": True, "coastal": True},
    },
    "아프리카": {
        "이집트 - 카이로": {"lat": 30.0444, "lon": 31.2357, "geothermal": False, "coastal": False},
        "이집트 - 아스완": {"lat": 24.0889, "lon": 32.8998, "geothermal": False, "coastal": False},
        "케냐 - 나이로비": {"lat": -1.2921, "lon": 36.8219, "geothermal": True, "coastal": False},
        "케냐 - 올카리아": {"lat": -0.8872, "lon": 36.3119, "geothermal": True, "coastal": False},
        "남아프리카공화국 - 케이프타운": {"lat": -33.9249, "lon": 18.4241, "geothermal": False, "coastal": True},
        "남아프리카공화국 - 요하네스버그": {"lat": -26.2041, "lon": 28.0473, "geothermal": False, "coastal": False},
        "모로코 - 카사블랑카": {"lat": 33.5731, "lon": -7.5898, "geothermal": False, "coastal": True},
        "모로코 - 와르자자트": {"lat": 30.9189, "lon": -6.8934, "geothermal": False, "coastal": False},
        "나이지리아 - 라고스": {"lat": 6.5244, "lon": 3.3792, "geothermal": False, "coastal": True},
        "에티오피아 - 아디스아바바": {"lat": 9.0300, "lon": 38.7400, "geothermal": True, "coastal": False},
    },
    "오세아니아": {
        "호주 - 시드니": {"lat": -33.8688, "lon": 151.2093, "geothermal": False, "coastal": True},
        "호주 - 멜버른": {"lat": -37.8136, "lon": 144.9631, "geothermal": False, "coastal": True},
        "호주 - 퍼스": {"lat": -31.9505, "lon": 115.8605, "geothermal": False, "coastal": True},
        "호주 - 앨리스스프링스": {"lat": -23.6980, "lon": 133.8807, "geothermal": False, "coastal": False},
        "뉴질랜드 - 오클랜드": {"lat": -36.8485, "lon": 174.7633, "geothermal": True, "coastal": True},
        "뉴질랜드 - 로토루아": {"lat": -38.1368, "lon": 176.2497, "geothermal": True, "coastal": False},
        "뉴질랜드 - 웰링턴": {"lat": -41.2865, "lon": 174.7762, "geothermal": True, "coastal": True},
        "피지 - 수바": {"lat": -18.1248, "lon": 178.4501, "geothermal": False, "coastal": True},
    }
}


# -----------------------------------------------------------------------------
# 3. Open-Meteo API 연동 함수 (예외 처리 구체화)
# -----------------------------------------------------------------------------
def fetch_climate_data(lat: float, lon: float):
    """
    Open-Meteo API를 호출하여 선택된 좌표의 일사량(MJ/m²)과 최대 풍속(m/s)을 받아옵니다.
    - 일사량 변환: MJ/m² * 0.277778 = kWh/m²
    - 예외 처리: 네트워크 에러나 API 응답 실패 시 프로그램이 중단되지 않고 기본값 반환
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "shortwave_radiation_sum,windspeed_10m_max",
        "timezone": "auto"
    }

    # 요청 실패 시 사용할 기본값
    default_solar_kwh = 4.5
    default_wind_speed = 5.0

    try:
        response = requests.get(url, params=params, timeout=6)
        response.raise_for_status()  # HTTP 상태 코드가 200이 아니면 예외 발생
        data = response.json()

        daily = data.get("daily", {})
        solar_list = daily.get("shortwave_radiation_sum", [])
        wind_list = daily.get("windspeed_10m_max", [])

        if solar_list and wind_list:
            # 일평균 일사량 계산 및 MJ/m² -> kWh/m² 단위 변환
            avg_solar_mj = sum(solar_list) / len(solar_list)
            avg_solar_kwh = avg_solar_mj * 0.277778

            # 일평균 최대 풍속 계산
            avg_wind_speed = sum(wind_list) / len(wind_list)

            return round(avg_solar_kwh, 2), round(avg_wind_speed, 2), False
        else:
            return default_solar_kwh, default_wind_speed, True

    except (requests.exceptions.RequestException, KeyError, ValueError, TypeError):
        # 네트워크 연결 실패, 타임아웃, JSON 파싱 오류 등 모든 예외에 대처
        return default_solar_kwh, default_wind_speed, True


# -----------------------------------------------------------------------------
# 4. 정량적 기후 기준 기반 재생에너지 최적 추천 로직
# -----------------------------------------------------------------------------
def evaluate_renewable_energy(solar: float, wind: float, geothermal: bool, coastal: bool):
    """
    일사량, 풍속, 지열 활성 여부, 해안선 인접 여부를 종합하여 맞춤형 솔루션을 반환합니다.
    """
    solutions = []

    # 1. 태양광 발전 기준
    if solar >= 4.5:
        solutions.append({
            "title": "☀️ 대규모 상업용 태양광 발전 (Solar PV)",
            "desc": f"평균 일사량이 **{solar} kWh/m²**로 우수합니다. 대규모 모듈 단지 조성 시 높은 경제성과 발전 효율을 기대할 수 있습니다."
        })
    elif solar >= 3.0:
        solutions.append({
            "title": "🌤️ 도심 분산형 태양광 (BIPV / 옥상 태양광)",
            "desc": f"평균 일사량이 **{solar} kWh/m²** 수준입니다. 자가소비형 도심 건물 및 주거지 분산 전원 구축이 효과적입니다."
        })

    # 2. 풍력 발전 기준
    if coastal and wind >= 5.5:
        solutions.append({
            "title": "🌊 해상 풍력 발전 (Offshore Wind)",
            "desc": f"해안가에 위치하고 평균 풍속이 **{wind} m/s**로 우수합니다. 대용량 부유식/고정식 해상 풍력 터빈 설치에 최적입니다."
        })
    elif wind >= 5.0:
        solutions.append({
            "title": "💨 육상 풍력 발전 (Onshore Wind)",
            "desc": f"평균 풍속이 **{wind} m/s**로 풍부합니다. 산지나 평지에 대형 풍력 발전기를 설치하여 연속적인 전력 생산이 가능합니다."
        })

    # 3. 지열 발전 기준
    if geothermal:
        solutions.append({
            "title": "🌋 기저부하 대응 지열 발전 (Geothermal Energy)",
            "desc": "지열 활성 구역에 위치하여 계절 및 날씨 변동과 관계없이 24시간 365일 안정적인 기저 전력을 생산할 수 있습니다."
        })

    # 4. 기타 보조 발전
    if not coastal and wind < 4.0 and solar < 3.5:
        solutions.append({
            "title": "💧 소수력 및 바이오매스 융복합 발전",
            "desc": "기후 자원이 다소 부족하므로, 하천 수류를 활용한 소수력 발전이나 유기성 폐자원 기반 바이오매스 융복합 발전이 유용합니다."
        })

    return solutions


# -----------------------------------------------------------------------------
# 5. 스트림릿 메인 UI 구성
# -----------------------------------------------------------------------------
st.title("🌱 글로벌 지역별 맞춤형 재생에너지 추천 시스템")
st.markdown("Open-Meteo 실시간 기후 데이터를 분석하여 해당 지역에 가장 최적화된 재생에너지 솔루션을 추천합니다.")
st.write("---")

# 사이드바: 지역 선택 기능
st.sidebar.header("📍 지역 선택 및 좌표 설정")
search_mode = st.sidebar.radio("입력 방식 선택", ["대륙/국가별 세부 지역 선택", "위도/경도 직접 입력"])

selected_lat = 37.5665
selected_lon = 126.9780
is_geothermal = False
is_coastal = False
location_name = "대한민국 - 서울"

if search_mode == "대륙/국가별 세부 지역 선택":
    continent = st.sidebar.selectbox("대륙 선택", list(LOCATION_DATA.keys()))
    city = st.sidebar.selectbox("세부 지역 선택", list(LOCATION_DATA[continent].keys()))

    city_info = LOCATION_DATA[continent][city]
    selected_lat = city_info["lat"]
    selected_lon = city_info["lon"]
    is_geothermal = city_info["geothermal"]
    is_coastal = city_info["coastal"]
    location_name = city
else:
    st.sidebar.subheader("좌표 입력")
    selected_lat = st.sidebar.number_input("위도 (Latitude)", min_value=-90.0, max_value=90.0, value=37.5665, step=0.0001)
    selected_lon = st.sidebar.number_input("경도 (Longitude)", min_value=-180.0, max_value=180.0, value=126.9780, step=0.0001)
    is_geothermal = st.sidebar.checkbox("지열 활성 지역 여부", value=False)
    is_coastal = st.sidebar.checkbox("해안선 인접 여부", value=False)
    location_name = f"직접 입력 좌표 ({selected_lat:.2f}, {selected_lon:.2f})"

# -----------------------------------------------------------------------------
# 6. 상단 대형 지도 표시
# -----------------------------------------------------------------------------
st.subheader(f"📍 선택한 위치: {location_name}")
map_df = pd.DataFrame({'lat': [selected_lat], 'lon': [selected_lon]})
# 상단에 크게 지도 표시
st.map(map_df, zoom=6)

# -----------------------------------------------------------------------------
# 7. 기후 데이터 분석 및 결과 출력
# -----------------------------------------------------------------------------
with st.spinner("Open-Meteo API에서 기후 데이터를 받아와 분석 중입니다..."):
    solar_val, wind_val, is_fallback = fetch_climate_data(selected_lat, selected_lon)

if is_fallback:
    st.warning("⚠️ API 통신이 원활하지 않아 표준 기후 기본 데이터로 대체 계산되었습니다.")

# 주요 측정 데이터 메트릭 표시
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("일평균 일사량", f"{solar_val} kWh/m²")
m_col2.metric("일평균 최대 풍속", f"{wind_val} m/s")
m_col3.metric("지열 활성화", "활성" if is_geothermal else "비활성")
m_col4.metric("지형 조건", "해안선 인접" if is_coastal else "내륙")

st.write("---")

# -----------------------------------------------------------------------------
# 8. 추천 재생에너지 솔루션 (대폭 키운 글씨 + 시각적 파란/녹색 카드)
# -----------------------------------------------------------------------------
st.subheader("💡 최적 재생에너지 추천 솔루션")

recommended_list = evaluate_renewable_energy(solar_val, wind_val, is_geothermal, is_coastal)

# HTML/CSS 시각적 카드 스타일 적용
for rec in recommended_list:
    st.markdown(f"""
        <div class="recommend-card">
            <div class="recommend-title">{rec['title']}</div>
            <div class="recommend-desc">{rec['desc']}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# -----------------------------------------------------------------------------
# 9. 작성하신 글 기반 3대 핵심 제언 (1줄 요약 카드 형태)
# -----------------------------------------------------------------------------
st.subheader("🚀 지속가능한 에너지전환을 위한 3대 제언")

p1, p2, p3 = st.columns(3)

with p1:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🎯</div>
            <div class="proposal-title">1. 지역 맞춤형 선별</div>
            <div class="proposal-text">지역별 일사량과 기후 특성을 분석해 가장 적합한 에너지원을 선택합니다.</div>
        </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🔋</div>
            <div class="proposal-title">2. ESS 저장장치 확대</div>
            <div class="proposal-text">발전량 변동성과 부족에 대비해 에너지저장장치(ESS)를 지속 확대합니다.</div>
        </div>
    """, unsafe_allow_html=True)

with p3:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🌐</div>
            <div class="proposal-title">3. 광역 전력망 개선</div>
            <div class="proposal-text">지역 간 원활한 전력 공급과 수급 균형을 위해 전력망 인프라를 연계 개선합니다.</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. 데이터 출처 및 하이퍼링크 (하단)
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="source-box">
        📌 <b>Data Sources & References:</b><br>
        • 실시간 기후 API: <a href="https://open-meteo.com/" target="_blank">Open-Meteo Free Weather API</a><br>
        • 세계 은행 일사량/풍속 지도: <a href="https://globalsolaratlas.info/" target="_blank">World Bank Global Solar Atlas</a> | <a href="https://globalwindatlas.info/" target="_blank">World Bank Global Wind Atlas</a>
    </div>
""", unsafe_allow_html=True)
