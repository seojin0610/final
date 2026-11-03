import streamlit as st
import pandas as pd
import requests

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 사용자 지정 CSS 디자인 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="글로벌 맞춤형 재생에너지 추천 시스템",
    page_icon="🌱",
    layout="wide"
)

# 시각적 강조를 위한 커스텀 CSS 스타일링 (제목 24px, 설명 17px, 파란색/녹색 계열 카드)
st.markdown("""
    <style>
    /* 추천 재생에너지 카드 스타일 */
    .recommend-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%);
        border-left: 6px solid #0284c7;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
    
    /* 3대 제언 카드 스타일 (작성하신 글 반영) */
    .proposal-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .proposal-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .proposal-text {
        font-size: 16px;
        font-weight: 600;
        color: #334155;
        line-height: 1.5;
    }
    
    /* 데이터 출처 박스 스타일 */
    .source-box {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 30px;
        font-size: 14px;
        color: #64748b;
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
# 2. 전 세계 80개 이상 세부 지역 좌표 및 기후 특성 데이터 세트
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
        "미국 - 피닉스(애리조나)": {"lat": 33.4484, "lon": -112.0740, "geothermal": False, "coastal": False},
        "미국 - 샌프란시스코": {"lat": 37.7749, "lon": -122.4194, "geothermal": True, "coastal": True},
        "미국 - 호놀룰루(하와이)": {"lat": 21.3069, "lon": -157.8583, "geothermal": True, "coastal": True},
        "캐나다 - 토론토": {"lat": 43.6532, "lon": -79.3832, "geothermal": False, "coastal": True},
        "캐나다 - 밴쿠버": {"lat": 49.2827, "lon": -123.1207, "geothermal": False, "coastal": True},
        "캐나다 - 캘거리": {"lat": 51.0447, "lon": -114.0719, "geothermal": False, "coastal": False},
        "멕시코 - 멕시코시티": {"lat": 19.4326, "lon": -99.1332, "geothermal": True, "coastal": False},
        "멕시코 - 칸쿤": {"lat": 21.1619, "lon": -86.8515, "geothermal": False, "coastal": True},
    },
    "남아메리카": {
        "브라질 - 상파울루": {"lat": -23.5505, "lon": -46.6333, "geothermal": False, "coastal": False},
        "브라질 - 리우데자네이루": {"lat": -22.9068, "lon": -43.1729, "geothermal": False, "coastal": True},
        "아르헨티나 - 부에노스아이레스": {"lat": -34.6037, "lon": -58.3816, "geothermal": False, "coastal": True},
        "칠레 - 산티아고": {"lat": -33.4489, "lon": -70.6693, "geothermal": True, "coastal": False},
        "칠레 - 아타카마 사막": {"lat": -23.8634, "lon": -69.1328, "geothermal": False, "coastal": False},
        "콜롬비아 - 보고타": {"lat": 4.7110, "lon": -74.0721, "geothermal": True, "coastal": False},
        "페루 - 리마": {"lat": -12.0463, "lon": -77.0428, "geothermal": True, "coastal": True},
    },
    "아프리카": {
        "이집트 - 카이로": {"lat": 30.0444, "lon": 31.2357, "geothermal": False, "coastal": False},
        "이집트 - 아스완": {"lat": 24.0889, "lon": 32.8998, "geothermal": False, "coastal": False},
        "케냐 - 나이로비": {"lat": -1.2921, "lon": 36.8219, "geothermal": True, "coastal": False},
        "남아프리카공화국 - 케이프타운": {"lat": -33.9249, "lon": 18.4241, "geothermal": False, "coastal": True},
        "모로코 - 카사블랑카": {"lat": 33.5731, "lon": -7.5898, "geothermal": False, "coastal": True},
        "나이지리아 - 라고스": {"lat": 6.5244, "lon": 3.3792, "geothermal": False, "coastal": True},
    },
    "오세아니아": {
        "호주 - 시드니": {"lat": -33.8688, "lon": 151.2093, "geothermal": False, "coastal": True},
        "호주 - 멜버른": {"lat": -37.8136, "lon": 144.9631, "geothermal": False, "coastal": True},
        "호주 - 퍼스": {"lat": -31.9505, "lon": 115.8605, "geothermal": False, "coastal": True},
        "호주 - 앨리스스프링스": {"lat": -23.6980, "lon": 133.8807, "geothermal": False, "coastal": False},
        "뉴질랜드 - 오클랜드": {"lat": -36.8485, "lon": 174.7633, "geothermal": True, "coastal": True},
        "뉴질랜드 - 웰링턴": {"lat": -41.2865, "lon": 174.7762, "geothermal": True, "coastal": True},
        "피지 - 수바": {"lat": -18.1248, "lon": 178.4501, "geothermal": False, "coastal": True},
    }
}


# -----------------------------------------------------------------------------
# 3. Open-Meteo API 호출 함수 (상세 예외 처리 포함)
# -----------------------------------------------------------------------------
def fetch_climate_data(lat: float, lon: float):
    """
    Open-Meteo API를 호출하여 해당 위도/경도의 일사량과 풍속 데이터를 가져옵니다.
    네트워크 통신 에러나 API 응답 실패 시 튕기지 않고 기본값으로 대체합니다.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "shortwave_radiation_sum,windspeed_10m_max",
        "timezone": "auto"
    }

    # API 실패 시 대체할 기본 안전 값
    default_solar = 4.5
    default_wind = 5.0

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # 상태 코드가 200이 아니면 예외 발생
        data = response.json()

        daily = data.get("daily", {})
        solar_list = daily.get("shortwave_radiation_sum", [])
        wind_list = daily.get("windspeed_10m_max", [])

        if solar_list and wind_list:
            # MJ/m² 단위를 kWh/m²로 변환하기 위해 0.277778 곱하기
            avg_solar_mj = sum(solar_list) / len(solar_list)
            avg_solar_kwh = avg_solar_mj * 0.277778

            # 최대 풍속 평균 계산 (m/s)
            avg_wind = sum(wind_list) / len(wind_list)

            return round(avg_solar_kwh, 2), round(avg_wind, 2), False
        else:
            return default_solar, default_wind, True

    except (requests.exceptions.RequestException, KeyError, ValueError):
        # 네트워크 오류나 데이터 파싱 오류 발생 시 프로그램 종료 없이 기본값 반환
        return default_solar, default_wind, True


