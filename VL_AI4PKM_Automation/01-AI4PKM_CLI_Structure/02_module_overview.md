# AI4PKM CLI 모듈 개요 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI의 주요 Python 모듈과 클래스, 함수에 대한 상세 설명입니다.

---

## 📋 목차
1. [CLI 진입점 (main/)](#cli-진입점-main)
2. [Orchestrator (orchestrator/)](#orchestrator-orchestrator)
3. [Pollers (pollers/)](#pollers-pollers)
4. [설정 및 유틸리티](#설정-및-유틸리티)
5. [테스트 (tests/)](#테스트-tests)

---

## CLI 진입점 (main/)

### 1. cli.py - 메인 CLI 명령어

**위치**: `ai4pkm_cli/main/cli.py`

**Entry Point**: `ai4pkm = "ai4pkm_cli.main.cli:main"`

**주요 명령어**:
```python
@click.command()
@click.option("--orchestrator", "-o", is_flag=True, help="Run orchestrator mode")
@click.option("--list-agents", "-l", is_flag=True, help="List all available agents")
@click.option("--show-config", is_flag=True, help="Show current configuration")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
def main(...):
    """AI4PKM CLI - Personal Knowledge Management framework."""
```

**사용 예**:
```bash
# Orchestrator 실행
ai4pkm --orchestrator
ai4pkm -o

# 에이전트 목록
ai4pkm --list-agents
ai4pkm -l

# 설정 조회
ai4pkm --show-config

# 디버그 모드
ai4pkm -o --debug
```

**하위 명령어 (Subcommands)**:
- `orchestrator run`: Orchestrator 시작
- `orchestrator status`: 상태 확인
- `orchestrator stop`: 중지
- `list-agents`: 에이전트 목록
- `trigger-agent <name>`: 에이전트 수동 실행
- `show-config`: 설정 조회

---

### 2. orchestrator.py - Orchestrator 명령어

**위치**: `ai4pkm_cli/main/orchestrator.py`

**역할**: Orchestrator 시작/중지/상태 관리

**주요 함수**:
```python
def orchestrator_run():
    """Start the orchestrator in monitoring mode."""
    # orchestrator/core.py의 Orchestrator 인스턴스 생성 및 실행

def orchestrator_status():
    """Show orchestrator status."""
    # 실행 중인 Orchestrator 상태 확인

def orchestrator_stop():
    """Stop the orchestrator."""
    # Orchestrator 종료
```

**사용 예**:
```bash
ai4pkm orchestrator run      # 시작
ai4pkm orchestrator status   # 상태
ai4pkm orchestrator stop     # 중지
```

---

### 3. list_agents.py - 에이전트 목록 조회

**위치**: `ai4pkm_cli/main/list_agents.py`

**역할**: `orchestrator.yaml`에 정의된 에이전트 목록 출력

**주요 함수**:
```python
def list_agents(config: Config):
    """List all agents defined in orchestrator.yaml."""
    # nodes 섹션 파싱 및 출력
    # - Agent name
    # - Executor (claude, gemini, etc.)
    # - Input path
    # - Output path
    # - Cron schedule (if any)
```

**출력 예**:
```
Available Agents:
  1. Enrich Ingested Content (EIC)
     - Executor: claude_code
     - Input: Ingest/Clippings
     - Output: AI/Articles

  2. Generate Daily Roundup (GDR)
     - Executor: claude_code
     - Cron: 0 1 * * * (Daily at 1 AM)
     - Output: AI/Roundup
```

---

### 4. trigger_agent.py - 에이전트 수동 실행

**위치**: `ai4pkm_cli/main/trigger_agent.py`

**역할**: 특정 에이전트를 파일 감지 없이 수동으로 실행

**주요 함수**:
```python
def trigger_agent(agent_name: str, file_path: Optional[str] = None):
    """Manually trigger an agent execution."""
    # AgentRegistry에서 에이전트 조회
    # ExecutionManager로 실행
```

**사용 예**:
```bash
# 에이전트만 실행 (batch 모드)
ai4pkm trigger-agent "GDR"

# 특정 파일에 대해 실행
ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/article.md"
```

---

### 5. show_config.py - 설정 조회

**위치**: `ai4pkm_cli/main/show_config.py`

**역할**: 현재 적용된 설정 표시

**주요 함수**:
```python
def show_config(config: Config):
    """Display current configuration."""
    # orchestrator.yaml 내용 출력
    # - Vault path
    # - Prompts directory
    # - Tasks directory
    # - Max concurrent executions
    # - Enabled pollers
    # - Agent list
```

---

## Orchestrator (orchestrator/)

### 1. core.py - Orchestrator 메인 로직

**위치**: `ai4pkm_cli/orchestrator/core.py`

**클래스**: `Orchestrator`

**역할**: 전체 시스템 조율 및 이벤트 루프 실행

**주요 메서드**:
```python
class Orchestrator:
    def __init__(self, vault_path: Path, config_path: Optional[Path] = None):
        """
        Initialize Orchestrator.

        Args:
            vault_path: Obsidian Vault 경로
            config_path: orchestrator.yaml 경로 (기본: vault_path/orchestrator.yaml)
        """
        # Config 로드
        # AgentRegistry 초기화
        # FileMonitor 초기화
        # ExecutionManager 초기화
        # CronScheduler 초기화
        # PollerManager 초기화

    def start(self):
        """Start orchestrator main loop."""
        # FileMonitor 시작 (파일 감시)
        # CronScheduler 시작 (주기 작업)
        # PollerManager 시작 (외부 데이터)
        # 이벤트 루프 실행

    def stop(self):
        """Stop orchestrator gracefully."""
        # 모든 서브시스템 종료
        # 실행 중인 작업 완료 대기
```

**이벤트 흐름**:
```
파일 생성/수정
   ↓
FileMonitor 감지
   ↓
AgentRegistry 매칭
   ↓
ExecutionManager 실행
   ↓
결과 저장
```

---

### 2. agent_registry.py - 에이전트 등록 및 관리

**위치**: `ai4pkm_cli/orchestrator/agent_registry.py`

**클래스**: `AgentRegistry`

**역할**: `orchestrator.yaml`의 `nodes` 섹션 파싱 및 에이전트 관리

**주요 메서드**:
```python
class AgentRegistry:
    def __init__(self, config: OrchestratorConfig):
        """Load agents from orchestrator.yaml."""
        # nodes 섹션 파싱
        # AgentDefinition 객체 생성

    def get_agents_for_path(self, file_path: Path) -> List[AgentDefinition]:
        """
        Find matching agents for a given file path.

        Args:
            file_path: 파일 경로

        Returns:
            매칭된 에이전트 리스트

        Example:
            Ingest/Clippings/article.md → EIC 에이전트
        """

    def get_agent_by_name(self, name: str) -> Optional[AgentDefinition]:
        """Get agent by name."""

    def list_agents(self) -> List[AgentDefinition]:
        """List all registered agents."""
```

**AgentDefinition 모델** (`models.py`):
```python
@dataclass
class AgentDefinition:
    name: str                    # 에이전트 이름 (예: "EIC")
    type: str                    # "agent" (고정)
    input_path: Union[str, List[str]]  # 입력 경로 패턴
    output_path: str             # 출력 경로
    output_type: str             # "new_file" | "update_file"
    executor: str                # "claude_code" | "gemini" | "codex"
    timeout_minutes: int         # 타임아웃
    max_parallel: int            # 최대 병렬 실행 수
    cron: Optional[str]          # Cron 표현식 (선택)
    task_create: bool            # 태스크 파일 생성 여부
    task_priority: str           # "high" | "medium" | "low"
```

---

### 3. execution_manager.py - 실행 관리

**위치**: `ai4pkm_cli/orchestrator/execution_manager.py`

**클래스**: `ExecutionManager`

**역할**: Subprocess로 AI executor 실행 및 동시성 제어

**주요 메서드**:
```python
class ExecutionManager:
    def __init__(self, config: Config, max_concurrent: int = 3):
        """Initialize execution manager."""
        self.max_concurrent = max_concurrent
        self.running_executions: Dict[str, subprocess.Popen] = {}

    def execute_agent(
        self,
        agent: AgentDefinition,
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        Execute an agent using subprocess.

        Args:
            agent: 에이전트 정의
            context: 실행 컨텍스트 (파일 경로, 프롬프트 등)

        Returns:
            ExecutionResult (성공/실패, 출력, 에러)
        """
        # 1. Executor 경로 해결 (Windows/Mac/Linux)
        # 2. 프롬프트 로드 (_Settings_/Prompts/{agent_name}.md)
        # 3. Subprocess 실행
        #    - claude --vault /path/to/vault --prompt /path/to/prompt.md ...
        # 4. 타임아웃 처리
        # 5. 로그 저장 (_Settings_/Logs/)

    def _resolve_executor_path(self, executor_name: str) -> str:
        """
        Resolve executor command path.

        Priority:
        1. orchestrator.yaml의 executors 설정
        2. shutil.which() (PATH 검색)
        3. Windows npm 경로 (%APPDATA%\\npm)
        """

    def wait_for_slot(self):
        """Wait until a execution slot is available."""
        # max_concurrent 제한 확인
```

**ExecutionContext 모델**:
```python
@dataclass
class ExecutionContext:
    file_path: Optional[Path]    # 트리거 파일 (선택)
    event_type: str               # "file_created" | "file_modified" | "cron" | "manual"
    vault_path: Path              # Vault 경로
    output_path: Path             # 출력 경로
```

**ExecutionResult 모델**:
```python
@dataclass
class ExecutionResult:
    success: bool                 # 성공 여부
    stdout: str                   # 표준 출력
    stderr: str                   # 표준 에러
    exit_code: int                # 종료 코드
    duration_seconds: float       # 실행 시간
```

---

### 4. file_monitor.py - 파일 시스템 모니터링

**위치**: `ai4pkm_cli/orchestrator/file_monitor.py`

**클래스**: `FileMonitor`

**역할**: `watchdog` 라이브러리 기반 파일 감시

**주요 메서드**:
```python
class FileMonitor:
    def __init__(
        self,
        vault_path: Path,
        agent_registry: AgentRegistry,
        execution_manager: ExecutionManager
    ):
        """Initialize file monitor."""
        self.observer = Observer()  # watchdog Observer

    def start(self):
        """Start monitoring file system."""
        # agent_registry에서 input_path 목록 가져오기
        # 각 경로에 대해 watchdog EventHandler 등록
        # observer.start()

    def stop(self):
        """Stop monitoring."""
        # observer.stop()

    def _on_file_event(self, event: FileSystemEvent):
        """
        Handle file system events.

        Args:
            event: watchdog 이벤트 (created, modified, deleted)
        """
        # 1. 파일 경로 추출
        # 2. AgentRegistry에서 매칭 에이전트 조회
        # 3. ExecutionManager로 실행
```

**감지 이벤트**:
- `FileCreatedEvent`: 새 파일 생성
- `FileModifiedEvent`: 파일 수정
- ❌ `FileDeletedEvent`: 무시 (삭제는 트리거하지 않음)

---

### 5. task_manager.py - 태스크 파일 관리

**위치**: `ai4pkm_cli/orchestrator/task_manager.py`

**클래스**: `TaskManager`

**역할**: `_Settings_/Tasks/` 디렉터리에 태스크 파일 생성 및 관리

**주요 메서드**:
```python
class TaskManager:
    def __init__(self, vault_path: Path, tasks_dir: str):
        """Initialize task manager."""
        self.tasks_dir = vault_path / tasks_dir

    def create_task(
        self,
        agent_name: str,
        file_path: Path,
        priority: str = "medium"
    ) -> Path:
        """
        Create a task file.

        Args:
            agent_name: 에이전트 이름
            file_path: 처리할 파일 경로
            priority: 우선순위 (high/medium/low)

        Returns:
            생성된 태스크 파일 경로

        Example:
            _Settings_/Tasks/2025-12-03-EIC-article.md
        """
        # 태스크 파일 생성
        # Frontmatter 작성

    def update_task_status(self, task_path: Path, status: str):
        """Update task status (pending → in_progress → done)."""
```

**태스크 파일 예**:
```markdown
---
agent: Enrich Ingested Content (EIC)
status: in_progress
priority: medium
created: 2025-12-03T08:00:00Z
input_file: Ingest/Clippings/article.md
output_file: AI/Articles/article-enriched.md
---

# Task: Enrich article.md

Processing...
```

---

### 6. cron_scheduler.py - 스케줄링

**위치**: `ai4pkm_cli/orchestrator/cron_scheduler.py`

**클래스**: `CronScheduler`

**역할**: `croniter` 라이브러리 기반 주기적 에이전트 실행

**주요 메서드**:
```python
class CronScheduler:
    def __init__(
        self,
        agent_registry: AgentRegistry,
        execution_manager: ExecutionManager
    ):
        """Initialize cron scheduler."""
        self.jobs: List[CronJob] = []

    def start(self):
        """Start cron scheduler."""
        # 에이전트 정의에서 cron 필드가 있는 것들 추출
        # 주기적으로 스케줄 확인
        # 실행 시간이 되면 ExecutionManager로 실행

    def _check_schedule(self):
        """Check if any job should run."""
        # croniter로 다음 실행 시간 계산
```

**Cron 표현식 예**:
```yaml
nodes:
  - name: Generate Daily Roundup (GDR)
    cron: "0 1 * * *"  # 매일 새벽 1시

  - name: Generate Weekly Roundup (GWR)
    cron: "0 9 * * 1"  # 매주 월요일 오전 9시
```

---

### 7. poller_manager.py - 외부 데이터 동기화

**위치**: `ai4pkm_cli/orchestrator/poller_manager.py`

**클래스**: `PollerManager`

**역할**: Poller 인스턴스 관리 및 주기적 실행

**주요 메서드**:
```python
class PollerManager:
    def __init__(self, config: OrchestratorConfig):
        """Initialize poller manager."""
        self.pollers: Dict[str, BasePoller] = {}
        # config의 pollers 섹션에서 enabled=true인 것들 로드

    def start(self):
        """Start all enabled pollers."""
        # 각 poller를 poll_interval마다 실행

    def stop(self):
        """Stop all pollers."""
```

**Poller 설정 예**:
```yaml
pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600  # 1시간

  limitless:
    enabled: true
    target_dir: "Ingest/Limitless"
    poll_interval: 3600
```

---

## Pollers (pollers/)

### 1. base_poller.py - 추상 클래스

**위치**: `ai4pkm_cli/pollers/base_poller.py`

**클래스**: `BasePoller` (ABC)

**역할**: 모든 Poller의 기본 인터페이스

**주요 메서드**:
```python
class BasePoller(ABC):
    def __init__(self, config: Dict[str, Any], vault_path: Path):
        """Initialize poller."""
        self.target_dir = vault_path / config['target_dir']
        self.poll_interval = config.get('poll_interval', 3600)

    @abstractmethod
    def poll(self):
        """Fetch data from external source and save to target_dir."""
        pass
```

---

### 2. gobi.py - Gobi 앱 동기화

**위치**: `ai4pkm_cli/pollers/gobi.py`

**클래스**: `GobiPoller`

**역할**: Gobi 앱 API 연동하여 메모 가져오기

**주요 메서드**:
```python
class GobiPoller(BasePoller):
    def poll(self):
        """Fetch Gobi notes and save as Markdown."""
        # 1. Gobi API 호출 (secrets.yaml에서 API 키 로드)
        # 2. 메모 목록 가져오기
        # 3. Markdown 파일로 변환
        # 4. target_dir에 저장 (Ingest/Gobi/)
```

---

### 3. limitless.py - Limitless AI 동기화

**위치**: `ai4pkm_cli/pollers/limitless.py`

**클래스**: `LimitlessPoller`

**역할**: Limitless AI 녹취록 가져오기

**주요 메서드**:
```python
class LimitlessPoller(BasePoller):
    def poll(self):
        """Fetch Limitless transcripts and save as Markdown."""
        # 1. Limitless API 호출
        # 2. 최근 7일 녹취록 가져오기
        # 3. Markdown 파일로 변환
        # 4. target_dir에 저장 (Ingest/Limitless/)
```

---

### 4. apple_photos.py - Apple Photos 동기화

**위치**: `ai4pkm_cli/pollers/apple_photos.py`

**클래스**: `ApplePhotosPoller`

**역할**: iCloud Photos 가져오기 (macOS only)

**주요 메서드**:
```python
class ApplePhotosPoller(BasePoller):
    def poll(self):
        """Fetch photos from Apple Photos library."""
        # 1. macOS Photos 라이브러리 접근
        # 2. 최근 7일 사진 가져오기
        # 3. metadata.yaml 생성
        # 4. target_dir에 저장 (Ingest/Photolog/)
```

---

## 설정 및 유틸리티

### 1. config.py - 설정 관리

**위치**: `ai4pkm_cli/config.py`

**클래스**: `Config`

**역할**: `orchestrator.yaml` 및 `secrets.yaml` 로드

**주요 메서드**:
```python
class Config:
    def __init__(self, vault_path: Path):
        """Load orchestrator.yaml and secrets.yaml."""
        self.vault_path = vault_path
        self.orchestrator_config = self._load_yaml('orchestrator.yaml')
        self.secrets = self._load_yaml('secrets.yaml', optional=True)

    def get(self, key: str, default=None):
        """Get config value by key."""

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret value (API keys, etc.)."""
```

---

### 2. logger.py - 로깅 시스템

**위치**: `ai4pkm_cli/logger.py`

**역할**: 통합 로깅 (파일 + 콘솔)

**주요 함수**:
```python
def setup_logger(vault_path: Path, debug: bool = False):
    """Setup logger with file and console handlers."""
    # 로그 파일: _Settings_/Logs/ai4pkm.log
    # 콘솔 출력: INFO 레벨 이상
    # 디버그 모드: DEBUG 레벨
```

---

### 3. markdown_utils.py - Markdown 유틸리티

**위치**: `ai4pkm_cli/markdown_utils.py`

**주요 함수**:
```python
def parse_frontmatter(file_path: Path) -> Tuple[Dict, str]:
    """
    Parse YAML frontmatter from Markdown file.

    Returns:
        (frontmatter_dict, content)
    """

def update_frontmatter(file_path: Path, updates: Dict):
    """Update frontmatter in-place."""

def create_markdown_file(
    file_path: Path,
    frontmatter: Dict,
    content: str
):
    """Create new Markdown file with frontmatter."""
```

---

## 테스트 (tests/)

### 테스트 구조
```
tests/
├── unit/                        # 유닛 테스트
│   ├── orchestrator/
│   │   ├── test_agent_registry.py
│   │   ├── test_execution_manager.py
│   │   └── test_file_monitor.py
│   └── main/
│       └── test_orchestrator.py
├── integration/                 # 통합 테스트
│   └── orchestrator/
│       └── test_content_matching.py
└── fixtures/                    # 테스트 데이터
    └── sample_vault/
```

---

## 의존성 라이브러리

**핵심 라이브러리** (`pyproject.toml`):
- `click`: CLI 명령어 파싱
- `watchdog`: 파일 시스템 모니터링
- `croniter`: Cron 표현식 파싱
- `pyyaml`: YAML 설정 파일 파싱
- `rich`: 터미널 출력 포맷팅
- `requests`: HTTP API 호출

---

## 다음 단계

- **[01_directory_structure.md](./01_directory_structure.md)**: 디렉터리 구조 개요
- **[03_config_file_guide.md](./03_config_file_guide.md)**: `orchestrator.yaml` 설정 가이드

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
