import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="서울-양평 기온 비교 (도시 열섬현상)", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
이 웹앱은 도심(서울)과 교외(양평)의 2025년 시간별 기온 데이터를 비교하여 **도시 열섬현상(Urban Heat Island)**을 시각적으로 분석합니다.
""")

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        # 요구사항 반영: encoding="cp949" 적용하여 CSV 파일 읽기
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        
        # '일시' 컬럼을 datetime 타입으로 변환
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        
        # 필요한 컬럼만 선택하고 이름 변경
        seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울 기온'})
        yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평 기온'})
        
        # '일시'를 기준으로 두 데이터 병합
        df = pd.merge(seoul, yangpyeong, on='일시', how='inner')
        
        # 서울과 양평의 기온차 계산
        df['기온차(서울-양평)'] = df['서울 기온'] - df['양평 기온']
        
        # 시각(0~23시) 및 월(1~12월) 추출
        df['시간'] = df['일시'].dt.hour
        df['월'] = df['일시'].dt.month
        
        return df
    except FileNotFoundError:
        st.error("❌ 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 이 스크립트와 같은 폴더에 있는지 확인해 주세요.")
        return None
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return None

# 데이터 불러오기
df = load_data()

if df is not None:
    # 사이드바에 간단한 요약 통계 정보 제공
    st.sidebar.header("📊 데이터 요약")
    st.sidebar.write(f"분석 데이터 수: {len(df):,} 개")
    st.sidebar.write(f"서울 평균 기온: {df['서울 기온'].mean():.2f} °C")
    st.sidebar.write(f"양평 평균 기온: {df['양평 기온'].mean():.2f} °C")
    st.sidebar.write(f"평균 기온차 (서울-양평): {df['기온차(서울-양평)'].mean():.2f} °C")

    # 📊 ① 1년간 두 지역의 기온 변화 (선그래프)
    st.header("① 1년간 두 지역의 기온 변화")
    line_chart_data = df.set_index('일시')[['서울 기온', '양평 기온']]
    st.line_chart(line_chart_data)
    
    # 레이아웃을 두 칼럼으로 나누어 하단 그래프 배치
    col1, col2 = st.columns(2)
    
    with col1:
        # 📊 ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
        st.header("② 시각별 평균 기온차 (서울 - 양평)")
        hourly_diff = df.groupby('시간')['기온차(서울-양평)'].mean()
        st.bar_chart(hourly_diff)
        st.caption("💡 대개 인공열과 콘크리트 축열의 영향으로 야간 및 새벽 시간대에 도심(서울)의 기온이 교외(양평)보다 높게 유지되는 열섬현상이 잘 나타납니다.")
        
    with col2:
        # 📊 ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
        st.header("③ 월별 평균 기온차 (서울 - 양평)")
        monthly_diff = df.groupby('월')['기온차(서울-양평)'].mean()
        st.bar_chart(monthly_diff)
        st.caption("💡 계절 변화에 따라 두 지역 간의 열섬현상 강도가 어떻게 다른지 한눈에 확인할 수 있습니다.")

    # 원본 데이터 확인 체크박스
    if st.checkbox("전체 데이터 보기"):
        st.dataframe(df)
