# AI4PKM 디렉터리 구조 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI는 Obsidian Vault와 통합된 Personal Knowledge Management(PKM) 자동화 프레임워크입니다.

## 프로젝트 루트 구조

```
AI4PKM/
├── ai4pkm_cli/              # Python CLI 패키지 (핵심 코드)
├── ai4pkm_vault/            # 예제 Vault 디렉터리
├── docs/                    # 프로젝트 문서
├── pyproject.toml           # Python 패키지 설정
├── orchestrator.yaml        # Orchestrator 설정 (Vault 내에 위치 권장)
└── README.md                # 프로젝트 설명
```

## ai4pkm_cli/ 패키지 구조 (핵심)

### 최상위 레벨
```
ai4pkm_cli/
├── __init__.py              # 패키지 초기화
├── config.py                # 설정 관리 (Config 클래스)
├── logger.py                # 로깅 시스템
├── markdown_utils.py        # Markdown 파일 처리 유틸리티
└── main/                    # CLI 엔트리 포인트 (신규)
```

**역할:**
- `config.py`: `orchestrator.yaml` 및 환경 변수 로드 및 관리
- `logger.py`: 통합 로깅 시스템 (파일 + 콘솔)
- `markdown_utils.py`: Markdown 파일 파싱, frontmatter 처리

**주요 변화:**
- ❌ **제거됨:** `agents/`, `commands/`, `watchdog/` 폴더
- ✅ **신규 추가:** `main/`, `orchestrator/` 중심 아키텍처

---

### main/ - CLI 진입점 (신규)
```
ai4pkm_cli/main/
├── __init__.py
├── cli.py                   # 메인 CLI 명령어 (ai4pkm)
├── orchestrator.py          # Orchestrator 명령어 (ai4pkm orchestrator)
├── list_agents.py           # 에이전트 목록 조회
├── show_config.py           # 설정 조회
└── trigger_agent.py         # 에이전트 수동 트리거
```

**역할:**
- `cli.py`: CLI 명령어 파싱 및 실행 (`ai4pkm` 명령어의 시작점)
- `orchestrator.py`: Orchestrator 시작/중지/상태 확인
- `list_agents.py`: `orchestrator.yaml`에 정의된 에이전트 목록 출력
- `trigger_agent.py`: 특정 에이전트를 수동으로 실행

**Entry Point:** `pyproject.toml`에서 `ai4pkm = "ai4pkm_cli.main.cli:main"` 정의

**CLI 명령어 예:**
```bash
ai4pkm orchestrator run      # Orchestrator 시작
ai4pkm list-agents           # 에이전트 목록
ai4pkm trigger-agent "EIC"   # EIC 에이전트 수동 실행
ai4pkm show-config           # 설정 조회
```

---

### orchestrator/ - 멀티 에이전트 오케스트레이션 시스템 (핵심)
```
ai4pkm_cli/orchestrator/
├── __init__.py
├── core.py                  # Orchestrator 메인 로직
├── agent_registry.py        # 에이전트 등록 및 관리
├── execution_manager.py     # 실행 스케줄링 및 subprocess 관리
├── file_monitor.py          # 파일 시스템 모니터링 (watchdog 기반)
├── task_manager.py          # 태스크 파일 생성 및 관리
├── cron_scheduler.py        # Cron 스케줄링 (예: 데일리 라운드업)
├── poller_manager.py        # Poller 관리 (Apple Photos, Gobi, Limitless 등)
├── models.py                # 데이터 모델 (AgentDefinition, FileEvent 등)
└── metrics.py               # 성능 메트릭 (추후 구현)
```

**역할:**
- **파일 변경 감지** → **에이전트 매칭** → **실행**의 자동화 파이프라인
- 여러 에이전트의 병렬 실행 관리
- 이벤트 기반 워크플로우 조율
- Cron 기반 스케줄링 (예: 매일 새벽 1시 라운드업)

#### 핵심 모듈 상세

**1. core.py - Orchestrator 메인 로직**
- `Orchestrator` 클래스: 전체 시스템 조율
- `orchestrator.yaml` 로드 및 검증
- FileMonitor, AgentRegistry, CronScheduler, PollerManager 초기화
- 이벤트 루프 실행

