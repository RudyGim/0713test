import streamlit as st
import pandas as pd

# 1. 페이지 및 레이아웃 설정
st.set_page_config(page_title="서울 기온 분석 대시보드", layout="wide")

st.title("📊 서울 기온 분석: 도시 열섬현상 및 전력수요 영향분석")
st.markdown("""
이 웹앱은 도심(서울)과 교외(양평)의 기온 데이터를 비교하여 **도시 열섬현상**을 분석하고, 
서울의 기온 변화가 **전력수요**에 미치는 영향을 데이터로 시각화합니다.
""")

# 2. 데이터 로드 및 전처리 기능 (캐싱 적용)
@st.cache_data
def load_all_data():
    try:
        # [공통] encoding="cp949" 필수 적용하여 데이터 로드
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        power = pd.read_csv("전력수요.csv", encoding="cp949")
        
        # 일시 컬럼을 datetime 타입으로 변환
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        power['일시'] = pd.to_datetime(power['일시'])
        
        # 필요한 열만 필터링 및 컬럼명 재설정
        seoul_clean = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
        yang_clean = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
        
        return seoul_clean, yang_clean, power
        
    except FileNotFoundError as e:
        st.error(f"❌ 파일 로드 실패: 같은 폴더 내에 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 모두 존재하는지 확인해 주세요. (상세 오류: {e})")
        return None, None, None
    except Exception as e:
        st.error(f"❌ 데이터 전처리 오류 발생: {e}")
        return None, None, None

# 데이터 로드 실행
seoul_df, yang_df, power_df = load_all_data()

# 데이터가 성공적으로 로드된 경우에만 대시보드 시각화 진행
if seoul_df is not None and yang_df is not None and power_df is not None:
    
    # st.tabs를 사용하여 2개의 탭 구성
    tab1, tab2 = st.tabs(["🌡️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------
    # [탭1: 열섬 분석] 서울 & 양평 기온 비교
    # -------------------------------------------------------------
    with tab1:
        st.header("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 열섬현상 분석")
        st.markdown("도심(서울)과 교외(양평) 간의 기온 차이를 시각화하여 도시 열섬현상의 시공간적 패턴을 확인합니다.")
        
        # 데이터 병합 (동일 일시 기준)
        df_temp = pd.merge(seoul_df, yang_df, on='일시', how='inner')
        df_temp['기온차'] = df_temp['서울_기온'] - df_temp['양평_기온']
        df_temp['시간'] = df_temp['일시'].dt.hour
        df_temp['월'] = df_temp['일시'].dt.month
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        line_chart_data = df_temp.set_index('일시')[['서울_기온', '양평_기온']]
        st.line_chart(line_chart_data)
        
        # ②, ③ 그래프를 나란히 배치하기 위한 컬럼 레이아웃
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hourly_diff = df_temp.groupby('시간')['기온차'].mean()
            st.bar_chart(hourly_diff)
            st.caption("💡 야간 및 새벽 시간대(일몰 이후)에 도심에 축열된 열이 빠져나가지 못해 양평과의 기온차가 더욱 뚜렷하게 벌어집니다.")
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            monthly_diff = df_temp.groupby('월')['기온차'].mean()
            st.bar_chart(monthly_diff)
            st.caption("💡 계절에 따라 도심지의 인공열 방출량과 녹지 효과 차이로 인해 월별 기온차 양상이 다르게 관측됩니다.")
            
    # -------------------------------------------------------------
    # [탭2: 전력 연결] 서울 기온 & 전력수요 비교
    # -------------------------------------------------------------
    with tab2:
        st.header("⚡ 서울 기온 변동과 전력수요의 관계")
        st.markdown("서울의 기온 변화에 따른 전력소비 특성 및 냉난방 수요 패턴을 정량적으로 파악합니다.")
        
        # 데이터 병합 (동일 일시 기준)
        df_power = pd.merge(seoul_df, power_df, on='일시', how='inner')
        df_power['월'] = df_power['일시'].dt.month
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 서울 기온 vs 전력수요 분포 (산점도)")
        st.scatter_chart(df_power, x='서울_기온', y='전력수요(MWh)')
        st.caption("💡 일반적으로 혹한기(난방)와 혹서기(냉방)에 전력 수요가 급증하는 U자형 패턴이 그려집니다.")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 기온 구간별 평균 전력수요")
            # 5도 단위 기온 구간 설정 및 한글 라벨링
            bins = list(range(-20, 45, 5))
            df_power['기온구간'] = pd.cut(df_power['서울_기온'], bins=bins, right=False)
            
            # 카테고리 순서가 꼬이지 않도록 데이터 가공
            grouped_interval = df_power.groupby('기온구간', observed=True)['전력수요(MWh)'].mean()
            # X축 레이블을 친숙한 문자열 형태로 변환
            grouped_interval.index = grouped_interval.index.map(lambda x: f"{int(x.left)}~{int(x.right)}°C")
            
            st.bar_chart(grouped_interval)
            st.caption("💡 기온이 매우 낮을 때와 매우 높을 때 각각 냉난방 부하가 걸려 평균 전력수요가 크게 늘어나는 것을 볼 수 있습니다.")
            
        with col4:
            # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = df_power.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power)
            st.caption("💡 한여름(7~8월) 냉방 수요와 겨울철(12~1월) 난방 수요가 증가하는 계절성이 나타납니다.")
            
else:
    st.info("💡 웹앱을 구동하기 전, CSV 데이터 파일들이 같은 디렉토리(폴더)에 준비되어 있는지 먼저 확인해 주세요.")
```eof

---

### 🛠️ 설치 및 웹앱 실행 가이드

1. **파일 구성**: 실행하려는 폴더 안에 아래 4개 파일이 함께 있는지 확인해 주세요.
   - `app.py` (위에서 생성한 코드 파일)
   - `서울_기온.csv`
   - `양평_기온.csv`
   - `전력수요.csv`
2. **필요 패키지 설치**: 터미널 환경에서 라이브러리를 설치합니다.
   
```bash
   pip install streamlit pandas
