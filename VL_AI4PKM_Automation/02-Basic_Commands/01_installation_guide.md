# AI4PKM CLI 설치 가이드 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI는 개인 지식 관리(PKM)를 자동화하는 Python 기반 명령줄 도구입니다. 이 가이드는 Windows, macOS, Linux 환경에서 AI4PKM CLI를 설치하고 설정하는 방법을 단계별로 안내합니다.

---

## 📋 목차
1. [필수 요구사항](#필수-요구사항)
2. [설치 방법](#설치-방법)
3. [Executor 설치](#executor-설치)
4. [초기 설정](#초기-설정)
5. [설치 확인](#설치-확인)
6. [문제 해결](#문제-해결)

---

## 필수 요구사항

### 시스템 요구사항
- **Python**: 3.8 이상 (권장: 3.10 이상)
- **운영체제**:
  - Windows 10/11
  - macOS 10.15+ (일부 기능은 macOS 전용)
  - Linux (Ubuntu 20.04+)
- **저장 공간**: 최소 100MB (의존성 패키지 포함)
- **Obsidian**: PKM Vault로 사용 (선택 사항이지만 권장)

### Python 버전 확인

설치 전 Python 버전을 확인하세요:

**Windows (PowerShell):**
```powershell
python --version
```

**macOS/Linux (Terminal):**
```bash
python3 --version
```

**예상 출력**:
```
Python 3.13.3
```

Python 3.8 이상이 설치되어 있어야 합니다. 설치되어 있지 않다면:
- **Windows**: [python.org](https://www.python.org/downloads/)에서 다운로드
- **macOS**: `brew install python3` (Homebrew 사용)
- **Linux**: `sudo apt install python3 python3-pip`

---

## 설치 방법

### 방법 1: GitHub에서 클론 (권장)

**1. 저장소 클론**

```bash
# AI4PKM 저장소 클론
git clone https://github.com/jykim/AI4PKM.git
cd AI4PKM
```

**2. 개발 모드로 설치**

이 방법은 코드를 수정하면 즉시 반영됩니다.

**Windows:**
```powershell
# 가상 환경 생성 (선택 사항)
python -m venv venv
.\venv\Scripts\activate

# 개발 모드 설치
pip install -e .
```

**macOS/Linux:**
```bash
# 가상 환경 생성 (선택 사항)
python3 -m venv venv
source venv/bin/activate

# 개발 모드 설치
pip install -e .
```

**설치 확인**:
```bash
ai4pkm --help
```

---

### 방법 2: pip로 직접 설치 (향후 지원 예정)

```bash
# PyPI에서 설치 (향후 지원)
pip install ai4pkm-cli
```

---

## Executor 설치

AI4PKM은 AI executor를 통해 작동합니다. 최소 1개 이상 설치 필요합니다.

### 1. Claude Code (권장)

**설치**:
```bash
npm install -g @anthropic-ai/claude-code
```

**확인**:
```bash
claude --version
```

**인증**:
Claude Code CLI를 처음 실행하면 자동으로 인증 프로세스가 시작됩니다.

**참고**: [Claude Code 공식 문서](https://docs.anthropic.com/claude-code)

---

### 2. Google Gemini CLI (선택)

**설치**:
```bash
npm install -g @google/generative-ai-cli
```

**확인**:
```bash
gemini --version
```

**인증**:
```bash
gemini auth login
```

---

### 3. OpenAI Codex (선택)

**설치**:
```bash
npm install -g openai-cli
```

**API 키 설정** (secrets.yaml):
```yaml
openai:
  api_key: "sk-xxxxxxxx"
```

---

### Windows 사용자: Executor 경로 설정

Windows에서 npm 글로벌 설치 경로가 PATH에 없을 수 있습니다.

**경로 확인**:
```powershell
npm config get prefix
```

**예상 출력**:
```
C:\Users\YourName\AppData\Roaming\npm
```

**orchestrator.yaml에 명시적 경로 설정**:
```yaml
orchestrator:
  executors:
    claude:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\gemini.cmd"
```

---

## 초기 설정

### 1. Vault 디렉터리 준비

AI4PKM은 Obsidian Vault와 함께 작동합니다.

**옵션 A: 예제 Vault 사용**
```bash
cd AI4PKM/ai4pkm_vault
```

**옵션 B: 기존 Vault 사용**
```bash
cd /path/to/your/obsidian/vault
```

---

### 2. orchestrator.yaml 생성

**예제 복사**:
```bash
# 예제 Vault에서 복사
cp AI4PKM/ai4pkm_vault/orchestrator.yaml /path/to/your/vault/

# 또는 수동 생성
touch orchestrator.yaml
```

**최소 설정** (`orchestrator.yaml`):
```yaml
version: "1.0"

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"
  max_concurrent: 2

defaults:
  executor: claude_code
  timeout_minutes: 30

nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    output_type: new_file

pollers: {}
```

---

### 3. Vault 폴더 구조 생성

필수 폴더를 생성하세요:

```bash
# Vault 루트에서 실행
mkdir -p _Settings_/Prompts
mkdir -p _Settings_/Tasks
mkdir -p _Settings_/Logs
mkdir -p Ingest/Clippings
mkdir -p AI/Articles
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "_Settings_\Prompts"
New-Item -ItemType Directory -Force -Path "_Settings_\Tasks"
New-Item -ItemType Directory -Force -Path "_Settings_\Logs"
New-Item -ItemType Directory -Force -Path "Ingest\Clippings"
New-Item -ItemType Directory -Force -Path "AI\Articles"
```

---

### 4. 프롬프트 파일 생성

에이전트 프롬프트를 생성하세요.

**예**: `_Settings_/Prompts/EIC.md`
```markdown
# Enrich Ingested Content (EIC)

You are an AI assistant specialized in enriching web clippings and articles.

## Task
- Read the input file
- Add summary, key points, and tags
- Improve formatting
- Save to output path

## Output Format
Use Markdown with frontmatter:
```yaml
---
title: [Title]
tags: [tag1, tag2]
created: [ISO date]
---

[Enriched content]
```
```

---

## 설치 확인

### 1. CLI 설치 확인

```bash
ai4pkm --help
```

**예상 출력**:
```
Usage: ai4pkm [OPTIONS]

  AI4PKM CLI - Personal Knowledge Management framework.

Options:
  -o, --orchestrator       Run orchestrator mode
  -l, --list-agents        List all available agents
  --show-config            Show current configuration
  -d, --debug              Enable debug logging
  --help                   Show this message and exit.
```

---

### 2. Executor 설치 확인

```bash
# Claude Code
claude --version

# Gemini (선택)
gemini --version
```

---

### 3. 설정 확인

```bash
cd /path/to/your/vault
ai4pkm --show-config
```

**예상 출력**:
```yaml
Configuration:
  Vault Path: /path/to/your/vault
  Prompts Dir: _Settings_/Prompts
  Tasks Dir: _Settings_/Tasks
  Max Concurrent: 2

Agents:
  1. Enrich Ingested Content (EIC)
     - Executor: claude_code
     - Input: Ingest/Clippings
     - Output: AI/Articles
```

---

### 4. Orchestrator 실행 테스트

```bash
cd /path/to/your/vault
ai4pkm orchestrator run
```

**예상 출력**:
```
[2025-12-03 08:00:00] Orchestrator starting...
[2025-12-03 08:00:00] Monitoring: Ingest/Clippings
[2025-12-03 08:00:00] Orchestrator running. Press Ctrl+C to stop.
```

Ctrl+C로 중지하세요.

---

## 문제 해결

### 문제 1: `ai4pkm` 명령어를 찾을 수 없음

**증상**:
```
ai4pkm: command not found
```

**해결 방법**:

**Windows:**
```powershell
# Python Scripts 폴더가 PATH에 있는지 확인
$env:PATH
# 없다면 추가
$env:PATH += ";C:\Python313\Scripts"
```

**macOS/Linux:**
```bash
# pip 사용자 bin 폴더 확인
echo $PATH
# 없다면 ~/.bashrc 또는 ~/.zshrc에 추가
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

---

### 문제 2: Windows에서 executor를 찾을 수 없음

**증상**:
```
ERROR: Could not resolve path for executor: claude
```

**해결 방법**:

`orchestrator.yaml`에 명시적 경로 설정:

```yaml
orchestrator:
  executors:
    claude:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
```

**경로 찾기**:
```powershell
where.exe claude
# 출력: C:\Users\YourName\AppData\Roaming\npm\claude.cmd
```

---

### 문제 3: Python 버전이 낮음

**증상**:
```
ERROR: Python 3.8 or higher is required
```

**해결 방법**:

1. Python 최신 버전 설치: https://www.python.org/downloads/
2. 설치 시 "Add Python to PATH" 체크
3. 재설치:
```bash
pip install -e .
```

---

### 문제 4: 의존성 설치 실패

**증상**:
```
ERROR: Could not install package: watchdog
```

**해결 방법**:

**Windows:**
```powershell
# Visual C++ Build Tools 설치 필요
# https://visualstudio.microsoft.com/downloads/
# "Desktop development with C++" 선택

# 재시도
pip install -e .
```

**macOS:**
```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 재시도
pip install -e .
```

**Linux:**
```bash
# 빌드 도구 설치
sudo apt install build-essential python3-dev

# 재시도
pip install -e .
```

---

### 문제 5: orchestrator.yaml 파일을 찾을 수 없음

**증상**:
```
ERROR: orchestrator.yaml not found in current directory
```

**해결 방법**:

1. Vault 디렉터리로 이동:
```bash
cd /path/to/your/vault
```

2. `orchestrator.yaml` 파일이 있는지 확인:
```bash
ls orchestrator.yaml
```

3. 없다면 생성:
```bash
cp /path/to/AI4PKM/ai4pkm_vault/orchestrator.yaml .
```

---

### 문제 6: Permission denied (macOS/Linux)

**증상**:
```
PermissionError: [Errno 13] Permission denied
```

**해결 방법**:

```bash
# pip 사용자 설치
pip install --user -e .

# 또는 sudo 사용 (권장하지 않음)
sudo pip install -e .
```

---

## 다음 단계

설치가 완료되었다면:

1. **[02_command_cheatsheet.md](./02_command_cheatsheet.md)**: 명령어 치트시트
2. **[03_quick_start_guide.md](./03_quick_start_guide.md)**: 빠른 시작 가이드
3. **[../01-AI4PKM_CLI_Structure/03_config_file_guide.md](../01-AI4PKM_CLI_Structure/03_config_file_guide.md)**: 설정 파일 가이드

---

## 추가 리소스

- **공식 GitHub**: https://github.com/jykim/AI4PKM
- **문서**: [AI4PKM Documentation](../01-AI4PKM_CLI_Structure/)
- **Issue 보고**: https://github.com/jykim/AI4PKM/issues

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
