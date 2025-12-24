# Orchestrator 아키텍처

**작성일**: 2025-12-24
**학습 단계**: Day 2, 세션 1
**학습 목표**: AI4PKM Orchestrator의 설계 철학과 핵심 아키텍처 이해

---

## 1. Orchestrator란 무엇인가?

### 1.1 정의

**Orchestrator**는 AI4PKM의 **멀티 에이전트 시스템**을 조율하는 핵심 엔진입니다.

```
                    ┌──────────────────┐
                    │  Orchestrator    │
                    │  (Coordinator)   │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
    │ Agent 1 │        │ Agent 2 │        │ Agent 3 │
    │  (EIC)  │        │  (CTP)  │        │  (GDR)  │
    └─────────┘        └─────────┘        └─────────┘
```

### 1.2 왜 Orchestrator가 필요한가?

**단일 에이전트 방식의 한계**:
```bash
# 레거시 방식: 수동으로 각 에이전트 실행
ai4pkm -p "Enrich Ingested Content"  # 수동 실행
ai4pkm -p "Create Thread Postings"   # 수동 실행
ai4pkm -p "Generate Daily Roundup"   # 수동 실행
```

**문제점**:
- ❌ 수동 실행 필요
- ❌ 에이전트 간 의존성 관리 어려움
- ❌ 확장성 부족
- ❌ 동시 실행 제어 불가능

**Orchestrator 방식의 장점**:
```bash
# 새로운 방식: Orchestrator가 자동으로 관리
ai4pkm -o  # 데몬 실행 → 모든 에이전트 자동 조율
```

**이점**:
- ✅ 자동화: 파일 변경 감지 시 자동 실행
- ✅ 조율: 에이전트 간 실행 순서 및 의존성 관리
- ✅ 확장성: 새 에이전트 추가가 쉬움
- ✅ 동시성 제어: max_concurrent 설정으로 리소스 관리
- ✅ 모니터링: 통합된 로깅 및 상태 관리

### 1.3 AI4PKM의 Orchestrator 설계 철학

**핵심 원칙**:

1. **설정 기반 (Configuration-Driven)**
   - 코드 수정 없이 `orchestrator.yaml`만 편집
   - 새 에이전트 추가도 YAML 파일에 정의만 하면 됨

2. **이벤트 기반 (Event-Driven)**
   - 파일 생성/수정 이벤트로 에이전트 트리거
   - Poller를 통한 다양한 트리거 소스 지원

3. **비동기 실행 (Asynchronous Execution)**
   - 여러 에이전트 동시 실행 가능
   - max_concurrent로 동시성 제어

4. **확장 가능 (Extensible)**
   - 새로운 Poller 타입 추가 가능
   - 새로운 Executor 추가 가능
   - 플러그인 아키텍처

---

## 2. Orchestrator 핵심 구성 요소

### 2.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                           │
│                                                             │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ FileSystem     │  │ Agent           │  │ Execution    │ │
│  │ Monitor        │  │ Registry        │  │ Manager      │ │
│  │                │  │                 │  │              │ │
│  │ - Watches      │  │ - Loads agents  │  │ - Runs       │ │
│  │   files        │  │ - Matches       │  │   agents     │ │
│  │ - Generates    │  │   triggers      │  │ - Manages    │ │
│  │   events       │  │                 │  │   queue      │ │
│  └───────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
│          │                    │                  │         │
│          │    Event Queue     │                  │         │
│          └────────►───────────┴──────────────────┘         │
│                                                             │
│  ┌────────────────┐  ┌─────────────────┐                   │
│  │ Cron           │  │ Poller          │                   │
│  │ Scheduler      │  │ Manager         │                   │
│  │                │  │                 │                   │
│  │ - Scheduled    │  │ - External      │                   │
│  │   triggers     │  │   pollers       │                   │
│  │   (cron)       │  │   (Gobi, etc.)  │                   │
│  └────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 핵심 컴포넌트 상세

#### 2.2.1 Orchestrator Core (`orchestrator/core.py`)

**역할**: 전체 시스템의 메인 이벤트 루프 및 조율

**주요 속성**:
```python
class Orchestrator:
    vault_path: Path           # Vault 루트 경로
    config: Config             # 설정 객체
    agent_registry: AgentRegistry        # 에이전트 관리
    execution_manager: ExecutionManager  # 실행 관리
    file_monitor: FileSystemMonitor      # 파일 모니터링
    cron_scheduler: CronScheduler        # 스케줄 관리
    poller_manager: PollerManager        # Poller 관리
```

**주요 메서드**:
- `start()`: Orchestrator 시작
- `stop()`: Orchestrator 중지
- `get_status()`: 현재 상태 조회
- `trigger_agent()`: 에이전트 수동 실행

