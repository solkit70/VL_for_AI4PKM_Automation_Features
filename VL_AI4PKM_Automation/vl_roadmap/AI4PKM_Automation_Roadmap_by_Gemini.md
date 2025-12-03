# AI4PKM 자동화 기능 학습 로드맵 (3일 과정) by Gemini

이 로드맵은 AI4PKM 프로젝트의 자동화 기능을 3일 안에 학습할 수 있도록 설계되었습니다. 기본적인 환경 설정 및 수동 실행 방법은 이미 숙지하고 있다는 전제 하에, `ai4pkm` CLI를 통한 자동화 파이프라인 구축 및 실행에 초점을 맞춥니다.

---

## 1일차: 핵심 구조 이해 및 기본 명령어 실행

### 학습 목표
- AI4PKM CLI의 전체적인 아키텍처와 주요 구성 요소의 역할을 파악합니다.
- 간단한 동기화 및 처리 명령어를 실행하여 CLI 환경에 익숙해집니다.

### 학습 내용
1.  **자동화 아키텍처 분석 (`VL_AI4PKM_Automation/vl_ai4pkm_materials/00 - AI4PKM_프로젝트_설명.md` 기반)**
    -   `main.py`: 모든 CLI 명령어의 시작점(`click` 라이브러리 기반).
    -   `cli.py`: 명령어 실행의 핵심 로직을 담고 있는 `PKMApp` 클래스.
    -   `commands/command_runner.py`: `-cmd` 옵션으로 실행되는 개별 명령어들을 매핑하고 실행하는 모듈.
    -   `config.py` 및 `ai4pkm_cli.json`: 프로젝트의 모든 설정을 관리하는 방식.

2.  **기본 명령어 종류 파악**
    -   `ai4pkm_cli/commands/` 폴더를 통해 사용 가능한 명령어의 종류를 확인합니다.
        -   `sync_limitless_command.py`: Limitless 녹음 데이터 동기화.
        -   `process_notes.py`: Bear/Apple Notes에서 가져온 노트 처리.
        -   `process_photos.py`: 지정된 폴더의 사진 처리.
        -   `sync_gobi_command.py`: Gobi 로그 데이터 동기화.

### 실습 과제
1.  **사용 가능한 에이전트 목록 확인**
    -   터미널에서 다음 명령어를 실행하여 `agent_factory.py`가 인식하는 AI 에이전트 목록을 확인합니다.
    ```bash
    python -m ai4pkm_cli.main --list-agents
    ```

2.  **Limitless 데이터 동기화 (Dry-run)**
    -   실제 파일을 변경하지 않고 어떤 작업이 수행될지 확인하기 위해 `--dry-run` 플래그를 사용하여 동기화 명령을 실행합니다.
    -   이 과정은 `sync_limitless_command`가 어떻게 동작하는지 이해하는 데 도움이 됩니다.
    ```bash
    python -m ai4pkm_cli.main -cmd sync-limitless --dry-run
    ```

---


## 2일차: 프롬프트 실행 및 AI 에이전트 활용

### 학습 목표
- `-p` 옵션을 사용하여 개별 프롬프트를 직접 실행하는 방법을 배웁니다.
- 설정 파일을 변경하여 다른 AI 에이전트(Claude, Gemini 등)를 활성화하고 사용하는 방법을 익힙니다.

### 학습 내용
1.  **프롬프트 시스템 이해**
    -   `ai4pkm_vault/_Settings_/Prompts/` 폴더에 정의된 다양한 프롬프트의 역할과 구조를 학습합니다.
        -   `GDR (Generate Daily Roundup)`: 일일 요약 생성.
        -   `EIC (Edit, Improve, Correct)`: 텍스트 교정 및 개선.
        -   `CTP (Complete Task Prompt)`: 주어진 태스크 완료.
    -   프롬프트가 어떻게 입력 파일을 받아 처리하고 결과를 출력하는지 흐름을 파악합니다.

2.  **AI 에이전트 전환 및 활용**
    -   `agent_factory.py`가 `ai4pkm_cli.json`의 `default_agent` 설정을 읽어 AI 에이전트를 선택하는 원리를 이해합니다.
    -   `agents/` 폴더의 `claude_agent.py`, `gemini_agent.py` 등이 어떻게 외부 CLI를 호출하여 작업을 수행하는지 확인합니다.

