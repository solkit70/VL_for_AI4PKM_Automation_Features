# Poller 시스템 가이드

**작성일**: 2025-12-24
**학습 단계**: Day 2, 세션 2
**학습 목표**: AI4PKM Poller 시스템의 동작 원리와 각 Poller 타입 이해

---

## 1. Poller란 무엇인가?

### 1.1 정의

**Poller**는 **외부 소스를 주기적으로 확인**하여 새로운 항목을 발견하면 에이전트를 트리거하는 컴포넌트입니다.

```
    Poller                    Orchestrator
       │                           │
       ├─── poll() ─────►  새 항목 발견
       │                           │
       └──────────────────►  TriggerEvent 생성
                                   │
                              Agent 실행
```

### 1.2 왜 Poller가 필요한가?

**파일 시스템 모니터링의 한계**:
- FileSystemMonitor는 **로컬 파일 변경**만 감지
- 외부 앱(Gobi, Limitless, Apple Notes 등)의 새 항목은 감지 불가능

**Poller의 역할**:
- 외부 API/데이터베이스를 주기적으로 확인
- 새 항목 발견 시 **자동으로 파일 생성** 또는 **이벤트 트리거**

### 1.3 Poller vs FileSystemMonitor

| 비교 항목 | FileSystemMonitor | Poller |
|----------|-------------------|--------|
| 감지 대상 | 로컬 파일 시스템 | 외부 앱/API |
| 동작 방식 | Watchdog (이벤트 기반) | 주기적 폴링 (time.sleep) |
| 실시간성 | 즉시 반응 | poll_interval에 따름 |
| 사용 사례 | 로컬 파일 추가/수정 | Gobi, Limitless 등 |

---

## 2. Poller 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│              PollerManager                              │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ GobiPoller   │  │ Limitless    │  │ AppleNotes   │ │
│  │              │  │ Poller       │  │ Poller       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │         │
│         └─────────────────┴─────────────────┘         │
│                          │                            │
│                   BasePoller (공통 로직)               │
└──────────────────────────┼──────────────────────────────┘
                           │
                     ┌─────▼─────┐
                     │ 외부 앱/API│
                     │ (Gobi 등)  │
                     └───────────┘
```

### 2.2 BasePoller (기본 클래스)

모든 Poller가 상속하는 기본 클래스:

```python
class BasePoller(ABC):
    """Base class for all pollers."""

    def __init__(self, poller_config, vault_path):
        self.poller_config = poller_config
        self.vault_path = vault_path
        self.target_dir = vault_path / poller_config['target_dir']
        self.poll_interval = poller_config.get('poll_interval', 3600)
        self.state = self.load_state()  # 이전 상태 로드
        self._running = False
        self._thread = None

    @abstractmethod
    def poll(self) -> None:
        """
        Poll for new items and create files.
        Subclasses must implement this method.
        """
        pass

    def start(self) -> None:
        """Start polling in background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop)
        self._thread.start()

    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                self.poll()  # 서브클래스 구현
            except Exception as e:
                self.logger.error(f"Poll error: {e}")

            # poll_interval만큼 대기
            time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop polling."""
        self._running = False
        if self._thread:
            self._thread.join()
```

**주요 기능**:
1. **상태 관리**: `load_state()`, `save_state()`
   - 이전에 어디까지 확인했는지 기억
   - 중복 처리 방지

2. **백그라운드 실행**: `start()`, `stop()`
   - 별도 스레드에서 주기적 실행
   - Orchestrator와 독립적으로 동작

3. **추상 메서드**: `poll()`
   - 각 Poller가 구현해야 함
   - 실제 폴링 로직

---

## 3. Poller 타입별 상세

### 3.1 GobiPoller

**목적**: Gobi 앱의 새 노트를 자동으로 Vault에 추가

**동작 방식**:
1. Gobi 데이터베이스 (`~/Library/Containers/com.gobi.app/Data/Library/Application Support/gobi.db`) 접근
2. 마지막 확인 이후 새 노트 검색
3. 새 노트를 Markdown 파일로 변환
4. `target_dir`에 저장

**설정 예시**:
```yaml
pollers:
  gobi:
    enabled: true
    target_dir: "_Inbox_"
    poll_interval: 300  # 5분마다
