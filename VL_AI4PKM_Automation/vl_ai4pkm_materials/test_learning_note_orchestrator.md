# AI4PKM Orchestrator 학습 노트

## 개요

AI4PKM Orchestrator는 멀티 에이전트 시스템을 조율하는 핵심 엔진입니다. 이벤트 기반 아키텍처를 통해 파일 시스템 감시, 외부 소스 폴링, 스케줄링을 통합 관리합니다.

## 핵심 구성 요소

### 1. Orchestrator Core

메인 이벤트 루프를 실행하며 모든 구성 요소를 초기화하고 관리합니다.

**주요 책임**:
- 설정 파일 (orchestrator.yaml) 로드
- 모든 매니저 컴포넌트 초기화
- 이벤트 큐 관리 및 이벤트 디스패칭
- 전체 시스템의 라이프사이클 관리

**실행 흐름**:
```
1. 설정 로드 (orchestrator.yaml)
2. Agent Registry 초기화
3. Execution Manager 시작
4. FileSystem Monitor 시작
5. Poller Manager 시작 (있는 경우)
6. Cron Scheduler 시작 (있는 경우)
7. 이벤트 루프 실행
```

### 2. Agent Registry

에이전트를 등록하고 관리하는 컴포넌트입니다.

**기능**:
- 프롬프트 파일 자동 스캔 및 파싱
- 에이전트 메타데이터 관리 (이름, 약어, 카테고리)
- 에이전트 검색 및 조회 인터페이스 제공

**프롬프트 파일 구조**:
```yaml
---
title: Agent Name
abbreviation: AN
category: category_name
---
프롬프트 내용...
```

### 3. Execution Manager

에이전트 실행을 관리하고 동시성을 제어합니다.

**주요 기능**:
- 실행 큐 관리
- 동시 실행 수 제어 (max_concurrent)
- Executor (Claude Code, Gemini) 호출
- 실행 결과 처리 및 로깅
- 에러 핸들링 및 재시도 로직

**실행 컨텍스트**:
```python
ExecutionContext:
  - agent_name: 실행할 에이전트
  - input_files: 입력 파일 목록
  - output_path: 출력 경로
  - executor: 사용할 AI 실행기
  - timeout: 타임아웃 설정
```

### 4. FileSystem Monitor

파일 시스템 변경을 감지하고 이벤트를 생성합니다.

**감시 대상**:
- orchestrator.yaml에 정의된 input_path
- 새 파일 생성
- 파일 수정
- 파일 삭제 (선택적)

**이벤트 생성**:
- 변경 감지 → TriggerEvent 생성
- 이벤트 큐에 전달
- Execution Manager가 처리

### 5. Poller Manager

외부 소스에서 주기적으로 데이터를 가져옵니다.

**지원 Poller**:
- Gobi Poller: Gobi 서비스에서 클리핑 가져오기
- Limitless Poller: Limitless 서비스 연동
- Apple Notes Poller: Apple Notes 동기화
- Apple Photos Poller: Apple Photos 가져오기
- Gobi By Tags Poller: 태그 기반 필터링

**동작 방식**:
- 백그라운드 스레드에서 실행
- poll_interval 주기로 폴링
- 새 데이터 발견 시 파일로 저장
- FileSystem Monitor가 감지하여 처리

### 6. Cron Scheduler

스케줄 기반 에이전트 실행을 관리합니다.

**스케줄 형식**:
```yaml
nodes:
  - type: agent
    name: Daily Report
    cron: "0 9 * * *"  # 매일 오전 9시
```

## 데이터 모델

### TriggerEvent

```python
TriggerEvent:
  - event_type: "file_created" | "file_modified" | "poller" | "cron"
  - source_path: 이벤트 소스 경로
  - agent_name: 처리할 에이전트
  - metadata: 추가 정보
```

### AgentDefinition

```python
AgentDefinition:
  - name: 에이전트 이름
  - abbreviation: 약어
  - category: 카테고리
  - prompt_path: 프롬프트 파일 경로
  - input_path: 입력 경로 (list 가능)
  - output_path: 출력 경로
  - executor: 실행기 (claude_code, gemini)
  - enabled: 활성화 여부
  - timeout_minutes: 타임아웃
  - max_parallel: 최대 동시 실행 수
```

## 설정 파일 (orchestrator.yaml)

### 기본 구조

```yaml
version: "1.0"
orchestrator:
  prompts_dir: _Settings_/Prompts
  tasks_dir: _Settings_/Tasks
  logs_dir: _Settings_/Logs
  max_concurrent: 3
  poll_interval: 1
  executors:
    claude_code:
      command: claude
    gemini:
      command: gemini

defaults:
  executor: claude_code
  timeout_minutes: 30
  max_parallel: 3

nodes:
  - type: agent
    name: Agent Name
    abbreviation: an
    input_path: input/
    output_path: output/
```