### 실습 과제
1.  **특정 파일에 EIC 프롬프트 실행**
    -   `_Inbox_` 폴더나 임의의 마크다운 파일을 대상으로 EIC 프롬프트를 실행하여 내용이 어떻게 개선되는지 확인합니다.
    -   `--prompt-args`를 사용하여 프롬프트에 필요한 인자(입력 파일 경로 등)를 전달합니다.
    ```bash
    python -m ai4pkm_cli.main -p EIC --prompt-args "input_file:C:\path\to\your\note.md"
    ```

2.  **기본 AI 에이전트 변경 및 실행**
    -   `ai4pkm_cli.json` 파일을 열어 `default_agent` 값을 "gemini"에서 "claude"로 또는 그 반대로 변경합니다.
    -   이후, 위에서 실행했던 동일한 프롬프트를 다시 실행하여 다른 AI 에이전트의 결과물이 어떻게 다른지 비교합니다.

---


## 3일차: Orchestrator와 Cron을 이용한 완전 자동화

### 학습 목표
-   파일 시스템의 변경을 감지하여 자동으로 작업을 처리하는 Orchestrator의 작동 방식을 이해합니다.
-   정해진 시간에 주기적으로 작업을 실행하는 Cron 설정 방법을 배웁니다.

### 학습 내용
1.  **Orchestrator 심층 분석**
    -   `orchestrator_cli.py`와 `orchestrator/core.py`가 자동화의 중심임을 이해합니다.
    -   `orchestrator.yaml` 파일의 구조를 분석하여, 어떤 폴더의 어떤 파일 패턴(`watch_path`, `glob_patterns`)이 어떤 프롬프트(`prompt_name`)와 에이전트(`agent`)를 트리거하는지 학습합니다.
    -   `watchdog/` 폴더의 파일 감시 모듈이 어떻게 Orchestrator와 연동되는지 파악합니다.

2.  **Cron 작업 설정 및 관리**
    -   `cron_manager.py`가 `ai4pkm_cli.json`의 `cron_jobs` 섹션을 읽어 스케줄을 관리하는 방식을 이해합니다.
    -   `cron_jobs`에 새로운 작업을 추가하고, 특정 시간에 특정 명령어(`-cmd`)나 프롬프트(`-p`)가 실행되도록 설정하는 방법을 배웁니다.

### 실습 과제
1.  **Orchestrator를 통한 자동 클리핑 처리**
    -   `orchestrator.yaml`에 `Ingest/Clippings/` 폴더를 감시하는 설정이 있는지 확인합니다.
    -   웹에서 새로운 기사를 클리핑하여 `Ingest/Clippings/` 폴더에 저장합니다.
    -   터미널에서 Orchestrator를 데몬 모드로 실행합니다.
        ```bash
        python -m ai4pkm_cli.main -o --daemon
        ```
    -   Orchestrator가 파일 생성을 감지하고, 해당 클리핑에 대해 지정된 프롬프트(예: `EIC`)를 실행하여 처리 결과를 `AI/` 폴더 등에 저장하는지 관찰합니다.

2.  **매일 아침 데일리 저널 생성 Cron 작업 테스트**
    -   `ai4pkm_cli.json`의 `cron_jobs`에 `GDR` 프롬프트를 매일 특정 시간에 실행하는 작업이 있는지 확인하거나 추가합니다.
    -   Cron 테스트 명령어를 사용하여 실제로 지정된 시간이 되지 않아도 작업이 정상적으로 실행되는지 확인합니다.
    ```bash
    python -m ai4pkm_cli.main -c --test-job "Generate Daily Roundup"
    ```
    -   실행 후 `Journal/` 폴더에 오늘 날짜의 라운드업 파일이 생성되었는지 확인합니다.

---


이 로드맵을 통해 3일간 AI4PKM의 강력한 자동화 기능들을 체계적으로 학습하고 실제 프로젝트에 적용할 수 있게 될 것입니다.