```

**상태 관리**:
```json
{
  "last_note_id": 12345,
  "last_poll_time": "2025-12-24T10:00:00"
}
```

**생성 파일 예시**:
```
_Inbox_/2025-12-24-gobi-note-title.md
```

### 3.2 GobiByTagsPoller

**목적**: Gobi 노트를 태그별로 분류하여 저장

**동작 방식**:
- GobiPoller와 유사
- 추가: 노트의 태그를 읽고 태그별 폴더에 저장

**설정 예시**:
```yaml
pollers:
  gobi_by_tags:
    enabled: true
    target_dir: "Projects"
    poll_interval: 300
    tag_mapping:
      "#work": "Projects/Work"
      "#personal": "Projects/Personal"
```

**생성 파일 예시**:
```
Projects/Work/2025-12-24-work-note.md     # #work 태그
Projects/Personal/2025-12-24-idea.md      # #personal 태그
```

### 3.3 LimitlessPoller

**목적**: Limitless 앱의 대화 및 노트를 가져오기

**동작 방식**:
1. Limitless API 호출
2. Starred conversations 및 새 항목 확인
3. Markdown 파일로 저장

**설정 예시**:
```yaml
pollers:
  limitless:
    enabled: true
    target_dir: "_Inbox_"
    poll_interval: 600  # 10분마다
    api_key: "${LIMITLESS_API_KEY}"  # 환경 변수
```

**최신 기능** (2025-12 업데이트):
- **Starred conversations 트래킹**
- API 키 누락 시 명확한 에러 메시지

**상태 관리**:
```json
{
  "last_conversation_id": "conv-123",
  "last_poll_time": "2025-12-24T10:00:00",
  "starred_conversations": ["conv-101", "conv-102"]
}
```

### 3.4 AppleNotesPoller

**목적**: Apple Notes의 새 노트를 Vault로 동기화

**동작 방식**:
1. macOS Notes 데이터베이스 접근
2. 새 노트 확인
3. HTML → Markdown 변환
4. `target_dir`에 저장

**설정 예시**:
```yaml
pollers:
  apple_notes:
    enabled: true
    target_dir: "_Inbox_"
    poll_interval: 1800  # 30분마다
```

**주의사항**:
- macOS 전용
- 데이터베이스 권한 필요

### 3.5 ApplePhotosPoller

**목적**: Apple Photos의 새 사진을 Vault로 복사

**동작 방식**:
1. macOS Photos 라이브러리 접근
2. 최근 사진 확인
3. 사진을 `target_dir`로 복사
4. 메타데이터 Markdown 생성

**설정 예시**:
```yaml
pollers:
  apple_photos:
    enabled: true
    target_dir: "Photos"
    poll_interval: 3600  # 1시간마다
    filter:
      favorites_only: true  # 즐겨찾기만
```

**생성 파일 예시**:
```
Photos/2025-12-24-IMG_1234.jpg
Photos/2025-12-24-IMG_1234.md  # 메타데이터
```

---

## 4. Poller 설정 가이드

### 4.1 orchestrator.yaml에서 Poller 활성화

```yaml
# orchestrator.yaml

orchestrator:
  prompts_dir: "_Settings_/Prompts"
  tasks_dir: "_Settings_/Tasks"
  logs_dir: "_Settings_/Logs"

  # Poller 설정
  pollers:
    # Gobi Poller
    gobi:
      enabled: true
      target_dir: "_Inbox_"
      poll_interval: 300  # 초 단위 (5분)

    # Limitless Poller
    limitless:
      enabled: true
      target_dir: "_Inbox_"
      poll_interval: 600
      api_key: "${LIMITLESS_API_KEY}"

    # Apple Notes Poller
    apple_notes:
      enabled: false  # 비활성화
      target_dir: "_Inbox_"
      poll_interval: 1800
