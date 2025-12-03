# Work Log - Day 1: CLI 기초와 명령어 실습

**날짜**: 2025-11-29 (토요일)
**학습 주제**: AI4PKM CLI 기초와 명령어 체계
**상태**: 진행 중 🔄

**유튜브 라이브 영상**: [재미로 하는 Vibe Coding 번외편 - Day 1 진도 나갑니다. AI4PKM 에 Vibe Learning Onboarding 하기 세 번째 시간](https://youtube.com/live/fqyOrT8Y2Rc)

---

## 📋 학습 목표

### Day 1 전체 목표
- AI4PKM CLI 명령어 체계 이해 및 실행
- 주요 모듈 구조 파악
- Prompt와 Command 차이 이해
- 3개 에이전트(Claude, Gemini, Codex) 특징 비교

### 오늘 세션별 목표

#### 🌅 오전 세션 (2-3시간)
1. **단계 1**: AI4PKM CLI 구조 이해 (45분)
2. **단계 2**: CLI 설치 및 기본 명령어 (60분)
3. **단계 3**: Prompt 직접 실행 (60분)

#### 🌆 오후 세션 (2-3시간)
4. **단계 4**: Command 실행 (90분)
5. **단계 5**: 에이전트 이해와 비교 (90분)

---

## 🔄 진행 상황

### ✅ 완료한 작업
- [x] WorkLog 파일 생성 (20251129_Day1_CLI_Basics.md)
- [x] 단계 1: CLI 구조 이해
  - [x] 범용 프롬프트 파일 수정 (산출물 폴더 위치 명시)
  - [x] AI4PKM CLI 구조 분석 완료
  - [x] 3개 문서 생성 완료
- [x] 단계 2: 기본 명령어 실습
  - [x] 설치 가이드 작성
  - [x] 명령어 치트시트 작성
  - [x] --help 출력 분석
  - [x] --show-config 출력 분석
  - [x] --list-agents 출력 분석
  - [x] 5개 문서 생성 완료
- [ ] 단계 3: Prompt 실행
- [ ] 단계 4: Command 실행
- [ ] 단계 5: 에이전트 비교

---

## 📝 상세 학습 기록

### 단계 1: AI4PKM CLI 구조 이해 ✅ (완료)

**시작 시간**: 2025-11-29 오전
**완료 시간**: 2025-11-29 오전

**학습 내용**:
- AI4PKM 디렉터리 구조 분석
- 주요 Python 모듈 역할 파악
- 설정 파일 구조 이해

**AI가 생성한 산출물**:
1. ✅ `01-AI4PKM_CLI_Structure/directory_structure.md` - 디렉터리 구조 시각화
   - AI4PKM 전체 프로젝트 구조
   - ai4pkm_cli/ 패키지 상세 구조
   - Vault 디렉터리 구조
   - 디렉터리 관계도

2. ✅ `01-AI4PKM_CLI_Structure/module_overview.md` - 모듈 역할 설명
   - 진입점 (main.py, cli.py)
   - 설정 관리 (config.py)
   - AI 에이전트 시스템
   - 명령어 시스템
   - 오케스트레이터 시스템 (신규)
   - 크론 관리
   - 레거시 vs 신규 시스템 비교

3. ✅ `01-AI4PKM_CLI_Structure/config_file_guide.md` - 설정 파일 가이드
   - ai4pkm_cli.json 전체 구조
   - 에이전트 설정 방법
   - 외부 서비스 동기화 설정
   - 크론 작업 설정
   - 문제 해결 가이드

**추가 작업**:
- ✅ 범용 프롬프트 파일 수정 ([20251121_Each_Day_Learning_prompt.md](VL_AI4PKM_Automation/vl_prompts/20251121_Each_Day_Learning_prompt.md))
  - 산출물 폴더 위치를 `VL_AI4PKM_Automation/` 아래로 명확히 지정
  - 중요 경고 문구 추가

**학습 요약**:
- AI4PKM은 **멀티 에이전트 아키텍처** 기반
- **레거시 시스템** (watchdog, KTM)과 **신규 시스템** (Orchestrator) 공존
- **3가지 에이전트**: Claude Code, Gemini CLI, Codex CLI
- **설정 파일** (ai4pkm_cli.json)이 모든 동작 제어
- **크론 작업**으로 자동화 스케줄링 가능

### 단계 2: CLI 설치 및 기본 명령어 실습 ✅ (완료)

**시작 시간**: 2025-11-29 오전
**완료 시간**: 2025-11-29 오후

**학습 내용**:
- AI4PKM CLI 설치 방법 (Windows/macOS/Linux)
- 기본 명령어 체계 이해
- 주요 옵션 분석
- **실습 추가**: 실제 설치 및 명령어 실행

**AI가 생성한 산출물**:
1. ✅ `02-Basic_Commands/installation_guide.md` - 설치 가이드
   - Windows/macOS/Linux 환경별 설치 절차
   - 대안 실행 방법 3가지
   - 문제 해결 가이드
   - 설치 확인 체크리스트

2. ✅ `02-Basic_Commands/command_cheatsheet.md` - 명령어 치트시트
   - 기본 정보 명령어
   - 프롬프트 실행 방법
   - 자동화 모드 (오케스트레이터, Cron)
   - 에이전트 단축키
   - 빠른 참조 표

3. ✅ `02-Basic_Commands/help_output_analysis.md` - --help 출력 분석
   - 실제 --help 출력 내용
   - 각 옵션 상세 설명 및 사용 예시
   - 옵션 그룹별 분류
   - 초보자 시작 가이드

4. ✅ `02-Basic_Commands/config_output_analysis.md` - --show-config 분석
   - 설정 출력 내용 해석
   - ai4pkm_cli.json 구조 상세
   - 설정 변경 가이드
   - 문제 해결 방법

5. ✅ `02-Basic_Commands/agents_list_analysis.md` - --list-agents 분석
   - 에이전트 상태 표시 방법
   - Claude/Gemini/Codex 특징 비교
   - 작업 유형별 에이전트 추천
   - 에이전트 설정 방법
   - 실전 사용 패턴

6. ✅ `02-Basic_Commands/hands_on_practice_results.md` - **실습 결과 문서** (NEW!)
   - 실제 설치 과정 및 결과
   - 핵심 명령어 실행 결과
   - 발견된 문제와 해결 방법
   - Windows 환경 특화 이슈 문서화

**실습 완료 내역**:

#### 1. 환경 확인 ✅
- Python 3.13.3 확인
- pip 25.0.1 확인
- Windows 환경 확인

#### 2. AI4PKM CLI 설치 ✅
```bash
pip install -e .
```
- 설치 성공: ai4pkm-cli-0.1.0
- 주요 패키지 설치: claude-code-sdk, rich, flask, croniter
- PATH 경고: Scripts 폴더가 PATH에 없음
- 실행 파일 위치: `C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts\ai4pkm.exe`

#### 3. 기본 명령어 실행

**--help 명령어** ✅
```bash
"C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts\ai4pkm.exe" --help
```
- 결과: 완전히 작동
- 모든 옵션 출력 확인
- CLI 구조 이해 완료

**--show-config 명령어** ⚠️
```bash
"C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts\ai4pkm.exe" --show-config
```
- 결과: 부분 성공 (Unicode 인코딩 오류)
- 출력 확인: Agent = claude_code, Agent Name = Claude Code
- 오류: emoji 문자 (✅, ❌) 렌더링 실패
- 원인: Windows CMD가 cp1252 인코딩 사용

**설정 파일 직접 확인** ✅
```bash
type ai4pkm_cli.json
```
- 기본 에이전트: `claude_code`
- 에이전트 설정: claude_code, gemini_cli, codex_cli
- 설정 파일 정상 생성 확인

**--list-agents 명령어** ⚠️
- 결과: Unicode 인코딩 오류 (🔥 이모지)
- 설정 파일로 에이전트 확인 완료

**학습 요약**:
- **설치 방법**: `pip install -e .` (editable 모드) ✅
- **실행 경로**: 전체 경로 사용 필요 (PATH 미설정)
- **주요 명령어**:
  - `-p`: 프롬프트 실행
  - `-cmd`: 명령어 실행
  - `-o`: 오케스트레이터 (권장)
  - `-c`: Cron 스케줄러
  - `-a`: 에이전트 지정 (일회성)
- **3가지 에이전트**:
  - Claude Code: 분석, 글쓰기 (세션 연속성)
  - Gemini CLI: 번역, 빠른 응답
  - Codex CLI: 코드 작성, 디버깅
- **설정 파일**: ai4pkm_cli.json (전역 설정)

**실습에서 발견한 문제**:

#### 문제 1: PATH 경로 누락 ⚠️
- **증상**: `ai4pkm: command not found`
- **원인**: Scripts 폴더가 PATH에 없음
- **해결**: 전체 경로 사용 또는 PATH에 추가
- **영향**: 모든 명령어 실행

#### 문제 2: Unicode 인코딩 오류 (Windows 특화) ⚠️
- **증상**: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'`
- **원인**: Windows CMD가 cp1252 인코딩 사용, emoji 미지원
- **영향**: `--show-config`, `--list-agents` 명령어
- **해결**: PowerShell 또는 Windows Terminal 사용 권장

**교훈**:
- Windows 환경에서는 UTF-8 인코딩 문제 주의
- PATH 설정이 중요 (Scripts 폴더)
- 설정 파일을 직접 확인하는 방법도 유용
- 문서화와 실습을 병행하면 실제 문제를 발견할 수 있음

---

## 💡 학습 포인트

### 단계 1에서 배운 주요 개념:

1. **AI4PKM 아키텍처 특징**
   - 이벤트 기반 자동화 시스템
   - 파일 생성/수정 → 자동으로 AI 에이전트 실행
   - 여러 에이전트가 병렬로 작동 가능

2. **핵심 디렉터리 구조**
   - `ai4pkm_cli/`: Python CLI 패키지 (소스 코드)
   - `_Settings_/Prompts/`: 사용자 정의 프롬프트 (사용자가 편집)
   - `Ingest/`: 외부 소스 데이터 (Gobi, Limitless 등)
   - `AI/Tasks/`: AI 실행 결과 저장

3. **레거시 vs 신규 시스템**
   - **레거시**: watchdog/ (파일 감시), ktp_runner (태스크 처리) → 향후 제거 예정
   - **신규**: orchestrator/ (통합 멀티 에이전트 시스템) → 현재 개발 중

4. **설정 파일의 중요성**
   - `ai4pkm_cli.json`이 모든 동작 제어
   - CWD(현재 작업 디렉터리)에 반드시 존재해야 함
   - 에이전트, 크론, 외부 서비스 모두 여기서 설정

5. **에이전트 시스템**
   - Factory Pattern으로 에이전트 생성
   - BaseAgent 추상 클래스를 상속받아 구현
   - 각 에이전트는 독립적으로 실행 가능

### 단계 2에서 배운 주요 개념:

1. **설치 방법**
   - Python 3.8+ 필요
   - `pip install -e .` (editable 모드)
   - 가상 환경 사용 권장
   - PATH 문제 해결 방법 3가지

2. **CLI 명령어 구조**
   - `-p`: 프롬프트 직접 실행 (가장 자주 사용)
   - `-cmd`: 사전 정의 명령어 실행
   - `-o`: 오케스트레이터 (신규, 권장)
   - `-c`: Cron 스케줄러 + 웹 서버
   - `-a`: 에이전트 일회성 지정 (반드시 `-p`와 함께)

3. **에이전트 특징 비교**
   - **Claude Code**: 분석/글쓰기 강점, 세션 연속성, 파일 자동 접근
   - **Gemini CLI**: 번역/속도 강점, 무료 티어, 멀티모달
   - **Codex CLI**: 코딩 전문, 디버깅 특화, 기술 문서

4. **설정 파일 구조**
   - `default-agent`: 기본 에이전트
   - `agents-config`: 에이전트별 세부 설정
   - `orchestrator`: 오케스트레이터 설정
   - `cron_jobs`: 예약 작업
   - 외부 서비스 설정 (Gobi, Limitless 등)

5. **명령어 사용 패턴**
   - 작업별 에이전트 선택: `ai4pkm -a g -p "번역"`
   - 설정 확인 후 실행: `ai4pkm --show-config`
   - 디버그 모드: `ai4pkm -d -p "테스트"`
   - 자동화: `ai4pkm -o` (백그라운드 실행)

---

## ⚠️ 발생한 문제

### 문제 1: 산출물 폴더 위치 오류 (해결됨 ✅)

**발생 시점**: 단계 1 시작 시

**문제 내용**:
- AI가 `01-AI4PKM_CLI_Structure/` 폴더를 프로젝트 루트에 생성
- 사용자 요구사항: `VL_AI4PKM_Automation/` 아래에 생성되어야 함

**원인**:
- 범용 프롬프트 파일에 "root folder에 nn- 로 시작하는 폴더를 만들어서"라고 기재됨
- 프롬프트 내용이 명확하지 않아 오해 발생

**해결 방법**:
1. 생성된 폴더를 올바른 위치로 이동: `mv 01-AI4PKM_CLI_Structure VL_AI4PKM_Automation/`
2. 범용 프롬프트 파일 수정:
   - 기존: "root folder에 nn- 로 시작하는 폴더를 만들어서"
   - 수정: "VL_AI4PKM_Automation 폴더 아래에 nn- 로 시작하는 폴더를 만들어서"
   - 추가: **중요** 경고 문구 추가

**교훈**:
- 프롬프트는 명확하고 구체적으로 작성해야 함
- 위치나 경로 지시는 상대 경로와 절대 경로를 모두 명시
- 중요한 규칙은 별도로 강조 표시

---

### 문제 2: 실습 누락 (해결됨 ✅)

**발생 시점**: 단계 2 문서 생성 후

**문제 내용**:
- AI가 문서만 생성하고 실제 명령어 실행을 하지 않음
- 사용자 요구사항: 핵심 명령어를 직접 실행하면서 학습해야 함

**원인**:
- 범용 프롬프트에 실습 진행에 대한 명확한 지시가 없었음
- "프로그래밍을 하거나 스크립트를 실행하거나 하는 일은 진행하지 말고"라는 문구가 오해 유발

**해결 방법**:
1. 범용 프롬프트에 "실습 진행 (Hands-On Practice)" 섹션 추가
2. 문서 작성 + 실습 병행 원칙 명시
3. 핵심 명령어 우선 실행 원칙 추가
4. 실습 워크플로우 정의

**교훈**:
- 학습은 문서화와 실습을 병행해야 효과적
- AI가 실습까지 진행하도록 명확히 지시 필요
- 핵심/필수 명령어와 고급 옵션을 구분하여 실습 범위 명확화

---

### 문제 3: Windows PATH 경로 누락 (해결 방법 제시 ⚠️)

**발생 시점**: 단계 2 실습 중 AI4PKM CLI 설치 후

**문제 내용**:
- `ai4pkm` 명령어 실행 시 "command not found" 오류
- Scripts 폴더가 시스템 PATH에 등록되지 않음

**원인**:
- Windows User Scripts 폴더: `C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts\`
- pip가 사용자 설치 모드로 실행 (normal site-packages is not writeable)
- User Scripts 폴더는 기본 PATH에 포함되지 않음

**임시 해결 방법**:
- 전체 경로로 실행:
  ```bash
  "C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts\ai4pkm.exe" --help
  ```

**영구 해결 방법** (권장):
1. 시작 → "환경 변수" 검색
2. "시스템 환경 변수 편집" 클릭
3. "환경 변수" 버튼 클릭
4. "사용자 변수"에서 "Path" 선택 → "편집"
5. "새로 만들기" 클릭
6. `C:\Users\dougg\AppData\Roaming\Python\Python313\Scripts` 추가
7. 새 터미널 열기

**교훈**:
- Windows 환경에서 pip user install 사용 시 PATH 설정 필요
- 실습을 통해 문서에 없는 실제 환경 문제 발견 가능
- 해결 방법을 여러 가지 제시 (임시/영구)

---

### 문제 4: Windows Unicode 인코딩 오류 (부분 해결 ⚠️)

**발생 시점**: 단계 2 실습 중 `--show-config`, `--list-agents` 실행

**문제 내용**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 1:
character maps to <undefined>
```

**원인**:
- Windows Command Prompt가 cp1252 인코딩 사용
- Rich 라이브러리가 emoji 문자 출력 시도 (✅ `\u2705`, ❌ `\u274c`, 🔥 `\U0001f525`)
- cp1252는 emoji를 지원하지 않음

**영향 받는 명령어**:
- `--show-config`: Agent Available 출력 시
- `--list-agents`: 에이전트 상태 표시 시

**해결 방법**:

#### 방법 1: PowerShell 또는 Windows Terminal 사용 (권장)
- PowerShell과 Windows Terminal은 UTF-8을 더 잘 지원
- Windows Terminal은 Microsoft Store에서 무료 설치 가능

#### 방법 2: 설정 파일 직접 확인 (임시)
```bash
type ai4pkm_cli.json
# 또는
cat ai4pkm_cli.json
```

#### 방법 3: 코드 수정 (근본적)
- [cli.py:633](../../ai4pkm_cli/cli.py#L633)와 [cli.py:614](../../ai4pkm_cli/cli.py#L614)에서 emoji 제거
- 또는 Rich Console에 `legacy_windows=False` 설정

**부분 성공**:
- 명령어는 작동하지만 emoji 출력 전에 오류 발생
- 부분적인 정보는 출력됨 (Agent, Agent Name 등)
- 기능적으로는 문제없지만 사용자 경험이 저하됨

**교훈**:
- Windows 환경에서는 UTF-8 인코딩 문제 고려 필요
- 크로스 플랫폼 CLI 개발 시 emoji 사용 주의
- 실습을 통해 다양한 환경에서의 호환성 문제 발견
- 여러 대안 방법 제시로 사용자에게 선택권 제공

---

## 🚀 다음 작업

**현재 상태**: 단계 2 완료 ✅ (오늘 학습 종료)

**완료된 단계**:
- ✅ 단계 1: CLI 구조 이해 (3개 문서 생성)
- ✅ 단계 2: 기본 명령어 실습 (6개 문서 생성 + 실습 완료)

**다음 세션 계획**: PowerShell 매뉴얼 실행 실습

**다음 세션에서 할 일**:
1. **PowerShell 환경 설정**:
   - Windows Terminal 또는 PowerShell 실행
   - PATH 환경 변수 설정 (선택사항)
   - Unicode 인코딩 문제 확인

2. **사용자가 직접 실행할 명령어** (매뉴얼 실습):
   ```powershell
   # 기본 정보 확인
   ai4pkm --help
   ai4pkm --show-config
   ai4pkm --list-agents

   # 간단한 프롬프트 실행
   ai4pkm -p "Hello, AI4PKM!"
   ai4pkm -p "2+2는?"

   # 에이전트 지정 실행 (Claude Code 사용)
   ai4pkm -a c -p "Python에서 리스트와 튜플의 차이점은?"
   ```

3. **AI 지원 사항**:
   - 실행 결과 분석 및 설명
   - 오류 발생 시 문제 해결 가이드
   - 실습 과정 문서화

4. **예상 산출물** (다음 세션):
   - `03-PowerShell_Practice/manual_execution_guide.md`: PowerShell 매뉴얼 실행 가이드
   - `03-PowerShell_Practice/execution_results.md`: 사용자 실행 결과 기록
   - `03-PowerShell_Practice/troubleshooting_guide.md`: 실습 중 문제 해결

**준비 사항**:
1. PowerShell 또는 Windows Terminal 실행 환경
2. 생성된 6개 문서 검토 (특히 `hands_on_practice_results.md`)
3. PATH 설정 고려 (선택사항)

**총 진행률**: 2/5 단계 완료 (40%)

**다음 세션 시작 멘트**: "PowerShell 매뉴얼 실습 시작해줘" 또는 "단계 3 시작해줘"

---

## 📚 참고 자료

### 오늘 생성된 문서 (9개)

**01-AI4PKM_CLI_Structure/** (3개):
1. [01_directory_structure.md](../01-AI4PKM_CLI_Structure/01_directory_structure.md) - 디렉터리 구조
2. [02_module_overview.md](../01-AI4PKM_CLI_Structure/02_module_overview.md) - 모듈 개요
3. [03_config_file_guide.md](../01-AI4PKM_CLI_Structure/03_config_file_guide.md) - 설정 파일 가이드

**02-Basic_Commands/** (6개):
1. [01_installation_guide.md](../02-Basic_Commands/01_installation_guide.md) - 설치 가이드
2. [02_command_cheatsheet.md](../02-Basic_Commands/02_command_cheatsheet.md) - 명령어 치트시트
3. [03_help_output_analysis.md](../02-Basic_Commands/03_help_output_analysis.md) - --help 분석
4. [04_config_output_analysis.md](../02-Basic_Commands/04_config_output_analysis.md) - --show-config 분석
5. [05_agents_list_analysis.md](../02-Basic_Commands/05_agents_list_analysis.md) - --list-agents 분석
6. **[06_hands_on_practice_results.md](../02-Basic_Commands/06_hands_on_practice_results.md)** - 실습 결과 (NEW!)

### 이전 문서
- 로드맵: [20251121_ClaudeCode_AI4PKM_Automation_Learning_Roadmap.md](../vl_roadmap/20251121_ClaudeCode_AI4PKM_Automation_Learning_Roadmap.md)
- 이전 WorkLog: [20251121_Day1_CLI_Basics_Planning.md](20251121_Day1_CLI_Basics_Planning.md)
- 프롬프트: [20251121_Each_Day_Learning_prompt.md](../vl_prompts/20251121_Each_Day_Learning_prompt.md)

---

**최종 업데이트**: 2025-11-29 (오늘 학습 완료)
