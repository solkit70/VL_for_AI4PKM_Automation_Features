# AI4PKM CLI 명령어 치트시트 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI의 모든 명령어와 옵션을 빠르게 참조할 수 있는 치트시트입니다.

---

## 📋 목차
1. [기본 명령어](#기본-명령어)
2. [Orchestrator 명령어](#orchestrator-명령어)
3. [에이전트 관련 명령어](#에이전트-관련-명령어)
4. [설정 및 정보](#설정-및-정보)
5. [디버깅 및 로깅](#디버깅-및-로깅)
6. [실전 예제](#실전-예제)

---

## 기본 명령어

### 도움말

```bash
# 전체 도움말 보기
ai4pkm --help
ai4pkm -h

# 버전 정보 (미래 버전)
ai4pkm --version
```

**출력 예**:
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

## Orchestrator 명령어

Orchestrator는 파일 감시, 에이전트 자동 실행, 스케줄링을 담당하는 핵심 시스템입니다.

### Orchestrator 실행

```bash
# Orchestrator 시작 (파일 감시 모드)
ai4pkm orchestrator run
ai4pkm -o

# 디버그 모드로 실행
ai4pkm orchestrator run --debug
ai4pkm -o -d
```

**동작**:
- `orchestrator.yaml`의 `input_path` 폴더 감시 시작
- 파일 생성/수정 감지 → 자동 에이전트 실행
- Cron 스케줄에 따라 주기적 에이전트 실행
- Poller 시작 (외부 데이터 동기화)

**종료**: `Ctrl+C`

**로그 출력 예**:
```
[2025-12-03 08:00:00] Orchestrator starting...
[2025-12-03 08:00:00] Loading agents from orchestrator.yaml
[2025-12-03 08:00:00] Registered agent: Enrich Ingested Content (EIC)
[2025-12-03 08:00:00] Monitoring: Ingest/Clippings
[2025-12-03 08:00:00] Orchestrator running. Press Ctrl+C to stop.
```

---

### Orchestrator 상태 확인

```bash
# 실행 중인 Orchestrator 상태
ai4pkm orchestrator status
```

**출력 예**:
```
Orchestrator Status: Running
PID: 12345
Uptime: 2 hours 15 minutes
Active agents: 3
Monitored paths: 2
```

---

### Orchestrator 중지

```bash
# Orchestrator 종료
ai4pkm orchestrator stop
```

---

## 에이전트 관련 명령어

### 에이전트 목록 조회

```bash
# 사용 가능한 에이전트 목록
ai4pkm list-agents
ai4pkm -l
```

**출력 예**:
```
Available Agents:
  1. Enrich Ingested Content (EIC)
     - Executor: claude_code
     - Input: Ingest/Clippings
     - Output: AI/Articles
     - Status: Active

  2. Generate Daily Roundup (GDR)
     - Executor: claude_code
     - Cron: 0 1 * * * (Daily at 1 AM)
     - Output: AI/Roundup
     - Status: Scheduled

  3. Create Thread Postings (CTP)
     - Executor: claude_code
     - Input: AI/Articles
     - Output: AI/Sharable
     - Status: Active
```

---

### 에이전트 수동 실행

```bash
# 특정 에이전트 수동 트리거 (batch 모드)
ai4pkm trigger-agent "GDR"
ai4pkm trigger-agent "Generate Daily Roundup (GDR)"

# 특정 파일에 대해 에이전트 실행
ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/article.md"
```

**사용 예**:
```bash
# 데일리 라운드업을 지금 바로 실행
ai4pkm trigger-agent "GDR"

# 특정 클리핑 파일 처리
ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/my-article.md"
```

---

## 설정 및 정보

### 설정 조회

```bash
# 현재 설정 표시
ai4pkm show-config
ai4pkm --show-config
```

**출력 예**:
```yaml
Configuration:
  Vault Path: /Users/username/Documents/MyVault
  Prompts Dir: _Settings_/Prompts
  Tasks Dir: _Settings_/Tasks
  Logs Dir: _Settings_/Logs
  Max Concurrent: 3

Defaults:
  Executor: claude_code
  Timeout: 30 minutes

Agents:
  - Enrich Ingested Content (EIC)
  - Generate Daily Roundup (GDR)
  - Create Thread Postings (CTP)

Pollers:
  - gobi (enabled, 3600s interval)
  - limitless (enabled, 3600s interval)
```

---

### 버전 정보

```bash
# CLI 버전 (향후 지원)
ai4pkm --version

# Executor 버전 확인
claude --version
gemini --version
```

---

## 디버깅 및 로깅

### 디버그 모드

```bash
# 디버그 로그 활성화
ai4pkm orchestrator run --debug
ai4pkm -o -d
```

**디버그 출력 예**:
```
[DEBUG] Loading orchestrator.yaml
[DEBUG] Parsing nodes section
[DEBUG] Found agent: EIC
[DEBUG] Input path: Ingest/Clippings
[DEBUG] Resolved executor: C:\Users\...\npm\claude.cmd
[DEBUG] Starting file monitor
[DEBUG] Watching: C:\Users\...\MyVault\Ingest\Clippings
[INFO] Orchestrator running
```

---

### 로그 파일 확인

```bash
# 로그 파일 위치
cat _Settings_/Logs/ai4pkm.log

# 실시간 로그 모니터링
tail -f _Settings_/Logs/ai4pkm.log
```

**Windows:**
```powershell
Get-Content _Settings_\Logs\ai4pkm.log -Tail 50 -Wait
```

---

## 실전 예제

### 예제 1: 기본 워크플로우

```bash
# 1. Vault 디렉터리로 이동
cd /path/to/your/vault

# 2. 설정 확인
ai4pkm show-config

# 3. Orchestrator 시작
ai4pkm orchestrator run

# (별도 터미널에서)
# 4. 웹 클리핑 저장
echo "# My Article" > Ingest/Clippings/article.md

# → EIC 에이전트가 자동 실행됨
# → AI/Articles/article-enriched.md 생성됨
```

---

### 예제 2: 디버그 모드로 문제 해결

```bash
# 1. 디버그 모드로 Orchestrator 실행
ai4pkm orchestrator run --debug

# 2. 로그 확인
# - Executor 경로 확인
# - 파일 감지 확인
# - 에러 메시지 확인
```

---

### 예제 3: 수동 에이전트 실행

```bash
# 1. 에이전트 목록 확인
ai4pkm list-agents

# 2. 데일리 라운드업 수동 실행
ai4pkm trigger-agent "GDR"

# 3. 결과 확인
ls AI/Roundup/
```

---

### 예제 4: Windows 환경 설정

```powershell
# 1. Vault로 이동
cd C:\Users\YourName\Documents\MyVault

# 2. Executor 경로 확인
where.exe claude
# 출력: C:\Users\YourName\AppData\Roaming\npm\claude.cmd

# 3. orchestrator.yaml 편집
notepad orchestrator.yaml

# executors 섹션 추가:
# orchestrator:
#   executors:
#     claude:
#       command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"

# 4. Orchestrator 실행
ai4pkm orchestrator run
```

---

### 예제 5: Cron 스케줄링 테스트

```bash
# 1. orchestrator.yaml에 cron 에이전트 추가
# nodes:
#   - name: Generate Daily Roundup (GDR)
#     cron: "0 1 * * *"  # 매일 새벽 1시
#     output_path: AI/Roundup

# 2. 수동으로 테스트
ai4pkm trigger-agent "GDR"

# 3. Orchestrator 시작 (cron 활성화)
ai4pkm orchestrator run

# → 매일 새벽 1시에 자동 실행됨
```

---

### 예제 6: 멀티 에이전트 파이프라인

```bash
# orchestrator.yaml 설정:
# nodes:
#   - name: EIC
#     input_path: Ingest/Clippings
#     output_path: AI/Articles
#
#   - name: CTP
#     input_path: AI/Articles
#     output_path: AI/Sharable

# 실행:
ai4pkm orchestrator run

# 워크플로우:
# 1. Ingest/Clippings/article.md 생성
# 2. EIC가 자동 실행 → AI/Articles/article-enriched.md 생성
# 3. CTP가 자동 실행 → AI/Sharable/article-thread.md 생성
```

---

## 명령어 요약표

| 명령어 | 짧은 형식 | 설명 |
|--------|----------|------|
| `ai4pkm --help` | `-h` | 도움말 표시 |
| `ai4pkm orchestrator run` | `-o` | Orchestrator 시작 |
| `ai4pkm list-agents` | `-l` | 에이전트 목록 |
| `ai4pkm show-config` | - | 설정 조회 |
| `ai4pkm --debug` | `-d` | 디버그 모드 |
| `ai4pkm orchestrator status` | - | Orchestrator 상태 |
| `ai4pkm orchestrator stop` | - | Orchestrator 중지 |
| `ai4pkm trigger-agent` | - | 에이전트 수동 실행 |

---

## 일반적인 사용 패턴

### 패턴 1: 개발/테스트

```bash
# 1. 디버그 모드로 시작
ai4pkm orchestrator run --debug

# 2. 에러 발생 시 로그 확인
cat _Settings_/Logs/ai4pkm.log

# 3. 설정 수정
vim orchestrator.yaml

# 4. 재시작 (Ctrl+C 후)
ai4pkm orchestrator run --debug
```

---

### 패턴 2: 프로덕션 실행

```bash
# 1. 설정 확인
ai4pkm show-config

# 2. 에이전트 확인
ai4pkm list-agents

# 3. Orchestrator 시작 (백그라운드)
nohup ai4pkm orchestrator run > orchestrator.log 2>&1 &

# 4. 상태 확인
ai4pkm orchestrator status

# 5. 로그 모니터링
tail -f orchestrator.log
```

**Windows (백그라운드 실행):**
```powershell
# PowerShell에서 백그라운드 작업
Start-Process -NoNewWindow ai4pkm -ArgumentList "orchestrator","run"
```

---

### 패턴 3: 일회성 작업

```bash
# 수동 에이전트 실행 (Orchestrator 없이)
ai4pkm trigger-agent "GDR"
ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/article.md"
```

---

## 환경 변수

일부 설정은 환경 변수로 오버라이드 가능합니다:

```bash
# Vault 경로 지정
export AI4PKM_VAULT_PATH="/path/to/vault"
ai4pkm orchestrator run

# 디버그 레벨
export AI4PKM_DEBUG=1
ai4pkm orchestrator run

# Executor 경로 (대안)
export CLAUDE_PATH="/usr/local/bin/claude"
export GEMINI_PATH="/usr/local/bin/gemini"
```

**Windows:**
```powershell
$env:AI4PKM_VAULT_PATH = "C:\Users\...\MyVault"
$env:AI4PKM_DEBUG = "1"
ai4pkm orchestrator run
```

---

## 단축키 (Orchestrator 실행 중)

| 키 | 동작 |
|----|------|
| `Ctrl+C` | Orchestrator 종료 |
| `Ctrl+Z` | 일시 중지 (백그라운드로 이동) |

---

## 다음 단계

- **[01_installation_guide.md](./01_installation_guide.md)**: 설치 가이드
- **[03_quick_start_guide.md](./03_quick_start_guide.md)**: 빠른 시작 가이드
- **[../01-AI4PKM_CLI_Structure/03_config_file_guide.md](../01-AI4PKM_CLI_Structure/03_config_file_guide.md)**: 설정 파일 가이드

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
