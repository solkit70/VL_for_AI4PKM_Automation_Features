# AI4PKM CLI 설정 파일 가이드 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI는 `orchestrator.yaml` 설정 파일로 동작을 제어합니다. 이 문서는 설정 항목을 상세히 설명합니다.

---

## 📋 목차
1. [설정 파일 위치](#설정-파일-위치)
2. [전체 구조 개요](#전체-구조-개요)
3. [Orchestrator 설정](#orchestrator-설정)
4. [Defaults 설정](#defaults-설정)
5. [Nodes (에이전트) 설정](#nodes-에이전트-설정)
6. [Pollers 설정](#pollers-설정)
7. [Secrets 관리](#secrets-관리)
8. [실전 예제](#실전-예제)

---

## 설정 파일 위치

### orchestrator.yaml (필수)
- **위치**: Obsidian Vault 루트 디렉터리
- **경로 예**: `/path/to/your/vault/orchestrator.yaml`
- **예제**: `ai4pkm_vault/orchestrator.yaml` 참조

```bash
# 설정 파일 생성 (예제 복사)
cp ai4pkm_vault/orchestrator.yaml /path/to/your/vault/

# Vault 디렉터리로 이동
cd /path/to/your/vault

# Orchestrator 실행
ai4pkm orchestrator run

# 설정 확인
ai4pkm show-config
```

### secrets.yaml (선택)
- **위치**: Vault 루트 디렉터리
- **역할**: API 키 및 민감 정보 저장
- **주의**: `.gitignore`에 추가 필수!

**예제**:
```yaml
# secrets.yaml
gobi:
  api_key: "your-gobi-api-key"
  user_id: "your-user-id"

limitless:
  api_key: "your-limitless-api-key"
```

---

## 전체 구조 개요

```yaml
# orchestrator.yaml

version: "1.0"

# 1. Orchestrator 런타임 설정
orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"
  skills_dir: "_Settings_/Skills"
  bases_dir: "_Settings_/Bases"
  max_concurrent: 3
  poll_interval: 1.0

# 2. 에이전트 기본 설정
defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3
  task_create: true
  task_priority: medium
  task_archived: false

# 3. 에이전트 정의 (핵심)
nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    ...

# 4. 외부 데이터 동기화
pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600
  ...
```

---

## Orchestrator 설정

`orchestrator` 섹션은 Orchestrator의 런타임 동작을 제어합니다.

### 전체 옵션

```yaml
orchestrator:
  prompts_dir: "_Settings_/Prompts"    # 프롬프트 파일 위치
  tasks_dir: "_Settings_/Tasks"        # 태스크 파일 저장 위치
  logs_dir: "_Settings_/Logs"          # 로그 파일 저장 위치
  skills_dir: "_Settings_/Skills"      # Claude Code Skills (MCP)
  bases_dir: "_Settings_/Bases"        # 프롬프트 기반 지식
  max_concurrent: 3                     # 최대 동시 실행 수
  poll_interval: 1.0                    # 파일 감시 폴링 간격 (초)

  # 선택 항목 (Windows 사용자)
  executors:
    claude:
      command: "C:\\Users\\username\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\username\\AppData\\Roaming\\npm\\gemini.cmd"
```

### 옵션 상세

#### prompts_dir
- **타입**: `string`
- **기본값**: `"_Settings_/Prompts"`
- **설명**: 에이전트 프롬프트 `.md` 파일이 저장된 디렉터리
- **예**: `_Settings_/Prompts/EIC.md`, `_Settings_/Prompts/GDR.md`

#### tasks_dir
- **타입**: `string`
- **기본값**: `"_Settings_/Tasks"`
- **설명**: 생성된 태스크 파일 저장 위치
- **예**: `_Settings_/Tasks/2025-12-03-EIC-article.md`

#### logs_dir
- **타입**: `string`
- **기본값**: `"_Settings_/Logs"`
- **설명**: Orchestrator 실행 로그 저장 위치
- **예**: `_Settings_/Logs/ai4pkm.log`

#### skills_dir
- **타입**: `string`
- **기본값**: `"_Settings_/Skills"`
- **설명**: Claude Code MCP Skills 디렉터리
- **예**: `_Settings_/Skills/obsidian-links/`

#### bases_dir
- **타입**: `string`
- **기본값**: `"_Settings_/Bases"`
- **설명**: Dataview 쿼리로 프롬프트에 주입할 기반 지식
- **예**: `_Settings_/Bases/AI4PKM Prompts.base`

#### max_concurrent
- **타입**: `integer`
- **기본값**: `3`
- **설명**: 동시에 실행 가능한 최대 에이전트 수
- **권장**: CPU 코어 수의 50-75%

#### poll_interval
- **타입**: `float`
- **기본값**: `1.0`
- **단위**: 초
- **설명**: 파일 시스템 감시 폴링 간격

#### executors (선택)
- **타입**: `dict`
- **설명**: Windows 환경에서 executor 경로 명시적 지정
- **이유**: Windows npm 설치 경로가 PATH에 없을 수 있음

**Windows 사용자 설정 예**:
```yaml
orchestrator:
  executors:
    claude:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\gemini.cmd"
```

---

## Defaults 설정

`defaults` 섹션은 모든 에이전트의 기본 설정입니다. 각 에이전트에서 오버라이드 가능합니다.

### 전체 옵션

```yaml
defaults:
  executor: claude_code          # 기본 AI executor
  timeout_minutes: 30            # 타임아웃 (분)
  max_parallel: 3                # 에이전트별 최대 병렬 실행 수
  task_create: true              # 태스크 파일 생성 여부
  task_priority: medium          # 태스크 우선순위
  task_archived: false           # 완료된 태스크 아카이브 여부
```

### 옵션 상세

#### executor
- **타입**: `string`
- **옵션**: `claude_code`, `gemini`, `codex`
- **기본값**: `claude_code`
- **설명**: 사용할 AI executor

**Executor 비교**:
| Executor | 장점 | 단점 |
|----------|------|------|
| `claude_code` | Claude Code SDK, 파일 작업 강력 | 별도 설치 필요 |
| `gemini` | Google Gemini, 빠른 응답 | CLI 별도 설치 |
| `codex` | OpenAI Codex, 코드 생성 특화 | API 키 필요 |

#### timeout_minutes
- **타입**: `integer`
- **기본값**: `30`
- **단위**: 분
- **설명**: Executor 실행 타임아웃

#### max_parallel
- **타입**: `integer`
- **기본값**: `3`
- **설명**: 동일한 에이전트의 동시 실행 수 제한

#### task_create
- **타입**: `boolean`
- **기본값**: `true`
- **설명**: 태스크 파일 생성 여부

#### task_priority
- **타입**: `string`
- **옵션**: `high`, `medium`, `low`
- **기본값**: `medium`
- **설명**: 생성되는 태스크의 우선순위

#### task_archived
- **타입**: `boolean`
- **기본값**: `false`
- **설명**: 완료된 태스크를 `_Archive_`로 이동할지 여부

---

## Nodes (에이전트) 설정

`nodes` 섹션은 에이전트를 정의합니다. 각 노드는 **파일 입력 → AI 처리 → 파일 출력** 파이프라인입니다.

### 에이전트 기본 구조

```yaml
nodes:
  - type: agent                          # 고정값: "agent"
    name: Enrich Ingested Content (EIC)  # 에이전트 이름
    input_path: Ingest/Clippings         # 입력 경로
    output_path: AI/Articles             # 출력 경로
    output_type: new_file                # 출력 타입

    # 선택 항목 (defaults에서 오버라이드)
    executor: claude_code
    timeout_minutes: 30
    max_parallel: 3
    task_create: true
    task_priority: high

    # Cron 스케줄링 (선택)
    cron: "0 1 * * *"                    # 매일 새벽 1시
```

### 필수 필드

#### type
- **타입**: `string`
- **값**: `"agent"` (고정)
- **설명**: 노드 타입

#### name
- **타입**: `string`
- **예**: `"Enrich Ingested Content (EIC)"`
- **설명**: 에이전트 이름 (프롬프트 파일명과 매칭)
- **프롬프트 파일**: `_Settings_/Prompts/{name}.md`

#### input_path
- **타입**: `string` 또는 `list[string]`
- **예**:
  - 단일: `"Ingest/Clippings"`
  - 다중: `["AI/Articles", "AI/Roundup"]`
  - Glob 패턴: `"Ingest/Photolog/Processed/*.jpg"`
- **설명**: 감시할 파일 경로

#### output_path
- **타입**: `string`
- **예**: `"AI/Articles"`
- **설명**: 결과 파일 저장 위치

#### output_type
- **타입**: `string`
- **옵션**:
  - `new_file`: 새 파일 생성
  - `update_file`: 기존 파일 업데이트
- **기본값**: `new_file`

### 선택 필드

#### cron
- **타입**: `string`
- **형식**: Cron 표현식 (5개 필드)
- **예**:
  - `"0 1 * * *"`: 매일 새벽 1시
  - `"0 9 * * 1"`: 매주 월요일 오전 9시
  - `"*/30 * * * *"`: 30분마다
- **설명**: 주기적 실행 스케줄

**Cron 표현식 형식**:
```
┌───────────── 분 (0 - 59)
│ ┌───────────── 시 (0 - 23)
│ │ ┌───────────── 일 (1 - 31)
│ │ │ ┌───────────── 월 (1 - 12)
│ │ │ │ ┌───────────── 요일 (0 - 6) (일요일=0)
│ │ │ │ │
* * * * *
```

**예제**:
```yaml
nodes:
  - name: Generate Daily Roundup (GDR)
    cron: "0 1 * * *"  # 매일 새벽 1시
    output_path: AI/Roundup

  - name: Generate Weekly Roundup (GWR)
    cron: "0 9 * * 1"  # 매주 월요일 오전 9시
    output_path: AI/Roundup
```

### 에이전트 예제

#### 1. 웹 클리핑 enrichment (EIC)
```yaml
- type: agent
  name: Enrich Ingested Content (EIC)
  input_path: Ingest/Clippings
  output_path: AI/Articles
  output_type: new_file
  task_priority: high
```

**동작**:
1. `Ingest/Clippings/` 폴더 감시
2. 새 `.md` 파일 생성 감지
3. `_Settings_/Prompts/EIC.md` 프롬프트 사용
4. `claude` executor 실행
5. 결과를 `AI/Articles/`에 저장

#### 2. 소셜 미디어 포스팅 생성 (CTP)
```yaml
- type: agent
  name: Create Thread Postings (CTP)
  input_path:
    - AI/Articles
    - AI/Roundup
    - AI/Research
  output_path: AI/Sharable
  output_type: new_file
```

**동작**:
- 3개 폴더 동시 감시
- 파일 생성 시 소셜 미디어 포스팅 생성

#### 3. 데일리 라운드업 (GDR) - Cron
```yaml
- type: agent
  name: Generate Daily Roundup (GDR)
  cron: "0 1 * * *"  # 매일 새벽 1시
  output_path: AI/Roundup
  timeout_minutes: 45
```

**동작**:
- 매일 새벽 1시 자동 실행
- 파일 트리거 없이 배치 모드
- Journal/, Topics/ 등 전체 Vault 분석

#### 4. 사진 처리 (PPP) - Glob 패턴
```yaml
- type: agent
  name: Pick and Process Photos (PPP)
  input_path:
    - "Ingest/Photolog/Processed/*.jpg"
    - "Ingest/Photolog/Processed/*.jpeg"
    - "Ingest/Photolog/Processed/*.png"
    - "Ingest/Photolog/Processed/*.yaml"
  output_path: Ingest/Photolog
  output_type: new_file
```

**동작**:
- 사진 파일 + metadata.yaml 감시
- 조합하여 사진 로그 생성

---

## Pollers 설정

`pollers` 섹션은 외부 데이터 소스와 주기적으로 동기화합니다.

### 전체 구조

```yaml
pollers:
  poller_name:
    enabled: true
    target_dir: "Ingest/PollerName"
    poll_interval: 3600  # 초
    # ... 추가 설정
```

### 공통 필드

#### enabled
- **타입**: `boolean`
- **기본값**: `false`
- **설명**: Poller 활성화 여부

#### target_dir
- **타입**: `string`
- **설명**: 동기화된 데이터 저장 위치

#### poll_interval
- **타입**: `integer`
- **기본값**: `3600`
- **단위**: 초
- **설명**: 동기화 간격

---

### 1. Apple Photos Poller

**macOS 전용**: iCloud Photos 라이브러리와 동기화

```yaml
pollers:
  apple_photos:
    enabled: true
    target_dir: "Ingest/Photolog"
    poll_interval: 3600  # 1시간
    days: 7              # 최근 7일
```

**옵션**:
- `days`: 최근 며칠 사진 가져오기

**출력**:
- `Ingest/Photolog/*.jpg`: 사진 파일
- `Ingest/Photolog/metadata.yaml`: 사진 메타데이터

---

### 2. Apple Notes Poller

**macOS 전용**: Apple Notes 앱과 동기화

```yaml
pollers:
  apple_notes:
    enabled: true
    target_dir: "Ingest/Apple Notes"
    poll_interval: 1800  # 30분
```

**출력**:
- `Ingest/Apple Notes/*.md`: 노트 파일

---

### 3. Gobi Poller

**Gobi 앱**: 메모 동기화

```yaml
pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600  # 1시간
    api_base_url: "https://api.joingobi.com/api"
    # local_timezone: "America/New_York"
```

**옵션**:
- `api_base_url`: Gobi API URL
- `local_timezone`: 타임존 (선택)

**인증**:
- `secrets.yaml`에서 API 키 로드:
  ```yaml
  gobi:
    api_key: "your-api-key"
    user_id: "your-user-id"
  ```

**출력**:
- `Ingest/Gobi/*.md`: Gobi 메모

---

### 4. Gobi By Tags Poller

**Gobi 앱**: 특정 태그 메모만 동기화

```yaml
pollers:
  gobi_by_tags:
    enabled: true
    target_dir: "Ingest/GobiByTags"
    poll_interval: 3600
    api_base_url: "https://api.joingobi.com/api"
    tags:
      - work
      - ideas
      - meeting
```

**옵션**:
- `tags`: 동기화할 태그 목록

---

### 5. Limitless Poller

**Limitless AI**: 녹취록 동기화

```yaml
pollers:
  limitless:
    enabled: true
    target_dir: "Ingest/Limitless"
    poll_interval: 3600
    # local_timezone: "America/New_York"
    start_days_ago: 7  # 최근 7일
```

**옵션**:
- `start_days_ago`: 최근 며칠 녹취록 가져오기
- `local_timezone`: 타임존

**인증**:
- `secrets.yaml`:
  ```yaml
  limitless:
    api_key: "your-limitless-api-key"
  ```

**출력**:
- `Ingest/Limitless/*.md`: 녹취록

---

## Secrets 관리

민감한 정보(API 키 등)는 `secrets.yaml`에 저장합니다.

### secrets.yaml 구조

```yaml
# secrets.yaml (Vault 루트)

# Gobi API
gobi:
  api_key: "sk-gobi-xxxxxxxx"
  user_id: "user@example.com"

# Limitless AI
limitless:
  api_key: "ll-xxxxxxxx"

# OpenAI (Codex executor 사용 시)
openai:
  api_key: "sk-xxxxxxxx"

# Google Gemini (Gemini executor 사용 시)
google:
  api_key: "AIxxxxxxxx"
```

### 보안 주의사항

1. **`.gitignore`에 추가**:
   ```gitignore
   # secrets.yaml
   secrets.yaml
   **/secrets.yaml
   ```

2. **파일 권한 설정**:
   ```bash
   chmod 600 secrets.yaml
   ```

3. **환경 변수 대안** (선택):
   ```bash
   export GOBI_API_KEY="sk-gobi-xxxxxxxx"
   export LIMITLESS_API_KEY="ll-xxxxxxxx"
   ```

---

## 실전 예제

### 예제 1: 기본 웹 클리핑 워크플로우

```yaml
version: "1.0"

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  max_concurrent: 2

defaults:
  executor: claude_code
  timeout_minutes: 30

nodes:
  # 웹 클리핑 → 아티클
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    output_type: new_file

  # 아티클 → 소셜 포스팅
  - type: agent
    name: Create Thread Postings (CTP)
    input_path: AI/Articles
    output_path: AI/Sharable
    output_type: new_file

pollers: {}
```

**워크플로우**:
1. 웹 클리핑을 `Ingest/Clippings/`에 저장
2. EIC 에이전트가 자동 실행 → `AI/Articles/` 생성
3. CTP 에이전트가 자동 실행 → `AI/Sharable/` 생성

---

### 예제 2: 데일리 라운드업 + Gobi 동기화

```yaml
version: "1.0"

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  max_concurrent: 3

defaults:
  executor: claude_code
  timeout_minutes: 30

nodes:
  # Gobi 메모 처리
  - type: agent
    name: Process Life Logs (PLL)
    input_path: Ingest/Gobi
    output_path: AI/Lifelog
    output_type: new_file

  # 매일 라운드업 (새벽 1시)
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: "0 1 * * *"
    output_path: AI/Roundup
    timeout_minutes: 45

pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600  # 1시간마다 동기화
```

**워크플로우**:
1. 1시간마다 Gobi 메모 동기화 → `Ingest/Gobi/`
2. PLL 에이전트가 자동 실행 → `AI/Lifelog/`
3. 매일 새벽 1시 GDR 실행 → `AI/Roundup/`

---

### 예제 3: 멀티 소스 리서치 워크플로우

```yaml
version: "1.0"

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  max_concurrent: 5

defaults:
  executor: claude_code
  timeout_minutes: 30

nodes:
  # 웹 클리핑 enrichment
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles

  # Limitless 녹취록 처리
  - type: agent
    name: Process Life Logs (PLL)
    input_path: Ingest/Limitless
    output_path: AI/Lifelog

  # Apple Notes 처리
  - type: agent
    name: Ad-hoc Research within PKM (ARP)
    input_path: Ingest/Apple Notes
    output_path: AI/Research

  # 주간 라운드업 (월요일 9시)
  - type: agent
    name: Generate Weekly Roundup (GWR)
    cron: "0 9 * * 1"
    output_path: AI/Roundup
    timeout_minutes: 60

pollers:
  limitless:
    enabled: true
    target_dir: "Ingest/Limitless"
    poll_interval: 3600
    start_days_ago: 7

  apple_notes:
    enabled: true
    target_dir: "Ingest/Apple Notes"
    poll_interval: 1800
```

---

### 예제 4: Windows 환경 설정

```yaml
version: "1.0"

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  max_concurrent: 2

  # Windows executor 경로 명시
  executors:
    claude:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
    gemini:
      command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\gemini.cmd"

defaults:
  executor: claude
  timeout_minutes: 30

nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles

pollers: {}
```

---

## 다음 단계

- **[01_directory_structure.md](./01_directory_structure.md)**: 디렉터리 구조 개요
- **[02_module_overview.md](./02_module_overview.md)**: 모듈 및 클래스 상세

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
