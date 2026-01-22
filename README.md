# 🌡️ 서울 기온 히스토리 분석기

> 1907년부터 현재까지, 오늘의 기온은 역사 속 어디쯤일까요?

서울의 118년간 기온 데이터를 활용하여 특정 날짜가 역대 같은 날짜와 비교해 얼마나 더웠는지, 추웠는지를 시각적으로 분석하는 웹 애플리케이션입니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ 주요 기능

### 📊 날짜별 기온 비교 분석
- 선택한 날짜의 평균/최저/최고 기온 표시
- 평년(역대 같은 날짜 평균) 대비 차이 계산
- 역대 순위 및 백분위 표시

### 📈 시각화
- **연도별 추이 차트**: 같은 월/일의 기온이 연도별로 어떻게 변했는지 확인
- **분포 히스토그램**: 역대 기온 분포와 선택 날짜의 위치
- **박스플롯**: 중앙값, 사분위수, 이상치 시각화

### 🏆 역대 기록
- 해당 날짜 기준 가장 더웠던 날 TOP 10
- 해당 날짜 기준 가장 추웠던 날 TOP 10

### 📁 데이터 업로드
- 기본 데이터(서울 1907~2026) 탑재
- 동일 형식의 새 CSV 파일 업로드 지원

---

## 🚀 배포 방법

### Streamlit Cloud 배포

1. **GitHub 저장소 생성**
   ```
   your-repo/
   ├── app.py (또는 main.py)
   ├── default_data.csv
   ├── requirements.txt
   └── README.md
   ```

2. **Streamlit Cloud 연결**
   - [share.streamlit.io](https://share.streamlit.io) 접속
   - GitHub 계정 연결
   - 저장소 선택 → 메인 파일 지정
   - **Deploy** 클릭

3. **배포 완료!**

---

## 💻 로컬 실행 방법

```bash
# 저장소 클론
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📁 데이터 형식

기상청 기상자료개방포털에서 다운로드한 CSV 파일을 사용합니다.

### 다운로드 방법
1. [기상자료개방포털](https://data.kma.go.kr) 접속
2. 기상자료 → 지상 → 관측지점별 일자료
3. 지점: 서울(108) 선택
4. 기간 설정 후 CSV 다운로드

### 파일 구조
```
기온자료,,,,
[검색조건],,,,
자료구분 : 일,,,,
... (메타데이터)
날짜,지점,평균기온(℃),최저기온(℃),최고기온(℃)
1907-10-01,108,13.5,7.9,20.7
1907-10-02,108,16.2,7.9,22.0
...
```

| 컬럼 | 설명 |
|------|------|
| 날짜 | YYYY-MM-DD 형식 |
| 지점 | 관측소 코드 (서울=108) |
| 평균기온(℃) | 일 평균기온 |
| 최저기온(℃) | 일 최저기온 |
| 최고기온(℃) | 일 최고기온 |

**인코딩**: EUC-KR (기상청 기본 형식)

---

## 📦 기술 스택

| 패키지 | 용도 |
|--------|------|
| `streamlit` | 웹 애플리케이션 프레임워크 |
| `pandas` | 데이터 처리 및 분석 |
| `numpy` | 수치 연산 |
| `plotly` | 인터랙티브 시각화 |

---

## 📊 데이터 정보

### 기본 탑재 데이터
- **출처**: 기상청 기상자료개방포털
- **관측소**: 서울(108)
- **기간**: 1907년 10월 ~ 2026년 1월
- **총 레코드**: 약 42,000일

### 결측 구간
한국전쟁 기간 중 일부 데이터 누락:
- 1950년 9월~11월 일부
- 1951년 12월 ~ 1953년 11월

---

## 🖼️ 스크린샷

### 메인 대시보드
- 선택 날짜의 기온 및 평년 대비 차이
- 역대 순위 표시

### 연도별 추이 차트
- 같은 월/일의 역대 기온 변화
- 선택 연도 강조 표시

### 분포 분석
- 히스토그램 및 박스플롯
- 통계 요약 (평균, 표준편차, 최솟값, 최댓값)

---

## 🔧 문제 해결

### ModuleNotFoundError 발생 시
1. `requirements.txt`가 루트 폴더에 있는지 확인
2. 파일명이 정확히 `requirements.txt`인지 확인
3. Streamlit Cloud에서 **Reboot app** 실행

### 데이터 로드 실패 시
1. CSV 파일 인코딩이 EUC-KR인지 확인
2. 파일 상단 7줄이 메타데이터인지 확인
3. 컬럼명이 올바른지 확인

---

## 📝 라이선스

MIT License

---

## 🙏 감사의 말

- 데이터 제공: [기상청 기상자료개방포털](https://data.kma.go.kr)
- 프레임워크: [Streamlit](https://streamlit.io)

---

<div align="center">

**Made with ❤️ using Streamlit & Plotly**

</div>