```

### 4.2 필수 설정 항목

모든 Poller 공통:
- **enabled**: `true` 또는 `false`
- **target_dir**: 파일을 저장할 디렉터리 (상대 경로)
- **poll_interval**: 폴링 주기 (초 단위)

Poller별 추가 설정:
- **limitless.api_key**: Limitless API 키
- **gobi_by_tags.tag_mapping**: 태그별 폴더 매핑

### 4.3 환경 변수 사용

민감한 정보(API 키)는 환경 변수로 관리:

```yaml
# orchestrator.yaml
pollers:
  limitless:
    api_key: "${LIMITLESS_API_KEY}"  # 환경 변수 참조
```

```bash
# .env 파일 또는 셸 설정
export LIMITLESS_API_KEY="your-api-key-here"
```

---

## 5. Poller 동작 흐름

### 5.1 Poller 라이프사이클

```
1. Orchestrator 시작
   ↓
2. PollerManager 초기화
   - orchestrator.yaml 읽기
   - enabled: true인 Poller만 로드
   ↓
3. 각 Poller 인스턴스 생성
   - BasePoller.__init__()
   - load_state() - 이전 상태 복구
   ↓
4. Poller 시작
   - start() 호출
   - 백그라운드 스레드 시작
   ↓
5. 폴링 루프 (무한 반복)
   ├─ poll() 실행
   │  ├─ 외부 소스 확인
   │  ├─ 새 항목 발견
   │  └─ target_dir에 파일 생성
   ├─ save_state() - 상태 저장
   └─ time.sleep(poll_interval)
   ↓
6. Orchestrator 종료 시
   - stop() 호출
   - 스레드 정리
```

### 5.2 예시: GobiPoller 실행 흐름

```python
# 1. Orchestrator가 GobiPoller 시작
poller.start()

# 2. 백그라운드 스레드에서 _poll_loop() 실행
while self._running:
    # 3. poll() 호출
    self.poll()  # GobiPoller.poll() 구현

    # 4. Gobi DB 확인
    new_notes = query_gobi_db(last_note_id)

    # 5. 새 노트 발견
    for note in new_notes:
        # 6. Markdown 파일 생성
        file_path = target_dir / f"{note.title}.md"
        file_path.write_text(note.content)

        # 7. 상태 업데이트
        self.state['last_note_id'] = note.id

    # 8. 상태 저장
    self.save_state()

    # 9. 다음 폴링까지 대기
    time.sleep(300)  # 5분
```

### 5.3 파일 생성 → 에이전트 트리거 연결

```
1. Poller가 파일 생성
   _Inbox_/gobi-note.md 생성
   ↓
2. FileSystemMonitor가 감지
   TriggerEvent(create, "_Inbox_/gobi-note.md")
   ↓
3. AgentRegistry가 에이전트 매칭
   - trigger_pattern: "_Inbox_/**/*.md"
   - trigger_event: "create"
   ↓
4. Agent 실행
   (예: "Process Inbox" 에이전트)
```

---

## 6. Poller 메커니즘 변경사항

### 6.1 이벤트 기반 → time.sleep 기반 (2025-12 업데이트)

**변경 이유**:
- 안정성 향상
- 리소스 사용 최적화
- 디버깅 용이

**이전 방식** (이벤트 기반):
```python
# Event 기반 동기화
event.wait(timeout=poll_interval)
```

**현재 방식** (time.sleep):
```python
# time.sleep 기반
time.sleep(poll_interval)
```

**장점**:
- 더 예측 가능한 동작
- CPU 사용량 감소
- 로그 추적 용이

---

## 7. Poller 상태 관리

### 7.1 state.json 파일

각 Poller는 `target_dir/state.json`에 상태 저장:

```json
{
  "last_poll_time": "2025-12-24T10:30:00",
  "last_note_id": 12345,
  "processed_items": ["item1", "item2"],
  "custom_data": {
    "starred_conversations": ["conv-101"]
  }
}
```

**용도**:
- 중복 처리 방지
- Orchestrator 재시작 후 이어서 폴링
- 디버깅 및 모니터링

### 7.2 상태 초기화

Poller를 처음부터 다시 실행하고 싶을 때:

```bash
# state.json 삭제
rm _Inbox_/state.json