# -----------------------------------------------------------------------------
# 4. 정량적 기준을 바탕으로 한 재생에너지 판정 로직
# -----------------------------------------------------------------------------
def evaluate_renewable_energy(solar: float, wind: float, geothermal: bool, coastal: bool):
    """
    일사량, 풍속, 지열 활성 여부, 해안선 인접 여부를 비교하여 맞춤형 재생에너지를 판정합니다.
    """
    solutions = []

    # 태양광 발전 판정
    if solar >= 4.5:
        solutions.append({
            "title": "☀️ 대규모 상업용 태양광 발전 (Solar PV)",
            "desc": f"평균 일사량이 **{solar} kWh/m²**로 매우 우수합니다. 고효율 태양광 모듈을 통해 전력 생산 효율을 극대화할 수 있습니다."
        })
    elif solar >= 3.0:
        solutions.append({
            "title": "🌤️ 도심형 분산식 태양광 (BIPV / 옥상 태양광)",
            "desc": f"평균 일사량이 **{solar} kWh/m²** 수준입니다. 유휴 공간을 활용한 도심형 분산 전원 구축이 적합합니다."
        })

    # 풍력 발전 판정
    if coastal and wind >= 5.5:
        solutions.append({
            "title": "🌊 해상 풍력 발전 (Offshore Wind)",
            "desc": f"해안 인접 지역이며 평균 풍속이 **{wind} m/s**로 강력합니다. 대단위 해상 풍력 단지 조성에 최적의 입지입니다."
        })
    elif wind >= 5.0:
        solutions.append({
            "title": "💨 육상 풍력 발전 (Onshore Wind)",
            "desc": f"평균 풍속이 **{wind} m/s**로 풍부합니다. 구릉지나 평지에 대형 풍력 터빈을 설치해 안정적인 전력을 생산할 수 있습니다."
        })

    # 지열 발전 판정
    if geothermal:
        solutions.append({
            "title": "🌋 지열 에너지 발전 (Geothermal Energy)",
            "desc": "지열 활성 구역에 위치하여 날씨와 무관하게 24시간 기저부하(Base Load) 전력을 안정적으로 공급할 수 있습니다."
        })

    # 기타 보조 솔루션
    if not coastal and wind < 4.0 and solar < 3.5:
        solutions.append({
            "title": "💧 소수력 및 바이오매스 융복합 발전",
            "desc": "기후 자원이 다소 부족하므로, 지역 수자원과 유기성 폐자원을 활용한 보조 신재생 융복합 발전이 유리합니다."
        })

    return solutions


