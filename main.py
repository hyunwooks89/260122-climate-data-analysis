import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="서울 기온 히스토리 분석기",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 커스텀 CSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    * {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-delta {
        font-size: 1rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .delta-hot {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        color: white;
    }
    
    .delta-cold {
        background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
        color: white;
    }
    
    .delta-normal {
        background: linear-gradient(135deg, #69db7c 0%, #51cf66 100%);
        color: white;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    .stDateInput > div > div > input {
        border-radius: 8px;
    }
    
    .sidebar .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #dee2e6, transparent);
        margin: 2rem 0;
    }
    
    .rank-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .rank-1 { background: #ffd700; color: #333; }
    .rank-2 { background: #c0c0c0; color: #333; }
    .rank-3 { background: #cd7f32; color: white; }
    .rank-other { background: #e9ecef; color: #495057; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 데이터 로드 함수
# ============================================================
@st.cache_data
def load_data(uploaded_file=None):
    """기본 데이터 또는 업로드된 데이터 로드"""
    try:
        if uploaded_file is not None:
            # 업로드된 파일 처리
            df = pd.read_csv(uploaded_file, encoding='euc-kr', skiprows=7, on_bad_lines='skip')
        else:
            # 기본 데이터 로드
            default_path = os.path.join(os.path.dirname(__file__), 'default_data.csv')
            if os.path.exists(default_path):
                df = pd.read_csv(default_path, encoding='euc-kr', skiprows=7, on_bad_lines='skip')
            else:
                return None, "기본 데이터 파일을 찾을 수 없습니다."
        
        # 데이터 정제
        df.columns = ['날짜', '지점', '평균기온', '최저기온', '최고기온']
        df['날짜'] = df['날짜'].astype(str).str.strip()
        df = df[df['날짜'].notna() & (df['날짜'] != '') & (df['날짜'] != 'nan')]
        df = df[df['지점'].notna()]
        
        # 날짜 변환
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        df = df.dropna(subset=['날짜'])
        
        # 월, 일 추출
        df['월'] = df['날짜'].dt.month
        df['일'] = df['날짜'].dt.day
        df['연도'] = df['날짜'].dt.year
        df['월일'] = df['날짜'].dt.strftime('%m-%d')
        
        return df, None
    except Exception as e:
        return None, str(e)

# ============================================================
# 분석 함수
# ============================================================
def analyze_date(df, target_date):
    """특정 날짜의 기온을 역대 같은 날짜와 비교 분석"""
    month = target_date.month
    day = target_date.day
    year = target_date.year
    
    # 같은 월/일 데이터 필터링
    same_day_df = df[(df['월'] == month) & (df['일'] == day)].copy()
    same_day_df = same_day_df.dropna(subset=['평균기온'])
    
    if len(same_day_df) == 0:
        return None
    
    # 해당 날짜 데이터
    target_data = same_day_df[same_day_df['연도'] == year]
    
    if len(target_data) == 0:
        return None
    
    target_row = target_data.iloc[0]
    
    # 통계 계산
    stats = {
        'target_date': target_date,
        'target_avg': target_row['평균기온'],
        'target_min': target_row['최저기온'],
        'target_max': target_row['최고기온'],
        'historical_mean': same_day_df['평균기온'].mean(),
        'historical_std': same_day_df['평균기온'].std(),
        'historical_min': same_day_df['평균기온'].min(),
        'historical_max': same_day_df['평균기온'].max(),
        'historical_count': len(same_day_df),
        'diff_from_mean': target_row['평균기온'] - same_day_df['평균기온'].mean(),
        'percentile': (same_day_df['평균기온'] < target_row['평균기온']).sum() / len(same_day_df) * 100,
        'same_day_df': same_day_df.sort_values('연도'),
        'rank': (same_day_df['평균기온'] >= target_row['평균기온']).sum() + 1
    }
    
    # 역대 순위 (더운 순)
    same_day_sorted = same_day_df.sort_values('평균기온', ascending=False).reset_index(drop=True)
    stats['hot_rank'] = (same_day_sorted['평균기온'] >= target_row['평균기온']).sum()
    
    # 역대 순위 (추운 순)
    same_day_sorted_cold = same_day_df.sort_values('평균기온', ascending=True).reset_index(drop=True)
    stats['cold_rank'] = (same_day_sorted_cold['평균기온'] <= target_row['평균기온']).sum()
    
    return stats

# ============================================================
# 메인 앱
# ============================================================
def main():
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🌡️ 서울 기온 히스토리 분석기</h1>
        <p>1907년부터 현재까지, 오늘의 기온은 역사 속 어디쯤일까요?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("### 📁 데이터 설정")
        
        uploaded_file = st.file_uploader(
            "새 데이터 업로드 (선택사항)",
            type=['csv'],
            help="기상청에서 다운로드한 CSV 파일을 업로드하세요. 업로드하지 않으면 기본 데이터를 사용합니다."
        )
        
        if uploaded_file:
            st.success("✅ 새 데이터가 업로드되었습니다!")
        else:
            st.info("📊 기본 데이터 사용 중")
        
        st.markdown("---")
        st.markdown("### ℹ️ 사용 방법")
        st.markdown("""
        1. 기본 데이터로 시작하거나 새 CSV 업로드
        2. 분석할 날짜 선택
        3. 역대 같은 날짜와 비교 결과 확인
        """)
    
    # 데이터 로드
    df, error = load_data(uploaded_file)
    
    if error:
        st.error(f"❌ 데이터 로드 실패: {error}")
        return
    
    if df is None or len(df) == 0:
        st.error("❌ 데이터를 불러올 수 없습니다.")
        return
    
    # 데이터 정보 표시
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📅 데이터 기간", f"{df['날짜'].min().strftime('%Y-%m-%d')} ~ {df['날짜'].max().strftime('%Y-%m-%d')}")
    with col_info2:
        st.metric("📊 총 데이터", f"{len(df):,}일")
    with col_info3:
        valid_count = df['평균기온'].notna().sum()
        st.metric("✅ 유효 데이터", f"{valid_count:,}일 ({valid_count/len(df)*100:.1f}%)")
    
    st.markdown("---")
    
    # 날짜 선택
    st.markdown("### 📅 분석할 날짜 선택")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 최근 유효 데이터 날짜 찾기
        valid_dates = df[df['평균기온'].notna()]['날짜']
        max_valid_date = valid_dates.max().date()
        min_valid_date = valid_dates.min().date()
        
        selected_date = st.date_input(
            "날짜 선택",
            value=max_valid_date,
            min_value=min_valid_date,
            max_value=max_valid_date,
            help="분석할 날짜를 선택하세요"
        )
    
    # 분석 실행
    stats = analyze_date(df, selected_date)
    
    if stats is None:
        st.warning(f"⚠️ {selected_date.strftime('%Y년 %m월 %d일')}의 데이터가 없습니다. 다른 날짜를 선택해주세요.")
        return
    
    st.markdown("---")
    
    # ============================================================
    # 결과 표시
    # ============================================================
    st.markdown(f"### 📊 {selected_date.strftime('%Y년 %m월 %d일')} 기온 분석 결과")
    
    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        diff = stats['diff_from_mean']
        if diff > 2:
            delta_class = "delta-hot"
            delta_text = f"평년 대비 +{diff:.1f}°C 🔥"
        elif diff < -2:
            delta_class = "delta-cold"
            delta_text = f"평년 대비 {diff:.1f}°C ❄️"
        else:
            delta_class = "delta-normal"
            delta_text = f"평년 대비 {diff:+.1f}°C"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">평균기온</div>
            <div class="metric-value" style="color: #e74c3c;">{stats['target_avg']:.1f}°C</div>
            <div class="metric-delta {delta_class}">{delta_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">최저기온</div>
            <div class="metric-value" style="color: #3498db;">{stats['target_min']:.1f}°C</div>
            <div class="metric-delta delta-normal">아침/새벽</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">최고기온</div>
            <div class="metric-value" style="color: #e67e22;">{stats['target_max']:.1f}°C</div>
            <div class="metric-delta delta-normal">낮 최고</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pct = stats['percentile']
        if pct >= 90:
            rank_text = f"상위 {100-pct:.0f}% 🔥"
            rank_color = "#e74c3c"
        elif pct <= 10:
            rank_text = f"하위 {pct:.0f}% ❄️"
            rank_color = "#3498db"
        else:
            rank_text = f"상위 {100-pct:.0f}%"
            rank_color = "#27ae60"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">역대 순위</div>
            <div class="metric-value" style="color: {rank_color};">{stats['hot_rank']}위</div>
            <div class="metric-delta delta-normal">{stats['historical_count']}년 중 {rank_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # 시각화
    # ============================================================
    tab1, tab2, tab3 = st.tabs(["📈 연도별 추이", "📊 분포 분석", "🏆 역대 기록"])
    
    with tab1:
        # 연도별 평균기온 추이 차트
        chart_df = stats['same_day_df'].copy()
        
        fig = go.Figure()
        
        # 평균선
        fig.add_hline(
            y=stats['historical_mean'], 
            line_dash="dash", 
            line_color="rgba(100,100,100,0.5)",
            annotation_text=f"평년 평균: {stats['historical_mean']:.1f}°C"
        )
        
        # 연도별 데이터
        fig.add_trace(go.Scatter(
            x=chart_df['연도'],
            y=chart_df['평균기온'],
            mode='lines+markers',
            name='평균기온',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6),
            hovertemplate='%{x}년<br>평균기온: %{y:.1f}°C<extra></extra>'
        ))
        
        # 선택된 연도 강조
        fig.add_trace(go.Scatter(
            x=[selected_date.year],
            y=[stats['target_avg']],
            mode='markers',
            name=f'{selected_date.year}년 (선택)',
            marker=dict(size=16, color='#e74c3c', symbol='star'),
            hovertemplate=f'{selected_date.year}년<br>평균기온: {stats["target_avg"]:.1f}°C<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"📅 {selected_date.month}월 {selected_date.day}일 역대 평균기온 추이",
            xaxis_title="연도",
            yaxis_title="평균기온 (°C)",
            hovermode='x unified',
            template='plotly_white',
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # 히스토그램
            fig_hist = go.Figure()
            
            fig_hist.add_trace(go.Histogram(
                x=stats['same_day_df']['평균기온'],
                nbinsx=20,
                name='분포',
                marker_color='#3498db',
                opacity=0.7
            ))
            
            # 선택된 날짜 표시
            fig_hist.add_vline(
                x=stats['target_avg'],
                line_dash="dash",
                line_color="#e74c3c",
                annotation_text=f"{selected_date.year}년: {stats['target_avg']:.1f}°C"
            )
            
            fig_hist.update_layout(
                title="평균기온 분포",
                xaxis_title="평균기온 (°C)",
                yaxis_title="빈도",
                template='plotly_white',
                height=350
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # 박스플롯
            fig_box = go.Figure()
            
            fig_box.add_trace(go.Box(
                y=stats['same_day_df']['평균기온'],
                name='평균기온',
                marker_color='#3498db',
                boxpoints='outliers'
            ))
            
            # 선택된 날짜 포인트
            fig_box.add_trace(go.Scatter(
                x=['평균기온'],
                y=[stats['target_avg']],
                mode='markers',
                name=f'{selected_date.year}년',
                marker=dict(size=12, color='#e74c3c', symbol='diamond')
            ))
            
            fig_box.update_layout(
                title="기온 분포 (박스플롯)",
                yaxis_title="평균기온 (°C)",
                template='plotly_white',
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
        
        # 통계 요약
        st.markdown("#### 📊 통계 요약")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("평년 평균", f"{stats['historical_mean']:.1f}°C")
        with stat_col2:
            st.metric("표준편차", f"{stats['historical_std']:.1f}°C")
        with stat_col3:
            st.metric("역대 최저", f"{stats['historical_min']:.1f}°C")
        with stat_col4:
            st.metric("역대 최고", f"{stats['historical_max']:.1f}°C")
    
    with tab3:
        # 역대 기록 테이블
        st.markdown("#### 🔥 가장 더웠던 날 TOP 10")
        top_hot = stats['same_day_df'].nlargest(10, '평균기온')[['연도', '평균기온', '최저기온', '최고기온']].reset_index(drop=True)
        top_hot.index = top_hot.index + 1
        top_hot.columns = ['연도', '평균기온(°C)', '최저기온(°C)', '최고기온(°C)']
        
        # 선택된 연도 하이라이트
        def highlight_selected(row):
            if row['연도'] == selected_date.year:
                return ['background-color: #fff3cd'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            top_hot.style.apply(highlight_selected, axis=1).format({
                '평균기온(°C)': '{:.1f}',
                '최저기온(°C)': '{:.1f}',
                '최고기온(°C)': '{:.1f}'
            }),
            use_container_width=True
        )
        
        st.markdown("#### ❄️ 가장 추웠던 날 TOP 10")
        top_cold = stats['same_day_df'].nsmallest(10, '평균기온')[['연도', '평균기온', '최저기온', '최고기온']].reset_index(drop=True)
        top_cold.index = top_cold.index + 1
        top_cold.columns = ['연도', '평균기온(°C)', '최저기온(°C)', '최고기온(°C)']
        
        st.dataframe(
            top_cold.style.apply(highlight_selected, axis=1).format({
                '평균기온(°C)': '{:.1f}',
                '최저기온(°C)': '{:.1f}',
                '최고기온(°C)': '{:.1f}'
            }),
            use_container_width=True
        )
    
    # ============================================================
    # 해석 요약
    # ============================================================
    st.markdown("---")
    st.markdown("### 💡 분석 요약")
    
    diff = stats['diff_from_mean']
    pct = stats['percentile']
    
    if diff > 3:
        interpretation = f"""
        🔥 **{selected_date.strftime('%Y년 %m월 %d일')}**은 역대 같은 날짜 중 **매우 더운 편**이었습니다.
        
        - 평균기온 **{stats['target_avg']:.1f}°C**는 평년({stats['historical_mean']:.1f}°C)보다 **{diff:.1f}°C 높습니다**
        - 역대 {stats['historical_count']}년 중 **{stats['hot_rank']}번째로 높은 기온**입니다
        - 상위 **{100-pct:.0f}%**에 해당하는 이례적으로 따뜻한 날이었습니다
        """
    elif diff < -3:
        interpretation = f"""
        ❄️ **{selected_date.strftime('%Y년 %m월 %d일')}**은 역대 같은 날짜 중 **매우 추운 편**이었습니다.
        
        - 평균기온 **{stats['target_avg']:.1f}°C**는 평년({stats['historical_mean']:.1f}°C)보다 **{abs(diff):.1f}°C 낮습니다**
        - 역대 {stats['historical_count']}년 중 **{stats['cold_rank']}번째로 낮은 기온**입니다
        - 하위 **{pct:.0f}%**에 해당하는 이례적으로 추운 날이었습니다
        """
    else:
        interpretation = f"""
        ✅ **{selected_date.strftime('%Y년 %m월 %d일')}**은 역대 같은 날짜와 비교해 **평년 수준**이었습니다.
        
        - 평균기온 **{stats['target_avg']:.1f}°C**는 평년({stats['historical_mean']:.1f}°C)과 비슷합니다 (차이: {diff:+.1f}°C)
        - 역대 {stats['historical_count']}년 중 **{stats['hot_rank']}위** (더운 순)
        - 전체의 **{100-pct:.0f}% 지점**에 위치하는 평범한 날이었습니다
        """
    
    st.markdown(interpretation)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.85rem;">
        📊 데이터 출처: 기상청 기상자료개방포털 | 서울 관측소(108) 일별 기온 데이터<br>
        🛠️ Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
