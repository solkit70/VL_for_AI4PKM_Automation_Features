아래 문서는 "Orchestrator Implementation Specification" (Last Updated: 2025-11-01, Version 1.0)의 실제 구현 기준을 한국어로 상세 정리한 학습 노트입니다. 사용자 가이드가 아닌, 운영 중인 구현(Production)의 동작과 코드 책임 분리, 한계, 개선안까지 포괄합니다.
원문: https://jykim.github.io/AI4PKM/dev-docs/2025-11-01-orchestrator-implementation-spec/

> 관련 노트: [[01 - Orchestrator 상세 해설]] · [[03 - Agentic AI 아키텍처 해설]] · [[04 - 온디맨드 지식 태스크 아키텍처 해설]]

## 1) 요약 (Executive Summary)

- 상태: ✅ Production (운영 중)
- 핵심 특징:
  - 단일 설정원천(nodes 기반) `orchestrator.yaml`
  - 전역 + 에이전트별 2단계 동시성 제한, 원자적 슬롯 예약
  - 과부하 시 QUEUED 태스크로 우아한 저하
  - 다중 실행기(claude_code, gemini_cli, codex_cli, custom_script)
  - Obsidian 호환 태스크 파일/로그 기반 추적
  - 정규식 기반 내용 트리거, 후처리 액션 지원(예: `remove_trigger_content`)
- 미구현(설계만): Cron, 완전한 multi-input, Skills, MCP 통합, Metrics 수집
- 운영 수치(문서 기준):
  - 코드 1,943 LOC / 6 코어 모듈 / 47 유닛테스트(38 통과)
  - 8개 에이전트 동작(EIC, PLL, PPP, GES, GDR, CTP, ARP, HTC)
  - ~50MB 메모리 / <100ms 이벤트 처리 지연

---

## 2) 아키텍처 (Architecture Overview)

### 2.1 코어 모듈(Separation of Concerns)
```
ai4pkm_cli/orchestrator/
├── core.py              # 조정자: 이벤트 루프, 큐 폴링, 실행 스레드 스폰, QUEUED 처리
├── agent_registry.py    # 에이전트 로딩/매칭: YAML 노드→프롬프트 매칭, 패턴/정규식 처리
├── execution_manager.py # 실행·동시성: 원자적 슬롯 예약, 실행 컨텍스트, 후처리
├── task_manager.py      # 태스크 파일: 생성/상태 전이/로그 append
├── file_monitor.py      # 파일 감시: watchdog 이벤트→FileEvent 큐잉
└── models.py            # 데이터 모델: AgentDefinition/ExecutionContext/FileEvent
```

모듈 요약 표:

| 모듈 | 경로 | 핵심 책임 | 주요 함수/포인트 | 에러 모드 |
|------|------|-----------|------------------|-----------|
| core | core.py | 이벤트 루프 / 큐 관리 / QUEUED 처리 / 타임아웃 검사 | `_event_loop()`, `_process_queued_tasks()` | 파일 이벤트 파싱 실패, 슬롯 없음 |
| agent_registry | agent_registry.py | YAML 로드, 약어 추출, 프롬프트 매칭 | `load_agents()`, `find_matching_agents()` | 프롬프트 누락, 패턴 충돌 |
| execution_manager | execution_manager.py | 동시성(글로벌/에이전트) 제어, 실행 스레드 생성, 후처리 | `reserve_slot()`, `execute_agent()` | 타임아웃, 후처리 실패 |
| task_manager | task_manager.py | 태스크 파일 생성/상태 전이/로그 append | `create_task_file()`, `update_status()` | 파일 쓰기 실패, 중복 생성 |
| file_monitor | file_monitor.py | watchdog 래핑, 이벤트 객체 생성 | `_on_created()`, `_on_modified()` | 빠른 연속 이벤트(디바운스 없음) |
| models | models.py | 데이터 구조/타입 정의 | dataclasses: `AgentDefinition` 등 | 필드 누락(Validation 경고) |

### 2.2 컴포넌트 역할 요약
- Core: FileSystemMonitor/AgentRegistry/ExecutionManager를 오케스트레이션. 폴링 간격 기본 1.0s. 용량 여유 시 스레드 스폰, 아니면 QUEUED 태스크 기록.
- Agent Registry: `orchestrator.yaml`의 nodes 읽기→약어(ABBR) 추출→프롬프트 파일 `*({ABBR}).md` 매칭. 글롭/정규식 기반 매칭, 제외 패턴·내용 패턴 지원.
- Execution Manager: 전역(`max_concurrent`) + 에이전트별(`max_parallel`) 동시성. `reserve_slot()`에서 락 2개로 원자적 예약. 실행 전 태스크 파일 생성/완료 시 상태 업데이트/후처리.
- Task Manager: `_Settings_/Tasks/`에 파일 생성. 파일명 `YYYY-MM-DD {ABBR} - {input}.md`. 상태 라이프사이클(QUEUED → IN_PROGRESS → PROCESSED/FAILED/TIMEOUT). 프로세스 로그 append.
- File Monitor: watchdog 기반 생성/수정/삭제 이벤트 감지. `.md` 대상. Frontmatter 파싱 지원. 이벤트 큐에 `FileEvent` push.
- Models: `AgentDefinition`(트리거/입출력/실행 설정 포함 22필드), `ExecutionContext`, `FileEvent` 등.

