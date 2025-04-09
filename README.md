# 유튜브 동영상 다운로드 및 자막 추출 스크립트

이 도구는 유튜브 동영상 링크를 입력하면 자동으로 자막을 추출한 후 문서로 만들어주는 파이썬 스크립트입니다. 추가적으로 Gemini API를 사용하여 자막을 한국어로 번역하는 기능도 제공합니다.

## 특징

- 유튜브 동영상 자막 추출
- 타임스탬프가 포함된 자막 문서 생성 (docx, txt)
- 전체 스크립트를 하나의 문서로 통합
- 문단별로 정리된 스크립트 생성
- Gemini API를 사용한 한국어 번역 기능
- 번역된 전체 스크립트 및 문단별 번역 제공

## 설치 방법

### 요구 사항

- Python 3.8 이상
- Poetry (선택 사항)
- Gemini API 키 (번역 기능 사용 시)

### 방법 1: pip 사용 (간단)

```bash
# 저장소 클론
git clone https://github.com/yourusername/youtube-transcript-generator.git
cd youtube-transcript-generator

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 방법 2: Poetry 사용 (권장)

```bash
# Poetry 설치 (아직 설치하지 않은 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 저장소 클론
git clone https://github.com/yourusername/youtube-transcript-generator.git
cd youtube-transcript-generator

# Poetry를 사용하여 의존성 설치
poetry install
```

## Gemini API 키 설정

번역 기능을 사용하려면 Gemini API 키가 필요합니다:

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키를 발급받으세요.
2. 다음 방법 중 하나로 API 키를 설정하세요:
   - `.env` 파일 생성 (권장): 프로젝트 루트 디렉토리에 `.env` 파일을 만들고 다음과 같이 작성합니다:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
   - 환경 변수로 설정: `export GEMINI_API_KEY="your-api-key-here"`
   - 명령줄 옵션으로 전달: `--api-key "your-api-key-here"`

## 사용 방법

### 기본 사용법:

```bash
# 직접 실행
python -m youtube_transcript_generator.main "https://www.youtube.com/watch?v=VIDEO_ID"

# 출력 디렉토리 지정
python -m youtube_transcript_generator.main "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir "./my_folder"
```

### 번역 기능 사용:

```bash
# 번역 기능 활성화 (.env 파일에 API 키 설정 필요)
python -m youtube_transcript_generator.main "https://www.youtube.com/watch?v=VIDEO_ID" --translate

# 또는 API 키를 직접 전달
python -m youtube_transcript_generator.main "https://www.youtube.com/watch?v=VIDEO_ID" --translate --api-key "your-api-key-here"

# 특정 .env 파일 지정
python -m youtube_transcript_generator.main "https://www.youtube.com/watch?v=VIDEO_ID" --translate --env-file "/path/to/.env"
```

### Poetry 환경에서 실행:

```bash
# Poetry 환경 내에서 실행
poetry run youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# 번역 기능 활성화
poetry run youtube-transcript "https://www.youtube.com/watch?v=VIDEO_ID" --translate
```

## 출력 파일

스크립트는 다음 파일들을 생성합니다:

1. `[동영상제목]_타임스탬프.docx` 및 `.txt`: 시간 정보가 포함된 원본 자막
2. `[동영상제목]_전체스크립트.docx` 및 `.txt`: 다음 내용을 포함합니다:
   - 정리된 전체 스크립트
   - 번역된 전체 스크립트 (번역 기능 활성화 시)
   - 문단별로 정리된 스크립트 
   - 문단별 번역 (번역 기능 활성화 시)

## .env 파일 설정

프로젝트 루트 디렉토리에 `.env` 파일 예시:

```
# API 키 설정
GEMINI_API_KEY=your_gemini_api_key_here

# 기타 설정 (필요시 추가)
# OUTPUT_DIR=./downloads
# DEFAULT_LANGUAGE=ko
```

## 참고 사항

- 이 프로그램은 유튜브의 자막 API를 사용하여 자막을 추출합니다.
- 자막이 없는 동영상의 경우 자막 추출이 불가능합니다.
- 번역 기능을 사용할 때는 Gemini API의 요청 제한에 주의하세요.
- 매우 긴 스크립트의 경우 번역에 시간이 걸릴 수 있습니다.
- `.env` 파일은 버전 관리에 포함하지 않는 것이 좋습니다 (`.gitignore`에 추가).

## 라이센스

MIT