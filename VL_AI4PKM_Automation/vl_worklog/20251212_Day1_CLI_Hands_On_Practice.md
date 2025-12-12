# WorkLog: Day 1 - CLI 기초 실습

**날짜**: 2025-12-12 (목요일)
**학습자**: ChangSoo (with Claude Code)
**학습 주제**: AI4PKM CLI 기초 명령어 실습
**학습 방식**: Hands-On Practice (실습 중심)

---

## 🔄 Continuous Vibe Learning - Repository 동기화

**동기화 일시**: 2025-12-12 오전
**Upstream 커밋**: 7d205ca - Merge pull request #56 from jykim/fix/task_file_handling (2025-11-21)
**로컬 커밋**: ed88580 - docs: Add WorkLog for documentation update (2025-12-03)

### 동기화 상태
✅ **로컬이 Upstream보다 최신 상태** (12일 앞섬)
- 변경사항 없음
- 학습 자료 최신 상태 유지 (2025-12-03 업데이트 완료)
- 동기화 작업 불필요

### 오늘 학습에 미치는 영향
✅ **영향 없음** - 최신 학습 자료로 바로 학습 진행 가능

---

## 📋 학습 목표

### Day 1 목표
- AI4PKM CLI 기본 명령어 이해 및 실행
- Orchestrator 개념 파악
- 에이전트 시스템 이해
- 설정 파일 구조 파악

### 오늘 세션 목표
1. ✅ `ai4pkm --help` 실행 및 분석
2. ✅ `ai4pkm --list-agents` 실행 및 에이전트 확인
3. ✅ `ai4pkm --show-config` 실행 및 설정 분석
4. ✅ orchestrator.yaml 설정 및 에이전트 구성
5. ✅ 학습 내용 정리 및 문서화

---

## 🎯 실습 진행 기록

### 실습 환경 확인 ✅

**가상 환경**: 활성화 완료
**프로젝트 위치**: `C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM`
**Python 버전**: 3.13.3

---

## 📝 실습 1: ai4pkm --help ✅

**실습 시작 시간**: 2025-12-12 오전
**실습 완료**: ✅ 성공

**목표**: AI4PKM CLI의 전체 명령어 구조 파악

**실습 과제**:
```bash
ai4pkm --help
```

**실행 결과**:
```
Usage: ai4pkm [OPTIONS] [AGENT_ABBREVIATION]

  PKM CLI - Personal Knowledge Management framework.

Options:
  -o, --orchestrator           Run orchestrator daemon (new multi-agent
                               system)
  --orchestrator-status        Show orchestrator status and loaded agents
  -t, --trigger-agent          Trigger an orchestrator agent interactively
                               once
  -d, --debug                  Enable debug logging
  --list-agents                List available AI agents and their status
  --show-config                Show current configuration
  -w, --working-dir DIRECTORY  Working directory to launch the agent from
  --help                       Show this message and exit.
```

**평가 항목**:
- ✅ 명령어가 정상 실행됨
- ✅ 도움말이 출력됨
- ✅ 주요 명령어 확인 완료

---

### 📊 결과 분석 및 설명

#### 1. 설치 상태: ✅ 정상

AI4PKM CLI가 정상적으로 설치되어 있으며, 가상 환경에서 `ai4pkm` 명령어를 직접 사용할 수 있습니다.

#### 2. 주요 명령어 그룹

**Orchestrator 관련 (핵심 기능)**:
- `-o, --orchestrator`: Orchestrator 데몬 실행 (멀티 에이전트 시스템)
- `--orchestrator-status`: Orchestrator 상태 및 로드된 에이전트 확인
- `-t, --trigger-agent`: Orchestrator 에이전트를 수동으로 한 번 실행

**정보 조회 명령어**:
- `--list-agents`: 사용 가능한 AI 에이전트 목록 및 상태
- `--show-config`: 현재 설정 조회

**유틸리티 옵션**:
- `-d, --debug`: 디버그 로깅 활성화
- `-w, --working-dir`: 작업 디렉터리 지정
- `--help`: 도움말 표시

#### 3. 핵심 학습 포인트

**새로운 아키텍처 확인**:
- ✅ "orchestrator daemon (new multi-agent system)" - 최신 Orchestrator 아키텍처 사용 중
- ✅ 이전 레거시 명령어들은 제거되고 Orchestrator 중심으로 재구성됨

**실습 가능한 명령어**:
1. `--list-agents` - 다음 실습에서 진행
2. `--show-config` - 설정 확인
3. `--orchestrator-status` - Orchestrator 상태 확인