### 2.3 데이터 흐름
```
사용자 파일 변경 → Watchdog → 이벤트 큐 → Core._event_loop()
  → AgentRegistry.find_matching_agents() → 동시성 체크
    → [가능] reserve_slot() & 실행 스레드 스폰 → IN_PROGRESS → 실행 → PROCESSED/FAILED → 후처리
    → [불가] 태스크 파일 생성(QUEUED) → 용량 생기면 _process_queued_tasks()로 FIFO 실행
```

### 2.4 디렉터리 구조(실제)
```
ai4pkm_vault/
├── orchestrator.yaml        # SINGLE SOURCE OF TRUTH
├── _Settings_/
│   ├── Prompts/            # *({ABBR}).md 최소 Frontmatter
│   ├── Tasks/              # 태스크 추적 파일(자동)
│   ├── Logs/               # 실행 로그(자동)
│   ├── Skills/             # (미구현) 스킬 모듈
│   └── Bases/              # (미구현) 지식 베이스
├── Ingest/
│   ├── Clippings/
│   └── Limitless/
└── AI/
    ├── Articles/
    ├── Lifelog/
    └── ...
```

---

## 3) 구성 시스템 (Configuration System)

### 3.1 orchestrator.yaml
```
orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"
  max_concurrent: 3
  poll_interval: 1.0

defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3
  task_priority: medium

nodes:
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    trigger_exclude_pattern: "*-EIC*"
```

### 3.2 로딩 과정과 폴백(Precedence)
- 로딩: YAML → dict 파싱 → 구조 유효성 점검(경고) → orchestrator 설정 추출 → defaults 캐스케이드 적용
- 폴백 체인(우선순위): Node 값 > YAML defaults > `ai4pkm_cli.json` > 코드 하드코드

### 3.3 노드 발견과 프롬프트 요구사항
- nodes에서 `type: agent`만 필터링, `name`의 괄호에서 약어 추출(정규식), `*({ABBR}).md` 프롬프트 탐색.
- 프롬프트 Frontmatter 최소 필드:
```
---
title: Enrich Ingested Content (EIC)
abbreviation: EIC
category: ingestion
---
```
- 입출력/트리거/타임아웃 등 설정은 모두 YAML 노드에서 오며, 프롬프트 Frontmatter로 설정하지 않음.

---

## 4) 에이전트 라이프사이클 (Agent Lifecycle)

### 4.1 트리거 파생과 이벤트 매칭
- 입력 경로에서 글롭 패턴 자동 파생: `{path}/*.md` (multi-input은 첫 경로만)
- 이벤트 타입 매핑: `new_file→created`, `updated_file→modified`, `daily_file→scheduled(미구현)`, `manual→manual`
- 매칭 순서: 수동 여부→이벤트 타입→패턴 글롭 매칭→제외 패턴→내용 정규식(있을 때만)→중복 태스크 방지

### 4.2 실행 흐름
- Core 이벤트 루프: 타임아웃 폴링, 이벤트 없을 때도 QUEUED 체크
- 슬롯 예약 실패 시: QUEUED 생성(트리거 데이터 JSON 인코딩 저장) 후 콘솔 `[QUEUED]` 출력
- 실행 스레드: 시작/성공/실패 로그, 에러는 오케스트레이터 크래시 유발하지 않음

---

## 5) 동시성·태스크 관리 (Concurrency & Tasks)

### 5.1 2단계 동시성 제어
- 전역 `max_concurrent`(기본 3): 전체 실행 수 제한
- 에이전트별 `max_parallel`(기본 3, 노드별 override): 동일 에이전트 동시 실행 제한

### 5.2 원자적 슬롯 예약(reserve_slot)
- 글로벌 락→글로벌 카운트 증가→에이전트 락→에이전트 카운트 증가 순으로 원자적 확인/예약
- 실패 시 즉시 롤백. 레이스 컨디션 제거(테스트 중 발견된 이슈를 커밋으로 수정)

### 5.3 QUEUED 처리
- 용량 부족 시 태스크를 QUEUED로 생성(FIFO). 각 루프에서 하나만 처리하여 쓰래싱 방지.
- 개선안: 사용 가능한 슬롯 수만큼 일괄 처리(batch), 인메모리 인덱스 도입

### 5.4 태스크 파일 구조와 상태 전이
- 파일명: `YYYY-MM-DD {ABBR} - {input}.md`
- Frontmatter: title/created/archived/worker/status/priority/output/task_type/generation_log/trigger_data_json
- 상태: `QUEUED → IN_PROGRESS → PROCESSED | FAILED | TIMEOUT`