### 고급 설정

**여러 입력 경로**:
```yaml
input_path:
  - path1/
  - path2/
  - path3/
```

**파일 패턴 필터**:
```yaml
input_pattern: "*.md"
exclude_pattern: "*_processed.md"
```

**트리거 조건**:
```yaml
trigger_content_pattern: "%% #process %%"
post_process_action: remove_trigger_content
```

## 실행 흐름 예시

### 1. 파일 기반 트리거

```
1. 사용자가 vl_ai4pkm_clippings/article.md 생성
2. FileSystem Monitor가 변경 감지
3. TriggerEvent 생성 (type: file_created)
4. Execution Manager가 이벤트 수신
5. 해당 경로를 감시하는 에이전트 찾기 (EIC)
6. ExecutionContext 생성
7. Executor (Claude Code) 호출
8. 결과를 vl_ai4pkm_materials/article_enriched.md에 저장
```

### 2. Poller 기반 트리거

```
1. Gobi Poller가 1시간마다 실행
2. Gobi API에서 새 클리핑 확인
3. 새 클리핑을 vl_ai4pkm_clippings/에 저장
4. FileSystem Monitor가 감지
5. 이후는 파일 기반 트리거와 동일
```

### 3. 스케줄 기반 트리거

```
1. Cron Scheduler가 "0 9 * * *" 체크
2. 시간 도달 시 TriggerEvent 생성
3. Daily Report 에이전트 실행
4. 어제의 모든 활동 요약
5. 결과를 Reports/daily_YYYYMMDD.md에 저장
```

## 주요 명령어

### Orchestrator 관리

```bash
# 상태 확인
ai4pkm --orchestrator-status

# 에이전트 목록
ai4pkm --list-agents

# 설정 확인
ai4pkm --show-config

# 수동 트리거 (약어 사용)
ai4pkm -t eic

# 백그라운드 실행
ai4pkm --daemon
```

### 디버깅

```bash
# 로그 확인
cat _Settings_/Logs/orchestrator.log

# 특정 에이전트 테스트
ai4pkm -t sns --input test_note.md

# 설정 검증
ai4pkm --validate-config
```

## Best Practices

### 1. 에이전트 설계

- **단일 책임**: 하나의 에이전트는 하나의 명확한 작업만 수행
- **명확한 입출력**: input_path와 output_path를 명확히 분리
- **재사용 가능**: 프롬프트를 일반화하여 다양한 상황에 적용

### 2. 성능 최적화

- **max_concurrent 조정**: 시스템 리소스에 맞게 설정
- **timeout 설정**: 긴 작업은 timeout 증가
- **비동기 실행**: 독립적인 에이전트는 동시 실행

### 3. 에러 처리

- **로그 활용**: _Settings_/Logs/ 에서 문제 추적
- **점진적 배포**: 새 에이전트는 enabled: false로 시작
- **테스트**: 수동 트리거로 먼저 검증

### 4. 유지보수

- **버전 관리**: orchestrator.yaml을 Git으로 관리
- **문서화**: 프롬프트 파일에 description 추가
- **모니터링**: 정기적으로 orchestrator-status 확인

## 문제 해결

### 에이전트가 실행되지 않음

1. `--orchestrator-status`로 에이전트 로드 확인
2. `enabled: true` 설정 확인
3. input_path가 존재하는지 확인
4. 로그 파일 확인

### Executor 오류

1. Executor 설치 확인 (`where claude`, `where gemini`)
2. orchestrator.yaml의 executors 경로 확인
3. API 키 설정 확인 (환경 변수)

### 파일 감시 문제

1. input_path 경로 확인
2. 파일 권한 확인
3. exclude_pattern 확인

## 학습 체크리스트

- [ ] Orchestrator의 6가지 핵심 구성 요소를 설명할 수 있다
- [ ] orchestrator.yaml 파일 구조를 이해한다
- [ ] TriggerEvent가 생성되고 처리되는 과정을 설명할 수 있다
- [ ] 새로운 에이전트를 만들고 등록할 수 있다
- [ ] 파일 기반, Poller 기반, 스케줄 기반 트리거의 차이를 안다
- [ ] --orchestrator-status 명령어로 상태를 확인할 수 있다
- [ ] 에이전트 실행 문제를 디버깅할 수 있다

## 다음 학습 주제

- 커스텀 Poller 작성하기
- 복잡한 워크플로우 체인 구성
- Executor 커스터마이징
- 프로덕션 배포 가이드
