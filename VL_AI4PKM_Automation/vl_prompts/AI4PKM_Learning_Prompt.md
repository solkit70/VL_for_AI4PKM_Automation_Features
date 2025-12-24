# AI4PKM 학습 프롬프트

이 프롬프트는 **AI4PKM 프로젝트**를 Vibe Learning 방법론으로 학습하기 위한 프로젝트별 프롬프트입니다.

**범용 학습 프롬프트**: `20251121_Each_Day_Learning_prompt.md` 참조

---

## 프로젝트 정보

**학습 중인 프로젝트**: AI4PKM (AI-powered Personal Knowledge Management)
**프로젝트 Repository**: https://github.com/jykim/AI4PKM
**Remote 이름**: upstream

**학습 RoadMap**: `VL_AI4PKM_Automation/vl_roadmap/20251121_ClaudeCode_AI4PKM_Automation_Learning_Roadmap.md`
**학습 WorkLog**: `VL_AI4PKM_Automation/vl_worklog/` 폴더
**학습 산출물**: `VL_AI4PKM_Automation/01-xxx/`, `02-xxx/` ... 폴더

---

## AI4PKM 특정 설정

### Repository 동기화 설정

**Remote Repository**: 사용함
- **Upstream**: https://github.com/jykim/AI4PKM (학습 대상 프로젝트)
- **Origin**: https://github.com/solkit70/VL_for_AI4PKM_Automation_Features (학습 자료 Repository)

**동기화 명령어** (학습 자료 폴더 제외):
```bash
git fetch upstream
git status
git log HEAD..upstream/main --oneline
# 변경된 파일 목록 (VL_AI4PKM_Automation 폴더 제외)
git diff --name-status HEAD upstream/main -- . ':!VL_*' ':!**/vl_*'
```

**Repository 관리 원칙**:
- **Upstream (AI4PKM 프로젝트)**: 학습 대상 코드만 동기화
- **Origin (학습 자료)**: `VL_AI4PKM_Automation/` 폴더는 별도 관리
- **동기화 시**: 학습 자료 폴더는 비교 대상에서 제외
- **코드 기여**: 팀 Repository(upstream)에 PR

### 주요 학습 영역

**AI4PKM CLI 구조** (코드 영역 - 동기화 필요):
- `ai4pkm_cli/` 폴더
- `orchestrator/` 폴더
- `ai4pkm_vault/orchestrator.yaml` 설정 파일

**학습 자료** (동기화 불필요):
- `VL_AI4PKM_Automation/01-AI4PKM_CLI_Structure/`
- `VL_AI4PKM_Automation/02-Basic_Commands/`
- `VL_AI4PKM_Automation/vl_worklog/`

### 동기화 영향도 평가 기준

**대규모 변경 사항 예시**:
- orchestrator/ 아키텍처 변경
- orchestrator.yaml 형식 변경
- CLI 명령어 체계 변경
- 주요 모듈 이름 변경

**중간 변경 사항 예시**:
- 새로운 Poller 추가
- 새로운 CLI 옵션 추가
- 주요 버그 수정

**소규모 변경 사항 예시**:
- 테스트 코드 추가/수정
- README 업데이트
- 마이너 버그 수정
- 주석 추가/수정

---

## AI4PKM 학습 목표

3일간 다음을 달성합니다:
1. **Day 1**: AI4PKM CLI 명령어 체계 이해 및 실행
2. **Day 2**: Orchestrator 아키텍처 이해 및 설정
3. **Day 3**: 실전 자동화 워크플로우 구현 및 커스터마이징

**학습 RoadMap**: `VL_AI4PKM_Automation/vl_roadmap/20251121_ClaudeCode_AI4PKM_Automation_Learning_Roadmap.md` 참조

---

## 학습 시작 프로세스 (AI4PKM)

### Step 1: Repository 동기화 (필수)

```bash
# 1. Upstream 최신 커밋 가져오기
git fetch upstream

# 2. 현재 상태 확인
git status

# 3. Upstream과의 차이 확인
git log HEAD..upstream/main --oneline

# 4. 변경된 파일 목록 (학습 자료 폴더 제외)
git diff --name-status HEAD upstream/main -- . ':!VL_*' ':!**/vl_*'
```

