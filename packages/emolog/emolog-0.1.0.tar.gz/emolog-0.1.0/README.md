# Emolog 📝

> A terminal-based emotion logging tool for developers

터미널에서 바로 사용할 수 있는 감정 기록 도구입니다. 개발자들이 업무 중 느끼는 다양한 감정을 체계적으로 기록하고 분석할 수 있습니다.

## ✨ 주요 기능

### 📝 감정 로깅
- **대화형 입력**: 상황 → 감정 → 강도 → 몸반응 → 생각 → 컨텍스트 → 태그 순서
- **자동완성**: 감정, 컨텍스트, 몸반응 등 미리 정의된 옵션 제공
- **빠른 접근**: 터미널에서 `emo` 명령어 하나로 즉시 기록

### 📊 분석 기능
- **통계**: 감정 분포, 평균 강도, 컨텍스트별 분석
- **패턴 분석**: 요일별, 시간대별 감정 패턴 발견
- **트리거 분석**: 스트레스 유발 요인 및 부정적 감정 분석
- **타임라인**: 하루/주간 감정 변화 시각화

### 🛠️ 데이터 관리
- **선택적 수정**: 개별 엔트리의 필드별 수정
- **선택적 삭제**: 원하는 엔트리만 골라서 삭제
- **일괄 초기화**: 기간별 또는 전체 데이터 리셋
- **백업/내보내기**: CSV, JSON 형태로 데이터 추출

## 🚀 설치 및 사용법

### 설치
```bash
# 저장소 클론
git clone <repository-url>
cd emolog

# 의존성 설치 (uv 사용 권장)
uv pip install -e .

# 또는 pip 사용
pip install -e .
```

### 기본 사용법
```bash
# 감정 기록하기
emo

# 명시적 로깅
emo log

# 통계 보기
emo stats

# 패턴 분석
emo patterns

# 스트레스 요인 분석
emo triggers

# 감정 타임라인
emo timeline

# 엔트리 수정
emo edit

# 선택적 삭제
emo delete

# 데이터 리셋
emo reset

# 데이터 내보내기
emo export --format csv --period week

# 백업 생성
emo backup
```

## 💾 데이터 저장

- **위치**: `~/.emolog/` 디렉토리
- **형식**: JSONL (JSON Lines) 파일
- **구조**: 날짜별로 자동 분류 (`YYYY/MM/YYYYMMDD.jsonl`)
- **시간대**: KST (한국 표준시) 기준
- **프라이버시**: 모든 데이터는 로컬에만 저장

## 📊 데이터 구조

```json
{
  "timestamp": "2024-08-12T11:30:00+09:00",
  "situation": "코드리뷰 받음",
  "emotion": "긴장",
  "intensity": 6,
  "body_reaction": "손에 땀",
  "thought": "실수가 많이 발견될까 걱정",
  "context": "work",
  "tags": ["코드리뷰", "개발"],
  "id": "uuid-string"
}
```

## 🎯 사용 사례

### 개발자를 위한 감정 추적
- 코드리뷰, 배포, 버그 수정 시 감정 변화 추적
- 스트레스 요인 식별 및 개선 방안 모색
- 업무 패턴과 감정 상태의 상관관계 분석

### 정신 건강 관리
- 일상의 감정 변화 모니터링
- 부정적 감정의 트리거 파악
- 긍정적 경험과 상황 식별

## 🛡️ 프라이버시

- 모든 데이터는 사용자 로컬 컴퓨터에만 저장됩니다
- 외부 서버로 데이터가 전송되지 않습니다
- 사용자가 직접 백업과 데이터 관리를 제어할 수 있습니다

## 🚀 배포 (개발자용)

### PyPI 배포 자동화
이 프로젝트는 GitHub Actions와 OIDC를 통한 안전한 자동 배포를 지원합니다.

1. **태그 생성으로 배포**:
   ```bash
   # 버전 업데이트
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **OIDC 기반 배포 설정** (저장소 관리자):
   - PyPI에서 Trusted Publisher 설정
   - Test PyPI에서 Trusted Publisher 설정
   - 토큰 관리 불필요! 🎉

3. **Trusted Publisher 설정 방법**:
   - PyPI → Account settings → Publishing → Add a new pending publisher
   - Owner: `{your-github-username}`
   - Repository name: `emolog`
   - Workflow name: `publish.yml`
   - Environment name: `pypi` (또는 `test-pypi`)

4. **수동 배포**:
   ```bash
   # 빌드
   python -m build
   
   # Test PyPI 업로드
   twine upload --repository testpypi dist/*
   
   # PyPI 업로드
   twine upload dist/*
   ```

## 🤝 기여

이 프로젝트는 개인 프로젝트로 시작되었지만, 기여를 환영합니다!

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/gmlee/emolog.git
cd emolog

# 개발 의존성 설치
make install
# 또는 직접: uv pip install -e ".[dev]"
```

### 🛡️ 엄격한 코드 품질 관리
이 프로젝트는 **ZERO TOLERANCE** 코드 품질 정책을 사용합니다:

```bash
# 코드 자동 포맷팅
make format

# 품질 검사 (커밋/푸시 전 필수)
make check

# 푸시 준비 완료 (포맷팅 + 검사)
make push-ready
```

#### 🚫 Git 훅 강제 실행
- **pre-commit**: 커밋 시 staged 파일 품질 검사
- **pre-push**: 푸시 시 전체 코드베이스 품질 검사
- **자동 차단**: black/isort 미적용 시 커밋/푸시 완전 차단
- **자동 설치**: 도구가 없으면 자동으로 설치

### 기여 프로세스
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. **Run quality tools** (`make push-ready`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
   - 🛡️ pre-commit 훅이 자동으로 품질 검사
6. Push to the branch (`git push origin feature/amazing-feature`)
   - 🛡️ pre-push 훅이 전체 코드베이스 검사
7. Open a Pull Request

### 🔧 개발 도구 한눈에 보기
| 명령어 | 설명 | 언제 사용? |
|--------|------|-----------|
| `make install` | 개발 환경 설정 | 프로젝트 시작 시 |
| `make format` | 코드 자동 포맷팅 | 개발 중 수시로 |
| `make lint` | 품질 검사만 | CI에서 또는 확인용 |
| `make check` | 품질+기능 검사 | 커밋 전 |
| `make push-ready` | 완전한 준비 | 푸시 전 필수 |
| `make clean` | 빌드 파일 정리 | 필요시 |

### 🛡️ 품질 보장
- **자동 포맷팅**: Black (88자 라인 길이)
- **Import 정렬**: isort (Black 프로필)
- **Git 훅**: 커밋/푸시 시 자동 품질 검사
- **CI/CD**: GitHub Actions에서 다중 Python 버전 테스트

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🎉 감사의 말

개발자들의 정신 건강과 감정 인식의 중요성에 대한 관심에서 출발한 프로젝트입니다. 
여러분의 일상에 작은 도움이 되기를 바랍니다. 😊
