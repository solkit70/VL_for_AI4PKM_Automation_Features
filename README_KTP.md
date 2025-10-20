# Knowledge Task Processor (KTP) System

- Use Watchdog to monitor target file change

## Task Routing (Phase 1)
Task Status: TBD -> IN PROGRESS
* ai4pkm에서 지원하는 agent에 보냄 (based on routing config)
* 여러 Task가 존재하는 경우 동시에 처리 가능

Task Routing Config
* Task Type
* Default Agent
* Timeout

## Execution & Monitoring (Phase 2)
Task Status: IN PROGRESS -> PROCESSED
* 수행 완료까지 확인하고 Task Status 업데이트 (PROCESSED)
* PROCESSED = 수행 완료, 평가 대기 중 (passive state)
* 에러시 Timeout logic 적용

## Results Evaluation & Follow-up (Phase 3)
Task Status: PROCESSED -> UNDER REVIEW -> COMPLETED
* Phase 3 시작 시 UNDER REVIEW로 상태 변경 (평가 진행 중, active state)
* 결과를 평가하고 보완 요청을 포함해 다시 수행
  * 예: EIC에서 일부 내용이 누락
  * 평가 기준은 Task Prompt에 포함
* 결과가 확인된 이후:
  * APPROVED → COMPLETED
  * FAILED → 실패 처리 (feedback 포함)

## Status Convention
- **PROCESSED**: Passive state - 작업 완료, 평가 대기 중
- **UNDER REVIEW**: Active state - 평가 진행 중

![[README_KTP 2025-10-15 17.22.03.excalidraw.svg]]
%%[[README_KTP 2025-10-15 17.22.03.excalidraw.md|🖋 Edit in Excalidraw]]%%