# -----------------------------------------------------------------------------
# 5. 스트림릿 웹 앱 UI 구성
# -----------------------------------------------------------------------------
st.title("🌱 글로벌 지역별 맞춤형 재생에너지 추천 시스템")
st.markdown("Open-Meteo 실시간 기후 데이터를 분석하여 지역별 최적의 에너지 전환 솔루션을 제안합니다.")
st.write("---")

# 사이드바: 지역 선택 및 입력 옵션
st.sidebar.header("📍 분석 지역 설정")
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
    st.sidebar.subheader("좌표 직접 입력")
    selected_lat = st.sidebar.number_input("위도 (Latitude)", min_value=-90.0, max_value=90.0, value=37.5665, step=0.0001)
    selected_lon = st.sidebar.number_input("경도 (Longitude)", min_value=-180.0, max_value=180.0, value=126.9780, step=0.0001)
    is_geothermal = st.sidebar.checkbox("지열 활성 지역 여부", value=False)
    is_coastal = st.sidebar.checkbox("해안선 인접 여부", value=False)
    location_name = f"직접 입력 위치 ({selected_lat:.2f}, {selected_lon:.2f})"

# -----------------------------------------------------------------------------
# 6. 상단 지도 표시 영역
# -----------------------------------------------------------------------------
st.subheader(f"📍 선택된 위치: {location_name}")
map_df = pd.DataFrame({'lat': [selected_lat], 'lon': [selected_lon]})
st.map(map_df, zoom=6)

# -----------------------------------------------------------------------------
# 7. 기후 데이터 호출 및 지표 메트릭 표시
# -----------------------------------------------------------------------------
with st.spinner("Open-Meteo API에서 기후 데이터를 계산해 불러오는 중..."):
    solar_val, wind_val, is_fallback = fetch_climate_data(selected_lat, selected_lon)

if is_fallback:
    st.warning("⚠️ API 통신 장애로 인해 해당 위치의 표준 기후 기본값이 적용되었습니다.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("일평균 일사량", f"{solar_val} kWh/m²")
col2.metric("일평균 최대 풍속", f"{wind_val} m/s")
col3.metric("지열 활성 여부", "활성" if is_geothermal else "비활성")
col4.metric("해안 인접 여부", "해안가" if is_coastal else "내륙")

st.write("---")

# -----------------------------------------------------------------------------
# 8. 추천 재생에너지 솔루션 목록 출력 (대형 글씨 및 블루/그린 카드)
# -----------------------------------------------------------------------------
st.subheader("💡 최적 재생에너지 추천 솔루션")

recommended_list = evaluate_renewable_energy(solar_val, wind_val, is_geothermal, is_coastal)

for rec in recommended_list:
    st.markdown(f"""
        <div class="recommend-card">
            <div class="recommend-title">{rec['title']}</div>
            <div class="recommend-desc">{rec['desc']}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# -----------------------------------------------------------------------------
# 9. 지속가능한 에너지전환을 위한 3대 제언 (작성하신 글 내용 반영)
# -----------------------------------------------------------------------------
st.subheader("🚀 지속가능한 에너지전환을 위한 3대 제언")

p_col1, p_col2, p_col3 = st.columns(3)

with p_col1:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🎯</div>
            <div class="proposal-text"><b>1. 지역 맞춤 선별</b><br>지역별 일사량과 특성을 분석해 가장 적합한 에너지원을 우선 선별합니다.</div>
        </div>
    """, unsafe_allow_html=True)

with p_col2:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🔋</div>
            <div class="proposal-text"><b>2. ESS 연계 기반 마련</b><br>발전량이 부족할 때를 대비해 에너지저장장치(ESS)를 확대합니다.</div>
        </div>
    """, unsafe_allow_html=True)

with p_col3:
    st.markdown("""
        <div class="proposal-card">
            <div class="proposal-icon">🌐</div>
            <div class="proposal-text"><b>3. 광역 전력망 연결</b><br>지역 간 안정적인 전력 공급을 위해 전력망을 개선하고 연결합니다.</div>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 10. 데이터 출처 하이퍼링크 명시 (하단)
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="source-box">
        📌 <b>Data Sources & References:</b><br>
        • 실시간 날씨 및 기후 데이터: <a href="https://open-meteo.com/" target="_blank">Open-Meteo Free Weather API</a><br>
        • 글로벌 재생에너지 통계 지도: <a href="https://globalsolaratlas.info/" target="_blank">World Bank Global Solar Atlas</a> | <a href="https://globalwindatlas.info/" target="_blank">World Bank Global Wind Atlas</a>
    </div>
""", unsafe_allow_html=True)
