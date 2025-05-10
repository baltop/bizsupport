# Bizsup - 사업지원 공고 크롤러

한국 테크노파크 및 비즈니스 지원 기관의 사업 공고를 수집하는 Scrapy 기반 웹 크롤링 시스템입니다.

## 설치 방법

### 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)
- 가상환경 사용 권장 (virtualenv 또는 conda)

### 설치 단계

1. 저장소 클론
   ```bash
   git clone https://github.com/yourusername/bizsup.git
   cd bizsup
   ```

2. 가상환경 생성 및 활성화
   ```bash
   # virtualenv 사용
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   venv\Scripts\activate  # Windows
   ```

3. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

   requirements.txt가 없는 경우, 다음 패키지들을 설치하세요:
   ```bash
   pip install scrapy
   pip install scrapy-playwright
   ```

4. Playwright 브라우저 설치
   ```bash
   playwright install
   ```

## 프로젝트 개요

이 프로젝트의 목표는 다음과 같습니다:

1. `server_full.csv`에 정의된 여러 사업지원 웹사이트 크롤링
2. 각 사이트에서 공고 목록 및 상세 정보 추출
3. 공고 내용을 마크다운 파일로 저장
4. 각 공고의 첨부파일 다운로드

이 시스템은 각 대상 웹사이트별로 개별 스파이더를 생성하여 일반 HTTP 요청과 Playwright 통합을 통한 JavaScript 렌더링 페이지를 모두 처리합니다.

## 주요 기능

- 여러 정부/기관 웹사이트 자동 크롤링
- 표준 HTTP 요청 및 JavaScript 렌더링 페이지 지원
- 구조화된 데이터 추출 (제목, 날짜, 상태, 기간 등)
- 표준화된 콘텐츠 저장을 위한 마크다운 생성
- 첨부파일 다운로드
- 페이지 제한 및 요청 제한 설정 가능

## 스파이더 유형

이 프로젝트는 두 가지 유형의 스파이더를 포함합니다:

1. **URL 링크 스타일**: 전통적인 HTML 링크가 있는 사이트를 위한 표준 Scrapy 스파이더
2. **JavaScript 링크 스타일**: 동적으로 로드되는 콘텐츠가 있는 사이트를 위한 Playwright 통합 Scrapy 스파이더

## 디렉토리 구조

```
bizsup/
├── bizsup/
│   ├── __init__.py
│   ├── items.py             # 아이템 정의
│   ├── middlewares.py       # 미들웨어 컴포넌트
│   ├── pipelines.py         # 아이템 파이프라인
│   ├── settings.py          # 프로젝트 설정
│   └── spiders/             # 스파이더 구현
│       ├── __init__.py
│       ├── btp.py           # URL 링크 스타일 스파이더
│       ├── gbtp.py
│       ├── itp.py
│       ├── jbba.py
│       ├── kpt.py
│       ├── lpt.py
│       └── my.py
├── CLAUDE.md                # 프로젝트 가이드라인/문서
├── scrapy.cfg               # Scrapy 설정
└── server_full.csv          # 대상 사이트 정의
```

## 출력 구조

스파이더가 실행되면 다음과 같은 출력 디렉토리 구조가 생성됩니다:

```
output/
├── btp/                    # 각 스파이더는 자체 출력 디렉토리를 가짐
│   ├── 12345.md            # 마크다운 형식의 공고 내용
│   └── 12345/              # 공고별 첨부파일 디렉토리
│       ├── document1.pdf
│       └── document2.xlsx
├── jbba/
│   ├── 67890.md
│   └── 67890/
...
```

## 사용 예시

사용 가능한 스파이더 목록 보기:
```
scrapy list
```

특정 스파이더 실행:
```
scrapy crawl btp
```

스파이더 실행 및 JSON으로 출력 저장:
```
scrapy crawl btp -o btp_results.json
```

Scrapy 쉘로 페이지에서 선택자 테스트:
```
scrapy shell "https://www.btp.or.kr/kor/CMS/Board/Board.do?mCode=MN013"
```