#### 4. 문서와의 일치성

✅ **학습 자료가 최신 상태임을 확인**:
- 2025-12-03에 업데이트한 문서의 명령어 구조와 정확히 일치
- Orchestrator 중심 아키텍처 반영됨
- 레거시 명령어 제거됨

---

## 📝 실습 2: ai4pkm --list-agents ⚠️

**실습 시작 시간**: 2025-12-12 오전
**실습 완료**: ⚠️ 에이전트 없음 (예상된 상황)

**목표**: 사용 가능한 AI 에이전트 목록 확인

**실습 과제**:
```bash
ai4pkm --list-agents
```

**실행 결과**:
```
No agents found.
```

**평가 항목**:
- ✅ 명령어가 정상 실행됨
- ⚠️ 에이전트가 설정되지 않음 (예상된 상황)
- ✅ 명령어 동작 확인 완료

---

### 📊 결과 분석 및 설명

#### 1. "No agents found"가 나타나는 이유

이것은 **오류가 아니라 정상적인 상황**입니다. 에이전트가 없다는 것은:

**원인 1: Executor가 설치되지 않음** (가장 가능성 높음)
- AI4PKM은 실제 AI 작업을 수행하기 위해 **Executor**가 필요합니다
- Executor 예시:
  - `claude-code` (Claude Code CLI)
  - `gemini-cli` (Google Gemini CLI)
  - 기타 커스텀 Executor

**원인 2: orchestrator.yaml에 에이전트가 설정되지 않음**
- [orchestrator.yaml](../../../ai4pkm_vault/orchestrator.yaml)에서 에이전트를 정의해야 합니다
- 설정 예시:
  ```yaml
  agents:
    - name: "Documentation Writer"
      abbreviation: "doc"
      executor: "claude-code"
      prompt_file: "documentation_writer.md"
      poller:
        type: "task_file"
        task_file: "doc_tasks.md"
  ```

#### 2. 에이전트 시스템의 구조

AI4PKM의 에이전트는 다음 구조로 작동합니다:

```
orchestrator.yaml (설정)
    ↓
Agent Definition (에이전트 정의)
    ↓
Executor (실행기: claude-code, gemini-cli 등)
    ↓
Poller (트리거: task_file, folder 등)
    ↓
Prompt (프롬프트 파일)
```

**현재 상황**:
- ✅ AI4PKM CLI 설치됨
- ❓ Executor 설치 여부 불명
- ❓ orchestrator.yaml 설정 상태 불명

#### 3. 다음 단계 전략

이 상황을 진단하기 위해 다음 실습을 진행합니다:

**실습 3: `ai4pkm --show-config`**
- orchestrator.yaml 파일 위치 확인
- 현재 설정 내용 확인
- 에이전트 정의 여부 확인

**실습 4: `ai4pkm --orchestrator-status`**
- Orchestrator 데몬 실행 여부 확인
- 로드된 에이전트 확인

#### 4. 참고 문서

에이전트 설정에 대한 자세한 내용:
- [03_config_file_guide.md](../../01-AI4PKM_CLI_Structure/03_config_file_guide.md) - orchestrator.yaml 가이드
- [02_module_overview.md](../../01-AI4PKM_CLI_Structure/02_module_overview.md) - Executor와 Poller 설명

---

## 📝 실습 3: orchestrator.yaml 설정 및 에이전트 구성 ✅

**실습 시작 시간**: 2025-12-12 오전
**실습 완료**: ✅ 성공

**목표**: VL_AI4PKM_Automation 폴더에서 AI4PKM 설정 및 에이전트 생성

### 3.1 문제 발견

첫 시도에서 설정 파일을 찾지 못하는 문제 발생:

```bash
# 프로젝트 루트에서 실행
C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM> ai4pkm --show-config
# 결과: No configuration found.
```

**원인**:
- AI4PKM은 **현재 작업 디렉터리**에서 `orchestrator.yaml`을 찾음
- 학습 폴더 `VL_AI4PKM_Automation`에서 작업하려면 그 디렉터리로 이동 필요

### 3.2 orchestrator.yaml 설정

**작업 위치**: `C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM\VL_AI4PKM_Automation\`

#### 단계 1: Executor 경로 추가

Windows 환경에서는 npm으로 설치한 CLI 도구의 전체 경로를 명시해야 합니다.

[orchestrator.yaml](../orchestrator.yaml) 파일 수정:

```yaml
orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"
  skills_dir: "_Settings_/Skills"
  bases_dir: "_Settings_/Bases"
  max_concurrent: 3
  poll_interval: 1.0

  # Windows executor paths 추가
  executors:
    claude_code:
      command: "C:\\Users\\dougg\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\dougg\\AppData\\Roaming\\npm\\gemini.cmd"