---

## 6) 구현 세부 (Implementation Details)

### 6.1 실행기(Executors)
- `claude_code`(기본), `gemini_cli`, `codex_cli`, `custom_script` 지원. 에이전트 노드에서 선택, 미지정 시 defaults/코드 폴백.

### 6.2 후처리(Post-Processing)
- `remove_trigger_content` 지원: `trigger_content_pattern`에 매칭되는 마커를 원본에서 제거.
- 확장 포인트: `archive_file`, `move_to`, `add_property` 등 추가 가능.

### 6.3 로그 관리와 디렉터리 자동 생성
- 로그 파일명 패턴: 타임스탬프/에이전트/실행ID 포함, `_Settings_/Logs/`에 저장.
- 오케스트레이터 초기화 시 `Prompts/Tasks/Logs/Skills/Bases` 디렉터리 자동 생성.

---

## 7) 현재 한계와 약점 (Limitations & Weaknesses)

- 미구현 기능: Cron, 완전한 multi-input, Skills, MCP, Metrics
- 테스트 공백: QUEUED 처리, 원자 예약 레이스, 후처리, 다중 실행기, E2E 실제 CLI
- 엣지 케이스: 빠른 연속 수정(디바운스 없음), 태스크 파일명 충돌, 고아 QUEUED 태스크 복구 없음, 누락 파일 silent fail, 트리거 데이터 직렬화 취약
- 성능 병목: 타임아웃 폴링, 선형 스캔, 매 이벤트 Frontmatter 파싱, 배치 없음
- 문서 공백: 구성 우선순위, 오류 메시지 개선, 실행기 요구사항, 후처리 문서화 부족

---

## 8) 개선 제안 (Areas for Improvement)

- 단기: 실패 테스트 수정, Metrics 수집 클래스, Health 체크 엔드포인트, 고아 QUEUED 복구
- 아키텍처: 블로킹 큐(이벤트 드리븐), QUEUED 인덱스, 에이전트 핫리로드, 구조화 로깅(JSON)
- 에러 핸들링: 시작 시 구성 검증, 재시도/백오프, watchdog 예외 보호
- 성능: 큐 배치 처리, Frontmatter 캐시/지연 파싱
- UX: 대화형 TUI, Dry Run, Agent 템플릿 생성기, Web 대시보드
- 모니터링: Prometheus 메트릭, OpenTelemetry, 감사 로그

---

## 9) 성공 지표 (Success Metrics)

- 프로덕션 기능: 안정 이벤트 루프, 동시성 제어, 태스크 추적, 다중 실행기, YAML 구성
- 코드 품질: 분리/타입힌트/복잡도 낮음/DRY, 47 테스트(업데이트 필요 9)
- 운영: <100ms 이벤트 반응, 저메모리/저CPU, 오랜 업타임, 오류 격리, 완전한 감사 트레일

---

## 10) 참고(References)

- 핵심 소스 링크: core(event loop/queue), agent_registry(load/match), execution_manager(slots/exec), task_manager(tasks), models
- 관련 문서: User Guide, 아키텍처 블로그, 오리지널 설계, 온디맨드 태스크 글
- 테스트: unit/integration, 수동 통합 가이드

---

## 11) 테스트 & 품질 스냅샷 (Tests & Quality Snapshot)

| 항목 | 값 | 설명 | 개선 액션 |
|------|----|------|-----------|
| 총 유닛테스트 | 47 | 기능/동시성/매칭 일부 커버 | 실패 9개 세부 분류 필요 |
| 통과 테스트 | 38 | 안정 핵심 경로 통과 | 실패 케이스 원인 태깅 |
| 실패 테스트 | 9 | 예약 경계/후처리/다중 실행기 추정 | 재현 로그 캡처 후 수정 |
| 코드 LOC | 1,943 | orchestrator 디렉터리 기준 | 중복/매직넘버 줄이기 |
| 이벤트 평균 지연 | <100ms | 문서 측정 값 | 측정 수집 자동화 필요 |
| 메모리 사용 | ~50MB | steady-state | metrics 수집기 추가 |
| 미커버 모듈 | 후처리, cron, skills | 미구현/테스트 없음 | 구현 후 최소 3케이스 테스트 |
| 동시성 Race 발견 | 1 (과거 수정) | 슬롯 예약 경쟁 | 회귀 테스트 추가 |

테스트 개선 우선순위 제안:
1. 슬롯 예약 경계(동시 N+1) 회귀 테스트 추가
2. 후처리 실패 시 롤백/상태 전이 테스트
3. 다중 실행기(gemini_cli, codex_cli) 통합 스모크
4. QUEUED → IN_PROGRESS 전이 타이밍 테스트(슬롯 가용 직후)
5. 프롬프트 누락/패턴 충돌 시 경고 검증