**사용자에게 보고**:
- 변경된 파일 수와 주요 영역 (학습 대상 코드만)
- ai4pkm_cli/, orchestrator/ 등 코어 코드 변경 사항
- **VL_AI4PKM_Automation/ 폴더는 분석에서 제외** (별도 Repository 관리)
- 학습 자료 업데이트 필요 여부
- 권장 조치사항

### Step 2: 학습 계획 수립

1. **이전 WorkLog 확인**
   - `VL_AI4PKM_Automation/vl_worklog/` 폴더에서 최근 WorkLog 읽기
   - 어디까지 진행했는지 파악

2. **RoadMap 참조**
   - `VL_AI4PKM_Automation/vl_roadmap/20251121_ClaudeCode_AI4PKM_Automation_Learning_Roadmap.md`
   - 오늘 진행할 Day와 세션 확인

3. **학습 계획 설명**
   - 오늘 학습 목표
   - 예상 소요 시간
   - 주요 학습 내용
   - 실습 항목

### Step 3: 학습 진행

1. **WorkLog 생성/업데이트**
   - `VL_AI4PKM_Automation/vl_worklog/YYYYMMDD_*.md`

2. **학습 자료 생성**
   - `VL_AI4PKM_Automation/NN-TopicName/` 폴더에 문서 생성

3. **실습 진행**
   - 핵심 명령어 실행
   - 결과 확인 및 기록

---

## AI4PKM 실습 환경

### 필수 도구
- Python 3.8+
- Node.js (Executor 실행)
- Git

### Executor 설치
```bash
# Claude Code
npm install -g @anthropic-ai/claude-code

# Google Gemini CLI (선택)
npm install -g @google/generative-ai-cli
```

### 프로젝트 설치
```bash
# 가상 환경 활성화
source venv/Scripts/activate  # Windows Git Bash
# 또는
.\venv\Scripts\activate       # Windows CMD/PowerShell

# 개발 모드 설치
pip install -e .

# 설치 확인
ai4pkm --help
```

### 설정 파일 위치
- CLI 설정: `ai4pkm_cli.json` (레거시)
- Orchestrator 설정: `ai4pkm_vault/orchestrator.yaml` (현재)
- 프롬프트: `ai4pkm_vault/_Settings_/Prompts/`
- 태스크: `ai4pkm_vault/_Settings_/Tasks/`
- 로그: `ai4pkm_vault/_Settings_/Logs/`

---

## 학습 자료 참조

### 기존 학습 자료
1. **01-AI4PKM_CLI_Structure** (최신: 2025-12-03 업데이트)
   - `01_directory_structure.md` - Orchestrator 아키텍처 구조
   - `02_module_overview.md` - 모듈 상세 설명
   - `03_config_file_guide.md` - orchestrator.yaml 가이드

2. **02-Basic_Commands** (최신: 2025-12-03 업데이트)
   - `01_installation_guide.md` - 설치 가이드
   - `02_command_cheatsheet.md` - 명령어 레퍼런스
   - `03_quick_start_guide.md` - 빠른 시작 가이드

### WorkLog 이력
- `20251129_Day1_CLI_Basics.md` - Day 1 일부 완료
- `20251203_Documentation_Update.md` - Orchestrator 아키텍처 반영

---

## AI에게 요청하는 작업 방식

**학습 시작 시 AI가 해야 할 일:**
1. ✅ **Upstream 동기화 확인** (AI4PKM은 항상 필요)
   - `git fetch upstream`
   - 변경사항 분석 및 보고

2. ✅ **이전 WorkLog 확인**
   - `VL_AI4PKM_Automation/vl_worklog/` 최근 파일 읽기
   - 진행 상황 파악

3. ✅ **오늘의 학습 계획 설명**
   - RoadMap 기반 오늘 학습 내용
   - 예상 시간과 주요 실습 항목
   - 프로그래밍/실행은 하지 말고 설명만

4. ✅ **사용자 승인 대기**
   - 계획 승인 후 학습 시작

---

이 프롬프트와 함께 `20251121_Each_Day_Learning_prompt.md` (범용 프롬프트)를 참조하여 AI4PKM 학습을 진행하세요.