```

**중요**:
- Windows 경로는 백슬래시(`\`)를 두 번 사용 (`\\`)
- 경로는 [ai4pkm_cli.json](../ai4pkm_cli.json)에서 확인 가능

#### 단계 2: 에이전트 정의 업데이트

기존 에이전트 정의에 필수 필드 추가:

```yaml
nodes:
  # Enrich Ingested Content
  - type: agent
    name: Enrich Ingested Content (EIC)
    abbreviation: "eic"              # 추가!
    executor: claude_code            # 추가!
    input_path: vl_ai4pkm_clippings
    output_path: vl_ai4pkm_materials
    output_type: new_file

  # Create Thread Postings
  - type: agent
    name: Create Thread Postings (CTP)
    abbreviation: "ctp"              # 추가!
    executor: claude_code            # 추가!
    input_path:
      - vl_ai4pkm_materials
      - 01-AI4PKM_CLI_Structure
      - 02-Basic_Commands
    output_path: Publish
```

**필수 필드**:
- `abbreviation`: 에이전트 약어 (명령어에서 사용)
- `executor`: 사용할 AI executor 지정
- `name`: 프롬프트 파일명과 정확히 일치해야 함

#### 단계 3: 프롬프트 파일 생성

[_Settings_/Prompts/](../_Settings_/Prompts/) 디렉터리에 프롬프트 파일 생성:

**Enrich Ingested Content (EIC).md**:
```markdown
---
title: Enrich Ingested Content (EIC)
abbreviation: EIC
category: learning
---

Enrich web clippings and raw content for Personal Knowledge Management.