**2. agent_registry.py - 에이전트 관리**
- `orchestrator.yaml`의 `nodes` 섹션 파싱
- 에이전트 정의 저장 및 조회
- 파일 경로 → 에이전트 매칭 로직
- 에이전트별 설정 (executor, timeout, priority 등)

**3. execution_manager.py - 실행 관리**
- Subprocess로 AI executor (claude, gemini 등) 실행
- 동시 실행 제한 (`max_concurrent` 설정)
- Windows/Mac/Linux executor 경로 해결
- 실행 로그 및 에러 처리

**4. file_monitor.py - 파일 감시**
- `watchdog` 라이브러리 기반
- `input_path`에 정의된 경로 감시
- 파일 생성/수정 이벤트 감지
- AgentRegistry와 연동하여 매칭된 에이전트 실행

**5. task_manager.py - 태스크 파일 관리**
- `_Settings_/Tasks/` 디렉터리에 태스크 파일 생성
- Task frontmatter 생성 (agent, status, priority 등)
- 태스크 상태 업데이트 (pending → in_progress → done)

**6. cron_scheduler.py - 스케줄링**
- `croniter` 라이브러리 기반
- `orchestrator.yaml`의 `cron` 필드 파싱
- 주기적 에이전트 실행 (예: 매일, 매주)

**7. poller_manager.py - 외부 데이터 동기화**
- Apple Photos, Gobi, Limitless 등 Poller 관리
- 주기적으로 외부 데이터 가져오기
- `orchestrator.yaml`의 `pollers` 섹션 설정

---

### pollers/ - 외부 데이터 소스 통합
```
ai4pkm_cli/pollers/
├── __init__.py
├── base_poller.py           # BasePoller 추상 클래스
├── apple_photos.py          # Apple iCloud Photos 동기화
├── apple_notes.py           # Apple Notes 동기화
├── gobi.py                  # Gobi 앱 동기화
├── gobi_by_tags.py          # Gobi 태그별 동기화
└── limitless.py             # Limitless AI 동기화
```

**역할:**
- 외부 서비스 API 연동
- 주기적 데이터 가져오기 (polling)
- Markdown 파일로 변환하여 `Ingest/` 폴더에 저장
- `orchestrator.yaml`의 `pollers` 설정으로 제어

**예:**
- `apple_photos.py`: iCloud 사진 → `Ingest/Photolog/*.jpg` + metadata.yaml
- `gobi.py`: Gobi 메모 → `Ingest/Gobi/*.md`
- `limitless.py`: Limitless 녹취록 → `Ingest/Limitless/*.md`

---

### tests/ - 테스트 코드
```
ai4pkm_cli/tests/
├── fixtures/                # 테스트 데이터
├── unit/                    # 유닛 테스트
│   ├── main/
│   └── orchestrator/
├── integration/             # 통합 테스트
│   └── orchestrator/
├── test_markdown_utils.py   # Markdown 유틸리티 테스트
└── test_orchestrator_eic_integration.py  # EIC 통합 테스트
```

**역할:**
- 코드 품질 보장
- CI/CD 파이프라인 통합
- Orchestrator 핵심 로직 검증

---

## Vault 디렉터리 구조

CLI가 작동하는 Obsidian Vault의 일반적인 구조:

```
ai4pkm_vault/  (또는 사용자 Vault)
├── orchestrator.yaml        # Orchestrator 설정 (필수!)
│
├── _Settings_/
│   ├── Prompts/            # 에이전트 프롬프트 (예: EIC.md, CTP.md)
│   ├── Tasks/              # 태스크 파일 저장소
│   ├── Logs/               # 실행 로그
│   ├── Skills/             # Claude Code Skills (MCP)
│   ├── Bases/              # 프롬프트 기반 지식
│   └── Templates/          # 노트 템플릿
│
├── Ingest/                 # 외부 소스 데이터
│   ├── Clippings/          # 웹 클리핑 → EIC 에이전트
│   ├── Gobi/               # Gobi 앱 동기화
│   ├── Limitless/          # Limitless AI 동기화
│   └── Photolog/           # 사진 로그
│
├── AI/                     # AI 생성 콘텐츠
│   ├── Articles/           # EIC 결과물
│   ├── Roundup/            # 데일리 라운드업 (GDR)
│   ├── Lifelog/            # 라이프 로그 (PLL)
│   ├── Events/             # 이벤트 요약 (GES)
│   └── Sharable/           # 소셜 미디어 포스팅 (CTP)
│
├── Journal/                # 데일리 저널
├── Projects/               # 프로젝트 노트
└── .obsidian/              # Obsidian 설정
```