# Orchestrator 재시작
ai4pkm -o
```

---

## 8. Poller 트러블슈팅

### 8.1 Poller가 시작하지 않음

**증상**:
```
# Orchestrator 시작 시 Poller 로드 안 됨
✓ Loaded 0 poller(s)
```

**원인 및 해결**:
1. **enabled: false로 설정됨**
   ```yaml
   pollers:
     gobi:
       enabled: true  # false → true로 변경
   ```

2. **target_dir 누락**
   ```yaml
   pollers:
     gobi:
       target_dir: "_Inbox_"  # 필수!
   ```

3. **잘못된 YAML 문법**
   ```bash
   # YAML 검증
   python -c "import yaml; yaml.safe_load(open('orchestrator.yaml'))"
   ```

### 8.2 API 키 오류 (Limitless)

**증상**:
```
Error: Missing Limitless API key
```

**해결**:
```bash
# 환경 변수 설정
export LIMITLESS_API_KEY="your-api-key"

# 또는 orchestrator.yaml에 직접 입력 (권장하지 않음)
pollers:
  limitless:
    api_key: "your-api-key"
```

### 8.3 중복 파일 생성

**증상**:
같은 항목이 여러 번 저장됨

**원인**:
- state.json 손상 또는 삭제됨

**해결**:
1. Orchestrator 중지
2. state.json 확인 및 복구
3. 재시작

---

## 9. 커스텀 Poller 작성 (고급)

### 9.1 새 Poller 클래스 생성

```python
# ai4pkm_cli/pollers/my_poller.py

from pathlib import Path
from typing import Any, Dict
from .base_poller import BasePoller
from ..logger import Logger

logger = Logger()

class MyCustomPoller(BasePoller):
    """Custom poller for my external app."""

    def poll(self) -> None:
        """Poll my external app for new items."""
        # 1. 외부 소스 확인
        new_items = self.fetch_new_items()

        # 2. 새 항목 처리
        for item in new_items:
            # 3. Markdown 파일 생성
            file_path = self.target_dir / f"{item.title}.md"
            content = self.format_item(item)
            file_path.write_text(content, encoding='utf-8')

            self.logger.info(f"Created {file_path}")

        # 4. 상태 업데이트
        if new_items:
            self.state['last_item_id'] = new_items[-1].id
            self.save_state()

    def fetch_new_items(self):
        """Fetch new items from external source."""
        # 외부 API 호출 또는 DB 쿼리
        pass

    def format_item(self, item):
        """Format item as Markdown."""
        return f"# {item.title}\n\n{item.content}"
```

### 9.2 PollerManager에 등록

```python
# ai4pkm_cli/orchestrator/poller_manager.py

from ..pollers.my_poller import MyCustomPoller

poller_classes = {
    'apple_photos': ApplePhotosPoller,
    'gobi': GobiPoller,
    'my_custom': MyCustomPoller,  # 추가!
}
```

### 9.3 orchestrator.yaml에서 활성화

```yaml
pollers:
  my_custom:
    enabled: true
    target_dir: "_Inbox_"
    poll_interval: 600
```

---

## 10. 주요 학습 포인트

### 10.1 Poller의 핵심 역할

1. **외부 소스 통합**
   - Gobi, Limitless, Apple 생태계 등
   - API 기반 또는 DB 기반 폴링

2. **자동화**
   - 주기적 확인 (poll_interval)
   - 새 항목 자동 다운로드

3. **상태 관리**
   - state.json으로 이력 추적
   - 중복 방지

4. **확장성**
   - BasePoller 상속으로 새 Poller 추가 용이

### 10.2 Poller vs FileSystemMonitor

- **Poller**: 외부 → 내부 (Pull)
- **FileSystemMonitor**: 내부 감시 (Push)

둘이 협력하여 완전한 자동화:
```
External App → Poller → File Creation → FileSystemMonitor → Agent
```

---

## 11. 다음 단계

세션 3에서 다룰 내용:
- **Orchestrator 실행 실습**
- **Poller 동작 확인**
- **로그 분석**

---

**학습 완료**: 2025-12-24
**다음 학습**: Orchestrator 실행 실습
