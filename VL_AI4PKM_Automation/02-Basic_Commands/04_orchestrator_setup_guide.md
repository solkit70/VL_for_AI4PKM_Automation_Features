# AI4PKM Orchestrator 설정 가이드 (Windows 환경)

**작성일**: 2025-12-12
**대상**: Windows에서 AI4PKM을 처음 설정하는 사용자
**난이도**: 초급
**소요 시간**: 30분

---

## 📋 목차

1. [시작하기 전에](#시작하기-전에)
2. [단계별 설정 가이드](#단계별-설정-가이드)
3. [문제 해결](#문제-해결)
4. [설정 확인](#설정-확인)

---

## 시작하기 전에

### 필수 조건

- ✅ Python 3.8+ 설치됨
- ✅ AI4PKM CLI 설치됨 (`pip install -e .`)
- ✅ Claude Code 또는 Gemini CLI 설치됨
- ✅ 가상 환경 활성화됨

### 준비물

1. **Executor 경로 확인**:
   ```powershell
   where claude
   # 또는
   where gemini
   ```

   출력 예시:
   ```
   C:\Users\YourName\AppData\Roaming\npm\claude.cmd
   ```

2. **작업 디렉터리 선택**:
   - AI4PKM 설정을 적용할 폴더 결정
   - 예: `C:\Projects\MyPKM\`

---

## 단계별 설정 가이드

### Step 1: orchestrator.yaml 파일 생성

작업 디렉터리에 `orchestrator.yaml` 파일을 생성합니다.

```yaml
# AI4PKM Orchestrator Configuration
version: "1.0"

# Orchestrator runtime settings
orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"
  skills_dir: "_Settings_/Skills"
  bases_dir: "_Settings_/Bases"
  max_concurrent: 3
  poll_interval: 1.0

  # Windows executor paths (필수!)
  executors:
    claude_code:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\gemini.cmd"

# Global defaults for all agents
defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3
  task_create: true
  task_priority: medium
  task_archived: false

# 에이전트 정의는 다음 단계에서 추가
nodes: []
```

**중요**:
- `C:\\Users\\YourName\\` 부분을 실제 경로로 변경
- 백슬래시(`\`)를 두 번(`\\`) 사용
- 사용하지 않는 executor는 삭제해도 됨

---

### Step 2: 폴더 구조 생성

다음 폴더들을 생성합니다:

```powershell
mkdir _Settings_\Prompts
mkdir _Settings_\Tasks
mkdir _Settings_\Logs
mkdir _Settings_\Skills
mkdir _Settings_\Bases
```

또는 Git Bash:
```bash
mkdir -p _Settings_/{Prompts,Tasks,Logs,Skills,Bases}
```

---

### Step 3: 첫 번째 에이전트 생성

#### 3.1 orchestrator.yaml에 에이전트 추가

`nodes:` 섹션을 다음과 같이 수정:

```yaml
nodes:
  # 테스트 에이전트
  - type: agent
    name: Test Agent (TA)
    abbreviation: "ta"           # 필수!
    executor: claude_code        # 필수!
    input_path: input
    output_path: output
    output_type: new_file
```

**필수 필드 확인**:
- ✅ `name`: 에이전트 이름 (프롬프트 파일명과 동일)
- ✅ `abbreviation`: 명령어에서 사용할 약어
- ✅ `executor`: 사용할 AI executor
- ✅ `input_path`: 입력 파일을 감시할 폴더
- ✅ `output_path`: 결과를 저장할 폴더

#### 3.2 프롬프트 파일 생성

`_Settings_/Prompts/Test Agent (TA).md` 파일 생성:

```markdown
---
title: Test Agent (TA)
abbreviation: TA
category: test
---

This is a test agent for AI4PKM.

## Input
- Source: input/*.md
- Any markdown files

## Output
- File: output/{{filename}}_processed.md
- Processed markdown

## Main Process
```
1. READ INPUT
   - Read the input file
   - Understand the content

2. PROCESS
   - Add a header
   - Add a timestamp
   - Format nicely

3. SAVE OUTPUT
   - Save to output folder
```

## Output Format
```markdown
# Processed: [Original Title]

**Processed at**: {{timestamp}}

[Original Content]

---

**Processed by**: Test Agent (TA)
```
```

**중요**:
- 파일명이 `orchestrator.yaml`의 `name`과 **정확히 일치**해야 함
- YAML 프론트매터 (---로 감싼 부분) 필수
- 최소 30-50줄 이상의 내용 권장

#### 3.3 입출력 폴더 생성

```powershell
mkdir input
mkdir output
```

---

### Step 4: 설정 확인

#### 4.1 작업 디렉터리로 이동

```powershell
cd C:\Projects\MyPKM
```

**중요**: `orchestrator.yaml`이 있는 디렉터리에서 실행해야 함!

#### 4.2 설정 파일 확인

```powershell
ai4pkm --show-config
```

**성공 시 출력**:
```
╭─ Configuration (C:\Projects\MyPKM\orchestrator.yaml) ─╮
│ Orchestrator Settings:                                │
│   prompts_dir: _Settings_/Prompts                     │
│   ...                                                 │
│ Configured Agents: 1                                  │
│   • Test Agent (TA)                                   │
╰───────────────────────────────────────────────────────╯
```

#### 4.3 에이전트 목록 확인

```powershell
ai4pkm --list-agents
```

**성공 시 출력**:
```
                    Available Agents
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ Abbreviation ┃ Name           ┃ Category┃ Input Path┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ TA           │ Test Agent (TA)│ test    │ input     │
└──────────────┴────────────────┴─────────┴───────────┘
```

✅ **설정 완료!** 에이전트가 표시되면 성공입니다.

---

## 문제 해결

### 문제 1: "No configuration found"

**증상**:
```powershell
ai4pkm --show-config
# No configuration found.
```

**원인**: 잘못된 디렉터리에서 실행

**해결**:
```powershell
# orchestrator.yaml이 있는 디렉터리로 이동
cd C:\Projects\MyPKM

# 또는 --working-dir 사용
ai4pkm --working-dir C:\Projects\MyPKM --show-config
```

---

### 문제 2: "No agents found"

**증상**:
```powershell
ai4pkm --list-agents
# No agents found.
```

**원인 1**: 에이전트 정의 불완전

**해결**: `orchestrator.yaml` 확인
```yaml
nodes:
  - type: agent
    name: Test Agent (TA)
    abbreviation: "ta"        # 이 줄 있나요?
    executor: claude_code     # 이 줄 있나요?
    input_path: input
    output_path: output
```

**원인 2**: 프롬프트 파일 문제

**해결**: 다음 사항 확인
1. 파일명이 `name` 필드와 정확히 일치하는가?
   - `Test Agent (TA).md` ✅
   - `test_agent.md` ❌
2. YAML 프론트매터가 있는가?
   ```markdown
   ---
   title: Test Agent (TA)
   abbreviation: TA
   category: test
   ---
   ```
3. 파일 크기가 충분한가?
   - 최소 50줄 이상 권장

---

### 문제 3: Executor를 찾을 수 없음

**증상**:
에이전트 실행 시 executor 오류

**원인**: executor 경로 오류

**해결**:
1. **경로 확인**:
   ```powershell
   where claude
   ```

2. **orchestrator.yaml 수정**:
   ```yaml
   orchestrator:
     executors:
       claude_code:
         command: "실제경로를입력하세요.cmd"
   ```

3. **경로 형식 주의**:
   - ✅ `"C:\\Users\\Name\\AppData\\Roaming\\npm\\claude.cmd"`
   - ❌ `"C:\Users\Name\AppData\Roaming\npm\claude.cmd"` (백슬래시 1개)
   - ❌ `C:\\Users\\Name\\AppData\\Roaming\\npm\\claude.cmd` (따옴표 없음)

---

## 설정 확인 체크리스트

설정이 완료되었는지 다음 항목을 확인하세요:

- [ ] `orchestrator.yaml` 파일이 작업 디렉터리에 있음
- [ ] Executor 경로가 올바르게 설정됨 (`where claude`로 확인)
- [ ] `_Settings_/Prompts/` 폴더가 생성됨
- [ ] 프롬프트 파일이 올바른 이름으로 생성됨
- [ ] 프롬프트 파일에 YAML 프론트매터가 있음
- [ ] `orchestrator.yaml`의 `nodes` 섹션에 에이전트 정의됨
- [ ] 에이전트 정의에 `abbreviation`, `executor` 필드 포함
- [ ] `ai4pkm --show-config` 명령이 성공
- [ ] `ai4pkm --list-agents` 명령이 에이전트를 표시

모든 항목이 체크되면 ✅ **설정 완료**입니다!

---

## 다음 단계

설정이 완료되면 다음을 시도해 보세요:

1. **테스트 파일 생성**:
   ```powershell
   echo "# Test Content" > input\test.md
   ```

2. **에이전트 수동 실행**:
   ```powershell
   ai4pkm -t ta
   ```

3. **결과 확인**:
   ```powershell
   cat output\test_processed.md
   ```

---

## 참고 자료

- [01_directory_structure.md](../01-AI4PKM_CLI_Structure/01_directory_structure.md) - AI4PKM 구조
- [02_command_cheatsheet.md](./02_command_cheatsheet.md) - 명령어 레퍼런스
- [03_config_file_guide.md](../01-AI4PKM_CLI_Structure/03_config_file_guide.md) - 설정 파일 상세 가이드

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-12-12
**테스트 환경**: Windows 11, Python 3.13.3, AI4PKM 최신 버전