**동작 흐름**:
```
1. Orchestrator 초기화
   ↓
2. 설정 로드 (orchestrator.yaml)
   ↓
3. 컴포넌트 초기화
   - AgentRegistry: 에이전트 로드
   - ExecutionManager: 실행 관리자 준비
   - FileSystemMonitor: 파일 감시 시작
   - PollerManager: Poller 시작
   - CronScheduler: 스케줄 등록
   ↓
4. 이벤트 루프 시작
   - 이벤트 큐에서 이벤트 대기
   - 이벤트 발생 시 에이전트 매칭
   - ExecutionManager에 실행 요청
   ↓
5. 종료 시그널까지 계속 실행
```

#### 2.2.2 Agent Registry (`orchestrator/agent_registry.py`)

**역할**: 에이전트 정의 로드 및 트리거 매칭

**주요 기능**:
1. **에이전트 로딩**:
   - `orchestrator.yaml`에서 에이전트 정의 읽기
   - 프롬프트 파일 로드
   - 에이전트 검증

2. **트리거 매칭**:
   - 이벤트 발생 시 적절한 에이전트 찾기
   - 트리거 패턴 매칭 (`trigger_pattern`)
   - 이벤트 타입 확인 (`trigger_event`)

**데이터 구조**:
```python
@dataclass
class AgentDefinition:
    # 기본 정보
    name: str                    # "Enrich Ingested Content (EIC)"
    abbreviation: str            # "eic"
    category: str                # "learning"

    # 트리거 설정
    trigger_pattern: str         # "vl_ai4pkm_clippings/**/*.md"
    trigger_event: str           # "create" | "modify" | "delete"
    cron: Optional[str]          # "0 9 * * *" (매일 오전 9시)

    # 입출력
    input_path: List[str]        # ["vl_ai4pkm_clippings"]
    output_path: str             # "vl_ai4pkm_materials"
    output_type: str             # "new_file" | "modify" | "none"

    # 실행
    executor: str                # "claude_code"
    max_parallel: int            # 1
    timeout_minutes: int         # 30
    prompt_body: str             # 프롬프트 본문
```

#### 2.2.3 Execution Manager (`orchestrator/execution_manager.py`)

**역할**: 에이전트 실행 관리 및 동시성 제어

**주요 기능**:
1. **실행 큐 관리**:
   - 에이전트 실행 요청 큐잉
   - 우선순위 처리

2. **동시성 제어**:
   - `max_concurrent` 설정에 따라 동시 실행 제한
   - 리소스 관리

3. **Executor 연동**:
   - Claude Code, Gemini 등 Executor 실행
   - stdin 기반 실행 (최신 아키텍처)
   - 타임아웃 관리

**실행 흐름**:
```
ExecutionManager.execute()
   ↓
1. ExecutionContext 생성
   ↓
2. 프롬프트 구성
   - Agent 프롬프트
   - Input context
   - Skills, MCP servers
   ↓
3. Executor 실행
   - subprocess로 claude/gemini 실행
   - stdin으로 프롬프트 전달
   ↓
4. 결과 처리
   - stdout 캡처
   - 로그 저장
   - 태스크 파일 생성/업데이트
   ↓
5. Post-processing
   - output_path에 결과 저장
   - 트리거 파일 처리 (archived 등)
```

#### 2.2.4 File System Monitor (`orchestrator/file_monitor.py`)

**역할**: 파일 시스템 변경 감지

**주요 기능**:
- Watchdog 라이브러리 사용
- 파일 생성/수정/삭제 이벤트 감지
- 이벤트 큐에 푸시

**동작**:
```python
# 파일 변경 감지
vl_ai4pkm_clippings/new_article.md (생성)
   ↓
# TriggerEvent 생성
TriggerEvent(
    event_type="create",
    file_path="vl_ai4pkm_clippings/new_article.md",
    timestamp=datetime.now()
)
   ↓
# Event Queue에 푸시
event_queue.put(trigger_event)
```

#### 2.2.5 Poller Manager (`orchestrator/poller_manager.py`)

**역할**: 외부 Poller 관리

**주요 기능**:
- Gobi, Limitless, Apple Notes 등 외부 앱 폴링
- 백그라운드 스레드에서 주기적 폴링
- 새 항목 발견 시 이벤트 생성

**Poller 예시**:
```python
# Gobi Poller
- Gobi 앱에서 새 항목 확인
- poll_interval마다 체크
- 새 항목 발견 시 TriggerEvent 생성
```

#### 2.2.6 Cron Scheduler (`orchestrator/cron_scheduler.py`)

**역할**: 스케줄 기반 트리거

**주요 기능**:
- Cron 표현식 파싱
- 정해진 시간에 에이전트 트리거
- 백그라운드 스케줄러 실행

**예시**:
```yaml
# orchestrator.yaml
nodes:
  - name: "Generate Daily Roundup (GDR)"
    cron: "0 9 * * *"  # 매일 오전 9시
```

