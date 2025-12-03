아래 문서는 https://jykim.github.io/AI4PKM/orchestrator.html (Last Updated: 2025-11-03, Version 1.0)을 기반으로, AI4PKM Orchestrator의 전체 내용을 한국어로 체계적으로 정리·확장한 학습 노트입니다. 로컬 저장소의 `AI4PKM_프로젝트_설명.md`보다 더 세밀한 설정·필드·동작을 포함합니다.

원문: https://jykim.github.io/AI4PKM/orchestrator.html

> 관련 노트: [[02 - Orchestrator 구현 스펙]] · [[03 - Agentic AI 아키텍처 해설]] · [[04 - 온디맨드 지식 태스크 아키텍처 해설]]

아래 페이지는 AI4PKM Orchestrator의 개념·설정·사용법을 한눈에 정리한 안내서입니다. 핵심은 “Obsidian Vault의 파일 변화를 감지 → 적절한 AI 에이전트(Claude/Gemini/Codex 등)를 자동 실행 → 결과물을 지정 위치에 기록”하는 멀티에이전트 자동화 시스템이라는 점입니다.

무엇을 하는가 (개요)

- 이벤트 기반 자동화: 클리핑/보이스노트/해시태그 등 파일 변화가 생기면 자동으로 해당 작업에 맞는 에이전트가 실행됩니다.
- 멀티에이전트 지원: Claude/Gemini/Codex 등 CLI 에이전트 라우팅을 지원하고, 동시에 여러 작업을 병렬 처리할 수 있습니다(동시성 한도 설정 가능).
- 투명한 추적: 실행 중 생성되는 Task 파일과 Log 파일로 처리 과정을 추적할 수 있습니다.
- YAML 설정: 전체 동작은 간단한 orchestrator.yaml로 선언적으로 구성합니다.

디렉터리와 설정 파일

Vault에는 최소 다음 구조가 필요합니다.

```
your-vault/
├── orchestrator.yaml              # 메인 구성 파일
├── _Settings_/
│   ├── Prompts/                   # 에이전트 프롬프트 정의 (Markdown)
│   │   ├── Enrich Ingested Content (EIC).md
│   │   ├── Hashtag Task Creator (HTC).md
│   │   └── ...
│   ├── Tasks/                     # 태스크 추적 파일 (자동 생성)
│   └── Logs/                      # 실행 로그 (자동 생성)
├── Ingest/
│   └── Clippings/                 # 입력: 웹 클리핑
└── AI/
  └── Articles/                  # 출력: 처리된 콘텐츠
```

orchestrator.yaml 핵심

orchestrator, defaults, nodes 세 블록으로 구성됩니다. 주요 포인트:

구성 요약 표:

| 블록 | 주요 키 | 설명 | 비고 |
|-------|---------|------|------|
| orchestrator | prompts_dir, tasks_dir, logs_dir, max_concurrent, poll_interval | 전역 디렉터리/동시성/폴링 설정 | 필수 블록 |
| defaults | executor, timeout_minutes, max_parallel, task_priority | 노드에서 값 없을 때 적용되는 기본값 | 생략 시 코드 폴백 일부 |
| nodes[*] | type, name, input_path, output_path, output_type, cron, trigger_* | 에이전트 라우팅 및 트리거/출력 제어 | 복수 정의 가능 |


- orchestrator: 프롬프트/태스크/로그 디렉터리, 동시 실행 수(max_concurrent), 폴링 주기(poll_interval) 등 런타임 전역 설정.
- defaults: 기본 실행자(executor: claude_code), 타임아웃(분), 에이전트별 기본 동시성 등 기본값.
- nodes: 실제 에이전트 라우팅 규칙. 각 항목이 하나의 에이전트 노드를 나타내며,
  - name(“Full Name (ABBR)”),
  - input_path(감시할 입력 디렉터리·리스트 가능),
  - output_path,
  - output_type(신규 파일 생성 new_file / 원본 갱신 update_file),
  - cron(향후 기능)
  등을 선언합니다. 예시로 EIC(Enrich Ingested Content)는 Ingest/Clippings에 새 파일이 생기면 자동 실행되어 AI/Articles에 결과를 생성하도록 설정합니다.

에이전트별 추가 옵션

- trigger_exclude_pattern: 트리거에서 제외할 글롭 패턴(예: _Settings_/*)
- trigger_content_pattern: 파일 내용에 정규식 매칭 시에만 실행(예: %% … #ai … %%)
- post_process_action: 사후처리(예: 트리거 마커 제거)
- executor/timeout_minutes/max_parallel/task_priority: 기본값을 노드 단위로 덮어쓰기 가능
  이 옵션들로 “특정 마커가 있을 때만 실행”, “우선순위 높은 작업은 병렬 1개만” 같은 세밀한 제어를 할 수 있습니다.

출력 모드

- new_file: 출력 디렉터리에 새 파일 생성(기본)
- update_file: 입력 파일을 제자리에서 수정(예: Journal 강화)
  오케스트레이터는 출력 생성/수정 여부를 검증하고, 원자적 쓰기(임시 파일 후 rename)도 감지하며, 후속 노드 트리거도 연쇄적으로 처리합니다.

프롬프트 파일 규격

- 위치: _Settings_/Prompts/
- 이름 규칙: {Full Name} ({ABBR}).md (예: Enrich Ingested Content (EIC).md)
- 최소 Frontmatter: title(노드명과 일치), abbreviation(예: “EIC”), category(ingestion/publish/research)
  본문에는 입력/출력 요구사항과 절차(예: 오탈자 수정 → Summary 추가 → 관련 토픽 링크) 등을 명시합니다. 이는 실행 시 오케스트레이터가 주입하는 출력 설정과 함께 품질 기준을 형성합니다.

CLI 사용법(요약)

- 상태 확인: `ai4pkm --orchestrator-status` → Vault 경로, 로드된 에이전트 수, 동시성, 에이전트 목록 등 확인
- 오케스트레이터 실행:
  - 기본: `ai4pkm -o`
  - 동시성 변경: `ai4pkm -o --max-concurrent 5`
  실행 중 Ctrl+C로 안전 종료, 로그는 `_Settings_/Logs/`, 태스크는 `_Settings_/Tasks/`에서 확인합니다.

참고 자료와 코드 위치

문서에서는 아키텍처 블로그, 온디맨드 태스크 처리 배경 글, GitHub 저장소, 그리고 소스 코드 경로(Orchestrator Core, CLI, 예시 설정/프롬프트) 링크도 제공합니다. 마지막 업데이트는 2025-11-03, 버전 표기는 1.0 (nodes-based configuration) 입니다.

실무 팁 (이 문서 바탕으로 바로 적용하기)

- 최소 세팅: `_Settings_/Prompts`, `_Settings_/Logs`, `_Settings_/Tasks`, `orchestrator.yaml`만 갖추면 시작 가능. 첫 노드는 EIC로 추천.
- 점진 확장: `update_file` 모드로 Journal 강화(DNE)를 추가해 데일리 노트 품질을 자동 개선.
- 정밀 트리거: `trigger_content_pattern`로 “%% … #ai … %%” 마커가 있을 때만 실행하도록 하여 원치 않는 자동화를 방지.
- 성능/안정성: `max_concurrent`와 `max_parallel`을 단계적으로 올리며 병목과 충돌을 점검. 타임아웃도 작업 길이에 맞게 조정.
