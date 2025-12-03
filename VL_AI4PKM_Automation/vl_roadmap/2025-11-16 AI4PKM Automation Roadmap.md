# AI4PKM 자동화 학습 로드맵 (3일 완주)

목표: ai4pkm 명령을 PowerShell(터미널)에서 활용하여 자동화 파이프라인을 실전 구동/점검/확장할 수 있게 합니다. 기본 환경세팅과 매뉴얼 사용법은 이미 숙지했다는 전제이며, 오직 자동화(CLI 실행, Orchestrator, Cron, 감시/로그)에만 집중합니다.

참고 자료
- 개요/핵심 설명: [[VL_AI4PKM_Automation/vl_ai4pkm_materials/00 - AI4PKM_프로젝트_설명]]
- 전체 자료 모음: `VL_AI4PKM_Automation/vl_ai4pkm_materials/`
- 유튜브 스크립트: `VL_AI4PKM_Automation/vl_ai4pkm_clippings/`

사전 준비(5분)
- PowerShell에서 아래 폴더로 이동: `Set-Location "c:\AI_study\PKM_Project\AI4PKM_2\AI4PKM\VL_AI4PKM_Automation"`
- 이 폴더의 `ai4pkm_cli.json`이 실행 설정에 적용됩니다. 실행 중 로그는 `._Settings_/Logs/ai4pkm_YYYY-MM-DD.log`에 기록됩니다.

---

## Day 1 — CLI 파악과 기본 명령 실습 (약 2~3시간)
목표: ai4pkm CLI 옵션/흐름 이해, 주요 명령 1회 이상 실행, 설정/로그 확인.

1) 환경/버전/설정 점검
- `ai4pkm --show-config`
- `ai4pkm --list-agents`
- (선택) 프롬프트 1회 실행: `ai4pkm -p "GDR"` 또는 `ai4pkm -a g -p "TKI"`

2) 기본 명령 실행(인자/결과 확인)
- 노트 처리: `ai4pkm -cmd "process_notes"`
- 사진 처리: `ai4pkm -cmd "process_photos"`
- 리포트(대화형): `ai4pkm -cmd "generate_report"`
- Gobi 제한 동기화(태그 기반):
  - `ai4pkm -cmd "sync-gobi-by-tags" -args '{ "tags": ["PKM","AI"] }'`
  - PowerShell에서는 JSON을 작은따옴표로 감싸면 이스케이프가 단순합니다.

3) 로그/산출물 검증
- 로그: `_Settings_/Logs/ai4pkm_*.log`에서 실행 흐름, 에러 확인
- 산출물/변환 위치: `Ingest/`, `AI/`, `Journal/` 등 변경 확인

Checkpoint & 기록
- 실행한 명령과 관찰한 변화, 이슈/개선 아이디어를 `VL_AI4PKM_Automation/vl_worklog/`에 간단히 기록

---

## Day 2 — Orchestrator·Cron·웹 API로 자동화 운영 (약 2~3시간)
목표: 파일 감시 기반 Orchestrator 데몬 이해/운영, Cron 잡 단발 테스트와 지속 실행, 웹 API 구동.

1) Orchestrator 상태/데몬
- 상태 확인: `ai4pkm --orchestrator-status`
- 데몬 실행: `ai4pkm -o` (중지: Ctrl+C)
- 동작 원리: `orchestrator.yaml`, `_Settings_/Prompts`, `_Settings_/Tasks`, 감시 핸들러(Watchdog) 참조

2) Cron 잡 운영
- 단발 테스트(대화형 선택): `ai4pkm -r`
- 지속 실행(웹 서버 포함): `ai4pkm -c` (중지: Ctrl+C)
- 크론 정의는 `ai4pkm_cli.json`의 `cron_jobs`에 명세
  예시 스니펫(참고용):
  ```json
  {
    "cron_jobs": [
      {
        "command": "process_notes",
        "cron": "0 9 * * *",
        "description": "매일 9시 최근 노트 처리"
      },
      {
        "command": "sync-gobi-by-tags",
        "arguments": {"tags": ["PKM","AI"]},
        "cron": "*/30 * * * *",
        "description": "30분마다 태그 동기화"
      }
    ]
  }
  ```

3) 웹 API 확인(로그 위주)
- `ai4pkm -c` 실행 시 Flask 웹 서버가 함께 구동됨(포트는 `ai4pkm_cli.json`의 `web_api.port`)
- 사용 시나리오: 외부 도구/스크립트에서 `/chat/completions` 호출 → 로그로 상태 확인

Checkpoint & 기록
- Orchestrator/cron 동작 스냅샷(로그 타임스탬프), 관찰 결과를 worklog에 캡처

---

## Day 3 — 미니 파이프라인 구성과 확장 (약 2~3시간)
목표: 실제 운영 흐름을 하루 루틴 수준으로 설계/검증하고, 에이전트/잡/프롬프트를 상황에 맞게 조정.

1) 미니 파이프라인 설계/실행
- 순서 예시: (a) `sync-gobi(-by-tags)` → (b) `process_notes` → (c) `generate_report`
- 모든 단계 로그/산출물 점검, 예상치 못한 파일/링크 문제 피드백 수집

2) 에이전트 조합/전환 실습
- 프롬프트 실행 시 에이전트 지정: `ai4pkm -a c -p "EIC"`
- 기본 에이전트는 `ai4pkm_cli.json`의 `default-agent`로 관리

3) 크론에 파이프라인 반영
- 예: 아침(동기화/노트), 저녁(리포트)로 분리 스케줄링
- `ai4pkm -r`로 단발 검증 → `ai4pkm -c`로 상시 운영

4) 운영 가이드 정리
- 장애/에러 대응(로그 경로, 재시도 지점)
- 안전 정지(Ctrl+C), 작업 중지 시의 일관성 확인
- 윈도우 환경 특성(경로/따옴표/인코딩) 요령 정리

최종 산출물
- `vl_worklog/`에 3일치 실행 기록/로그 포인터/개선 메모
- `vl_roadmap/`에 본 문서 링크를 상단에 추가 및 TODO 체크박스 정리

---

팁 & 베스트 프랙티스
- CWD 기반 설정: 항상 원하는 `ai4pkm_cli.json`이 있는 폴더에서 실행하세요.
- PowerShell 인자: JSON은 작은따옴표로 감싸면 편합니다. 예) `-args '{ "tags": ["PKM","AI"] }'`
- 로그 우선: 이슈가 생기면 `_Settings_/Logs/`를 먼저 확인하세요.
- 안전한 반복: `-r`로 단발 검증 → `-c`로 상시 운영 → 필요 시 Orchestrator(`-o`) 병행.