---

## 3. 데이터 모델

### 3.1 TriggerEvent

이벤트 발생을 나타내는 데이터 구조:

```python
@dataclass
class TriggerEvent:
    event_type: str          # "create", "modify", "delete", "schedule"
    file_path: Optional[Path]
    agent_abbreviation: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]
```

### 3.2 ExecutionContext

에이전트 실행 컨텍스트:

```python
@dataclass
class ExecutionContext:
    execution_id: str           # UUID
    agent: AgentDefinition
    trigger_data: Dict[str, Any]

    start_time: datetime
    end_time: Optional[datetime]

    status: str                 # "pending", "completed", "failed"
    prompt: Optional[str]
    response: Optional[str]
    error_message: Optional[str]
```

---

## 4. Orchestrator vs 단일 에이전트 비교

### 4.1 레거시 방식 (단일 에이전트)

```bash
# 사용자가 직접 실행
ai4pkm -p "Enrich Ingested Content"

# 특징:
# - 한 번에 하나의 에이전트만 실행
# - 수동 트리거 필요
# - 에이전트 간 연결 없음
```

### 4.2 Orchestrator 방식 (멀티 에이전트)

```bash
# Orchestrator 데몬 실행
ai4pkm -o

# 특징:
# - 여러 에이전트 동시 관리
# - 자동 트리거 (파일 변경, 스케줄)
# - 에이전트 간 워크플로우 구성 가능
# - 통합 모니터링 및 로깅
```

### 4.3 비교표

| 항목 | 레거시 방식 | Orchestrator 방식 |
|------|------------|-------------------|
| 실행 방식 | 수동 | 자동 + 수동 |
| 동시성 | 단일 실행 | 다중 실행 (max_concurrent) |
| 트리거 | 사용자 명령 | 파일, 스케줄, Poller |
| 워크플로우 | 수동 연결 | 자동 연결 |
| 모니터링 | 개별 로그 | 통합 모니터링 |
| 확장성 | 제한적 | 높음 |

---

## 5. Orchestrator 실행 흐름 예시

### 5.1 시나리오: 웹 클리핑 → Enrichment → 게시물 생성

```
1. 사용자가 웹 클리퍼로 기사 저장
   vl_ai4pkm_clippings/article.md 생성
   ↓
2. FileSystemMonitor가 감지
   TriggerEvent(create, "vl_ai4pkm_clippings/article.md")
   ↓
3. AgentRegistry가 EIC 에이전트 매칭
   - trigger_pattern: "vl_ai4pkm_clippings/**/*.md"
   - trigger_event: "create"
   ↓
4. ExecutionManager가 EIC 실행
   - Executor: claude_code
   - Input: article.md
   - Output: vl_ai4pkm_materials/article_enriched.md
   ↓
5. EIC 완료 후 새 파일 생성
   vl_ai4pkm_materials/article_enriched.md 생성
   ↓
6. FileSystemMonitor가 다시 감지
   TriggerEvent(create, "vl_ai4pkm_materials/article_enriched.md")
   ↓
7. AgentRegistry가 CTP 에이전트 매칭
   - trigger_pattern: "vl_ai4pkm_materials/**/*.md"
   - trigger_event: "create"
   ↓
8. ExecutionManager가 CTP 실행
   - Input: article_enriched.md
   - Output: Publish/article_thread.md
   ↓
9. 워크플로우 완료!
```

---

## 6. 주요 학습 포인트

### 6.1 Orchestrator의 핵심 가치

1. **자동화**
   - 파일 저장만 하면 자동으로 처리
   - 스케줄 기반 자동 실행

2. **조율**
   - 여러 에이전트를 유기적으로 연결
   - 의존성 관리 (A → B → C)

3. **확장성**
   - 새 에이전트 추가가 쉬움
   - 새 Poller 추가 가능

4. **모니터링**
   - 통합된 로깅
   - 상태 조회 (`--orchestrator-status`)

### 6.2 설계 패턴

1. **Event-Driven Architecture**
   - 이벤트 생성 → 큐 → 처리
   - 비동기 실행

2. **Registry Pattern**
   - AgentRegistry: 에이전트 등록 및 조회
   - 중앙 집중식 관리

3. **Manager Pattern**
   - ExecutionManager: 실행 관리
   - PollerManager: Poller 관리
   - 책임 분리

4. **Configuration-Driven**
   - YAML로 모든 설정
   - 코드 수정 불필요

---

## 7. 다음 단계

세션 2에서 다룰 내용:
- **Poller 시스템 상세**: 각 Poller 타입 이해
- **트리거 메커니즘**: 어떻게 에이전트가 실행되는가?
- **실제 Poller 설정**: orchestrator.yaml에서 Poller 구성

---

**학습 완료**: 2025-12-24
**다음 학습**: Poller 시스템 가이드
