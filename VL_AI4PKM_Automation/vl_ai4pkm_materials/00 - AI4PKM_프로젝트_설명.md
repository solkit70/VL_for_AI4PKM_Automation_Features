아래 설명은 프로젝트 전체 구조, 각 구성요소의 용도, 동작 방식, 핵심 스펙과 활용 방법을 한국어로 포괄적으로 정리한 기술 해설입니다. ChatGPT에 옮겨 설명하거나 온보딩 문서로 바로 사용할 수 있도록 계층적으로 구성했습니다.

## 1. 프로젝트 개요

AI4PKM은 개인 지식 관리(PKM)를 AI 에이전트·자동화 파이프라인과 결합하여 “캡처 → 정리 → 통합 → 검색/표현” 루프를 지속적으로 유지하도록 설계된 Obsidian 기반 지식 베이스 + Python CLI 프레임워크입니다.  
핵심 목표:
- 여러 소스(클리핑, 메모, 녹음, 사진, 라이프로그)를 일정/이벤트/연구/저널 문맥으로 자동 통합
- 워크플로(Prompts + Orchestrator)로 일일/주간 라운드업과 콘텐츠 변환(EIC 등) 자동화
- 다중 AI 에이전트(Claude Code, Gemini CLI, Codex CLI)를 선택/교체 가능한 실행 파이프라인
- 파일 변화 감시(Watchdog) + Cron + Orchestrator로 지속적 처리

## 2. 상위 디렉터리 구조 (Vault 관점)

| 디렉터리 | 용도 |
|----------|------|
| `ai4pkm_vault/_Settings_/Prompts/` | 워크플로/태스크를 정의하는 개별 Prompt 명세 (예: GDR, EIC, CTP 등) |
| `ai4pkm_vault/_Settings_/Templates/` | 노트 생성 시 사용하는 템플릿 (Journal, Topic 등) |
| `ai4pkm_vault/_Settings_/Workflows/` | 인간 + AI 협업 프로세스 문서화 |
| `AI/` | AI가 생성한 결과물(Research, Roundup, Sharable 등) |
| `Ingest/` | 외부 입력 원천(Clippings, Limitless, Gobi, Photolog 등)의 원본/초벌 캡처 |
| `Journal/` | 날짜별 데일리 저널(일일 라운드업과 상호 링크) |
| `Topics/` | 주제별 지식(아직 일부 미생성; 라운드업에서 “Topics to Create”로 관리) |
| `Projects/`, `Publish/` | 프로젝트와 공개용 아티팩트 |
| `ai4pkm_cli/` | Python CLI 실행 프레임워크 (코드, 에이전트, 오케스트레이터, 명령) |
| `docs/` | 마이그레이션/사양 문서 (예: KTM→Multi-Agent 전환 문서 등) |

Obsidian 관점: Vault로 열면 `_Settings_` 하위에 Prompts/Workflows/Templates가 있어 “AI 헬퍼” 레이어를 제공, 사용자는 일반 노트(Edit) + AI 실행 결과(Write-Back)를 한 곳에서 순환.

## 3. Python CLI (`ai4pkm_cli`) 구성

주요 파일/모듈 기능:

- `main.py`  
  - `click` 기반 단일 진입점. 옵션으로 프롬프트 실행(-p), 명령 실행(-cmd), 크론 실행(-c), 오케스트레이터(-o), KTP(Deprecated) 등을 선택.
- `cli.py (PKMApp)`  
  - 구성 초기화(Config) + 에이전트 선택(AgentFactory) + CronManager + 서버(Server).  
  - Prompt 직접 실행(`execute_prompt`), Command 실행(`execute_command`), 크론 테스트, Task Management 모드(Deprecated) 포함.
- `config.py`  
  - `ai4pkm_cli.json` 로드/저장. 기본 설정(에이전트, 크론, 사진/노트 처리, orchestrator 경로 등) merge.
- `agent_factory.py`  
  - 설정된 기본 에이전트(fallback 포함) 인스턴스 생성. 사용 가능한 에이전트 목록 조회.
- `agents/`  
  - `base_agent.py`: 공통 추상 인터페이스(run_prompt, is_available 등)  
  - `claude_agent.py`: Claude Code CLI 호출(권한 모드 bypass) + fallback 텍스트  
  - `gemini_agent.py`: Gemini CLI (`--prompt`, `--approval-mode`) 실행  
  - `codex_agent.py`: (유사 패턴, 코드 생략됐지만 동일 구조 추정)
- `commands/command_runner.py`  
  - 문자열 명령 → 실제 처리 모듈 매핑 (`process_photos`, `process_notes`, `ktp`, `sync-limitless` 등)
- `orchestrator_cli.py` + `orchestrator/core` (파일 일부만 노출)  
  - 차세대 멀티에이전트 데몬. `orchestrator.yaml` 정의된 노드를 기반으로 파일 입력 감시 후 Prompt/에이전트 실행.
- `server.py`  
  - Flask 기반 Web API (Vapi 호환 `/chat/completions`) + SSE 스트리밍.  
  - Gobi 로그 파일 파싱 API, 정적 리소스 제공. 음성 최적화 응답 처리.
- `watchdog/`  
  - 파일 감시 핸들러(Task, Clippings, Hashtags 등). 변경 감지 → 처리 파이프라인 트리거.
- `cron_manager.py`  
  - `ai4pkm_cli.json` 의 `cron_jobs` 목록을 일정에 따라 실행.
- `markdown_utils.py`, `utils.py`, `logger.py`  
  - 마크다운 처리 유틸, 로깅, 공통 도구.

... (이하 원문과 동일 — 기존 파일 전체 내용을 그대로 복사)