## Input
- Source: vl_ai4pkm_clippings/*.md
- Raw markdown files with web clippings or notes

## Output
- File: vl_ai4pkm_materials/{{filename}}_enriched.md
- Well-structured and enriched content

## Main Process
...
```

**Create Thread Postings (CTP).md**:
```markdown
---
title: Create Thread Postings (CTP)
abbreviation: CTP
category: publishing
---

Create social media thread postings from enriched content.

## Input
- Source: vl_ai4pkm_materials/*.md
- Enriched content files

## Output
- File: Publish/{{filename}}_thread.md
- Social media thread format

## Main Process
...
```

**중요**:
- 프롬프트 파일명은 `orchestrator.yaml`의 `name` 필드와 **정확히 일치**해야 함
- YAML 프론트매터 필수 (title, abbreviation, category)
- 파일 크기가 너무 작으면 에이전트 로딩 실패

### 3.3 설정 확인

#### ai4pkm --show-config

```bash
cd C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM\VL_AI4PKM_Automation
ai4pkm --show-config
```

**결과**:
```
╭─ Configuration (C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM\VL_AI4PKM_Automation\orchestrator.yaml) ─╮
│ Orchestrator Settings:                                                                          │
│   prompts_dir: _Settings_/Prompts                                                               │
│   tasks_dir: _Settings_/Tasks                                                                   │
│   logs_dir: _Settings_/Logs                                                                     │
│   skills_dir: _Settings_/Skills                                                                 │
│   bases_dir: _Settings_/Bases                                                                   │
│   max_concurrent: 3                                                                             │
│   poll_interval: 1.0                                                                            │
│   executors: {'claude_code': {...}, 'gemini': {...}}                                           │
│                                                                                                 │
│ Default Agent Settings:                                                                         │
│   executor: claude_code                                                                         │
│   timeout_minutes: 30                                                                           │
│   max_parallel: 3                                                                               │
│   task_create: True                                                                             │
│   task_priority: medium                                                                         │
│   task_archived: False                                                                          │
│                                                                                                 │
│ Configured Agents: 2                                                                            │
│   • Enrich Ingested Content (EIC)                                                               │
│   • Create Thread Postings (CTP)                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
```

✅ **설정 파일이 정상적으로 로드됨!**

#### ai4pkm --list-agents

```bash
ai4pkm --list-agents
```

**결과**:
```
                                Available Agents
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Abbreviation ┃ Name                          ┃ Category   ┃ Input Path             ┃ Output Path         ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ EIC          │ Enrich Ingested Content (EIC) │ learning   │ vl_ai4pkm_clippings    │ vl_ai4pkm_materials │
│ CTP          │ Create Thread Postings (CTP)  │ publishing │ vl_ai4pkm_materials... │ Publish             │
└──────────────┴───────────────────────────────┴────────────┴────────────────────────┴─────────────────────┘
```

✅ **에이전트가 성공적으로 로드됨!**

### 3.4 최종 폴더 구조

```
VL_AI4PKM_Automation/
├── orchestrator.yaml                    # 메인 설정 파일
├── _Settings_/
│   ├── Prompts/
│   │   ├── Enrich Ingested Content (EIC).md
│   │   └── Create Thread Postings (CTP).md
│   ├── Tasks/                          # 태스크 파일 저장
│   ├── Logs/                           # 로그 파일 저장
│   ├── Skills/                         # Claude Code Skills
│   └── Bases/                          # 프롬프트 기반 지식
├── vl_ai4pkm_clippings/                # EIC 입력 폴더
├── vl_ai4pkm_materials/                # EIC 출력, CTP 입력
├── Publish/                            # CTP 출력 폴더
├── 01-AI4PKM_CLI_Structure/            # 학습 자료
├── 02-Basic_Commands/                  # 학습 자료
├── vl_prompts/                         # 학습 프롬프트
├── vl_roadmap/                         # 학습 로드맵
└── vl_worklog/                         # 학습 WorkLog
```

---

## 💡 학습한 주요 포인트

### 실습 1에서 배운 것:
- AI4PKM CLI는 Orchestrator 중심 아키텍처로 설계됨
- 레거시 명령어는 제거되고 새로운 명령어 체계 사용
- 핵심 명령어: orchestrator, list-agents, show-config, orchestrator-status

### 실습 2에서 배운 것:
- `--list-agents`는 orchestrator.yaml에 정의된 에이전트를 표시
- 에이전트가 없는 것은 정상적인 초기 상태
- 에이전트 동작을 위해서는 Executor 설치와 orchestrator.yaml 설정이 필요
- AI4PKM은 "설정 기반 프레임워크"로 사용자가 에이전트를 정의하는 구조

### 실습 3에서 배운 것 (가장 중요!):
- **작업 디렉터리의 중요성**: AI4PKM은 현재 디렉터리에서 `orchestrator.yaml`을 찾음
- **Windows Executor 경로 설정**: npm 글로벌 설치 경로를 명시적으로 지정 필요
- **에이전트 필수 필드**:
  - `abbreviation`: 명령어에서 사용할 약어
  - `executor`: 사용할 AI executor
  - `name`: 프롬프트 파일명과 정확히 일치
- **프롬프트 파일 요구사항**:
  - YAML 프론트매터 필수 (title, abbreviation, category)
  - 파일명이 orchestrator.yaml의 name과 정확히 일치
  - 파일 크기가 충분해야 함 (최소 수십 바이트 이상)

### 전체 학습 요약:
1. **설치만으로는 부족**: AI4PKM CLI는 설치 후 설정이 필수
2. **레거시 vs 신규**: `ai4pkm_cli.json` (레거시) → `orchestrator.yaml` (신규)
3. **3단계 설정 프로세스**:
   - Step 1: Executor 경로 설정
   - Step 2: 에이전트 정의 (abbreviation, executor 추가)
   - Step 3: 프롬프트 파일 생성

---

## ⚠️ 발생한 문제와 해결 방법

### 문제 1: "No configuration found" ❌→✅

**문제 상황**:
```bash
C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM> ai4pkm --show-config
# 결과: No configuration found.
```

**원인**:
- AI4PKM은 **현재 작업 디렉터리**에서 `orchestrator.yaml`을 찾음
- 프로젝트 루트에는 설정 파일이 없음

**해결 방법**:
```bash
# 방법 1: 작업 디렉터리로 이동
cd VL_AI4PKM_Automation
ai4pkm --show-config

# 방법 2: --working-dir 옵션 사용
ai4pkm --working-dir VL_AI4PKM_Automation --show-config
```

**교훈**:
- AI4PKM 명령어는 항상 `orchestrator.yaml`이 있는 디렉터리에서 실행

### 문제 2: "No agents found" (설정 후에도 발생) ❌→✅

**문제 상황**:
- `orchestrator.yaml`에 에이전트 정의했는데도 "No agents found"

**원인**:
- 프롬프트 파일이 너무 작음 (13 bytes)
- 에이전트 정의에 `abbreviation`과 `executor` 필드 누락

**해결 방법**:
1. **프롬프트 파일 제대로 작성**:
   - YAML 프론트매터 추가
   - Input, Output, Main Process 섹션 포함
   - 최소 50줄 이상의 내용

2. **에이전트 정의 완성**:
   ```yaml
   nodes:
     - type: agent
       name: Enrich Ingested Content (EIC)
       abbreviation: "eic"        # 필수!
       executor: claude_code      # 필수!
       input_path: ...
       output_path: ...
   ```

**교훈**:
- 에이전트가 표시되려면 **모든 구성 요소가 완전**해야 함
- 프롬프트 파일은 단순 placeholder가 아니라 **실제 내용** 필요

### 문제 3: Windows에서 Executor를 찾지 못함 ❌→✅

**문제 상황**:
- claude-code가 설치되어 있는데 AI4PKM이 찾지 못함

**원인**:
- Windows npm 글로벌 경로가 PATH에 없을 수 있음
- AI4PKM이 executor 실행 파일을 찾을 수 없음

**해결 방법**:
orchestrator.yaml에 전체 경로 명시:
```yaml
orchestrator:
  executors:
    claude_code:
      command: "C:\\Users\\dougg\\AppData\\Roaming\\npm\\claude.cmd"
```

**경로 찾는 방법**:
```powershell
# Windows
where claude

# 또는 ai4pkm_cli.json에서 확인
```

**교훈**:
- Windows 환경에서는 executor 경로를 **명시적으로 지정**하는 것이 안전

---

## 🎓 중요한 학습 포인트 정리

### 1. AI4PKM 설정의 핵심 원칙

**"3개 파일 + 1개 디렉터리" 규칙**:
```
✅ orchestrator.yaml        # 설정 파일
✅ _Settings_/Prompts/*.md  # 프롬프트 파일
✅ ai4pkm_cli.json         # Executor 경로 참조
✅ [작업 디렉터리]          # 명령어 실행 위치
```

### 2. 에이전트 생성 체크리스트

- [ ] `orchestrator.yaml`에 executor 경로 추가
- [ ] `nodes` 섹션에 에이전트 정의
  - [ ] `name` (프롬프트 파일명과 일치)
  - [ ] `abbreviation` (명령어 약어)
  - [ ] `executor` (사용할 AI)
  - [ ] `input_path` (입력 폴더)
  - [ ] `output_path` (출력 폴더)
- [ ] `_Settings_/Prompts/` 에 프롬프트 파일 생성
  - [ ] 파일명이 `name` 필드와 정확히 일치
  - [ ] YAML 프론트매터 포함
  - [ ] 충분한 내용 (50줄 이상 권장)
- [ ] 작업 디렉터리로 이동
- [ ] `ai4pkm --list-agents` 로 확인

### 3. 디버깅 순서

문제 발생 시 다음 순서로 확인:
1. **작업 디렉터리**: `orchestrator.yaml`이 있는 곳인가?
2. **설정 파일 로딩**: `ai4pkm --show-config` 성공하는가?
3. **에이전트 정의**: abbreviation, executor 포함되어 있나?
4. **프롬프트 파일**: 파일명 일치하고 내용 충분한가?
5. **Executor 경로**: Windows에서 전체 경로 지정했나?

---

## 🚀 다음 학습 계획 (Day 2)

### Day 2 예상 주제: Orchestrator 실행 및 에이전트 테스트
1. `ai4pkm -o` (Orchestrator 데몬 실행)
2. `ai4pkm --orchestrator-status` (상태 확인)
3. `ai4pkm -t eic` (EIC 에이전트 수동 실행)
4. 실제 파일로 워크플로우 테스트
5. 로그 분석 및 디버깅

### 준비 사항:
- ✅ orchestrator.yaml 설정 완료
- ✅ 프롬프트 파일 생성 완료
- ⏳ 테스트용 클리핑 파일 준비
- ⏳ 에이전트 실행 결과 확인 방법 학습

---

## 📚 생성된 학습 자료

1. **[orchestrator.yaml](../orchestrator.yaml)** - VL_AI4PKM_Automation용 설정 완료
2. **[Enrich Ingested Content (EIC).md](../_Settings_/Prompts/Enrich%20Ingested%20Content%20(EIC).md)** - EIC 에이전트 프롬프트
3. **[Create Thread Postings (CTP).md](../_Settings_/Prompts/Create%20Thread%20Postings%20(CTP).md)** - CTP 에이전트 프롬프트
4. **[20251212_Day1_CLI_Hands_On_Practice.md](./20251212_Day1_CLI_Hands_On_Practice.md)** - 본 WorkLog

---

**학습 완료 시간**: 2025-12-12 오후
**다음 학습 예정**: Day 2 - Orchestrator 실행 및 워크플로우 테스트
**학습 성과**: ✅ AI4PKM 기본 설정 완전 이해 및 에이전트 2개 구성 성공