---

## 설정 파일 위치

### orchestrator.yaml (필수)
- **위치**: Vault 루트 (예: `ai4pkm_vault/orchestrator.yaml`)
- **역할**: 에이전트 정의, 파일 경로 매핑, Poller 설정
- **예제**: `ai4pkm_vault/orchestrator.yaml` 참조

**핵심 섹션:**
```yaml
orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  max_concurrent: 3

defaults:
  executor: claude_code
  timeout_minutes: 30

nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles

pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600
```

### secrets.yaml (선택)
- **위치**: Vault 루트 (예: `ai4pkm_vault/secrets.yaml`)
- **역할**: API 키 및 민감 정보 저장
- **주의**: `.gitignore`에 추가 필수!

---

## 아키텍처 변화 요약

### 이전 (레거시)
```
사용자
  ↓
ai4pkm (CLI)
  ↓
├─→ agents/ (claude_agent.py, gemini_agent.py)
├─→ commands/ (ktp_runner.py, sync_gobi_command.py)
└─→ watchdog/ (file_watchdog.py, handlers/)
  ↓
Obsidian Vault
```

### 현재 (Orchestrator 중심)
```
사용자
  ↓
ai4pkm orchestrator run
  ↓
orchestrator/core.py (Orchestrator)
  ↓
├─→ orchestrator/file_monitor.py (파일 감시)
├─→ orchestrator/agent_registry.py (에이전트 관리)
├─→ orchestrator/execution_manager.py (실행)
├─→ orchestrator/cron_scheduler.py (스케줄링)
└─→ orchestrator/poller_manager.py (외부 데이터)
  ↓
Obsidian Vault (orchestrator.yaml 설정 기반)
```

---

## 주요 경로 규칙

1. **설정 파일**: Vault 루트에 `orchestrator.yaml` 필요
2. **프롬프트**: `_Settings_/Prompts/` 아래에 `.md` 파일 (예: `EIC.md`)
3. **로그**: `_Settings_/Logs/` (orchestrator.yaml에서 지정)
4. **태스크**: `_Settings_/Tasks/` (orchestrator.yaml에서 지정)
5. **Skills**: `_Settings_/Skills/` (Claude Code MCP 통합)

---

## 실행 흐름

### 1. Orchestrator 시작
```bash
cd /path/to/your/vault
ai4pkm orchestrator run
```

### 2. 파일 감시 시작
- `orchestrator.yaml`의 `nodes[].input_path` 감시
- 예: `Ingest/Clippings/` 폴더 감시

### 3. 파일 생성/수정 감지
```bash
echo "# My Article" > Ingest/Clippings/article.md
```

### 4. 에이전트 매칭
- `agent_registry.py`가 `article.md` → `EIC` 에이전트 매칭

### 5. 태스크 생성
- `task_manager.py`가 `_Settings_/Tasks/2025-12-03-EIC-article.md` 생성

### 6. 실행
- `execution_manager.py`가 `claude` executor 실행
- `_Settings_/Prompts/EIC.md` 프롬프트 사용
- 결과를 `AI/Articles/article-enriched.md`에 저장

### 7. 태스크 완료
- 태스크 상태: `pending` → `in_progress` → `done`

---

## 다음 단계

- **[02_module_overview.md](./02_module_overview.md)**: 각 모듈의 상세 클래스/함수 설명
- **[03_config_file_guide.md](./03_config_file_guide.md)**: `orchestrator.yaml` 설정 항목 가이드

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
