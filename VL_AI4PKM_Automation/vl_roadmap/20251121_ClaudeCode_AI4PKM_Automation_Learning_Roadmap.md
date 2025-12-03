# AI4PKM 자동화 기능 학습 로드맵 (3일 과정)

**작성일**: 2025-11-21
**작성자**: Claude Code
**학습 목표**: AI4PKM의 터미널 기반 자동화 스크립트 기능을 실습 중심으로 마스터하기

---

## 📋 전제 조건

이 로드맵은 다음을 이미 완료했다고 가정합니다:
- ✅ AI4PKM 환경 설정 완료
- ✅ Obsidian vault 기본 구조 이해
- ✅ 수동 실행 방법 숙지 (YouTube 영상 학습 완료)
   - [AI-powered PKM Practice — Setting up Obsidian & Saving Web Info Locally with One Click (Web Clipper)](https://youtu.be/Ku4_N4b78rc?si=R1mqCCDVE-gGGRc2) — Quick walkthrough for Obsidian setup and one‑click web clipping. (English)

   - [AI-powered PKM 실습 — AI와 PKM의 만남 (프로그래밍 언어 없이 앱 개발)](https://youtu.be/SkeQinoBkDw?si=9QtSoVWyi7CciBly) — 한국어 설명과 데모 영상입니다.

   - [실전 Vibe Coding — AI4PKM에 Vibe Learning Onboarding](https://youtu.be/LEWr-1-SOcE?si=r9dIkNr_pix6f5g4) — 개념 설명부터 실습까지 포함한 실전 가이드.

   - [PKM Project YouTube Playlist](https://www.youtube.com/playlist?list=PLRQGNaa1hGF07sNyr5y9ntpTWONZhKQ8Z) — PKM Project 관련 모든 영상 모음

## 🎯 학습 목표

3일간 다음을 달성합니다:
1. **AI4PKM CLI 명령어 체계 이해 및 실행**
2. **Orchestrator 아키텍처 이해 및 설정**
3. **실전 자동화 워크플로우 구현 및 커스터마이징**

---

## 📅 Day 1: CLI 기초와 명령어 실습

### 🌅 오전 세션 (2-3시간): AI4PKM CLI 이해하기

#### 이론 (45분)
1. **AI4PKM CLI 전체 구조 파악**
   - `ai4pkm_cli/` 디렉터리 구조 탐색
   - 주요 모듈 역할 이해:
     - `main.py`: 진입점과 명령어 옵션
     - `cli.py`: PKMApp 핵심 로직
     - `agents/`: Claude, Gemini, Codex 에이전트
     - `commands/`: 명령어 실행 로직
     - `orchestrator/`: 멀티에이전트 오케스트레이션

2. **설정 파일 이해**
   - `ai4pkm_cli.json` 구조와 역할
   - 에이전트 설정 (기본 에이전트, fallback)
   - 크론 작업 설정
   - 타임아웃과 동시성 설정

**참고 자료**:
- `VL_AI4PKM_Automation/vl_ai4pkm_materials/00 - AI4PKM_프로젝트_설명.md`
- `ai4pkm_cli/main.py` (특히 1-150 라인)

#### 실습 1: CLI 설치 및 기본 명령어 (60분)

```bash
# 1. AI4PKM 설치 확인
cd /path/to/AI4PKM
python -m pip install -e .

# 2. 기본 명령어 실행
ai4pkm --help
ai4pkm --show-config
ai4pkm --list-agents

# 3. 설정 파일 검토
cat ai4pkm_cli.json
# 또는 IDE에서 열기
```

**실습 과제**:
- [ ] `ai4pkm --show-config` 실행하고 출력 내용 이해하기
- [ ] `ai4pkm --list-agents` 실행하고 사용 가능한 에이전트 확인
- [ ] `ai4pkm_cli.json` 파일 열어서 각 섹션 주석 달기

#### 실습 2: Prompt 직접 실행 (60분)

```bash
# 1. 사용 가능한 Prompt 목록 확인
ls ai4pkm_vault/_Settings_/Prompts/

# 2. 간단한 Prompt 실행 (예: EIC - Enrich Ingested Content)
ai4pkm -p "Enrich Ingested Content (EIC)"

# 3. 특정 에이전트 지정해서 실행
ai4pkm -p "Enrich Ingested Content (EIC)" -a gemini

# 4. 디버그 모드로 실행
ai4pkm -p "Enrich Ingested Content (EIC)" -d
```

**실습 과제**:
- [ ] `_Settings_/Prompts/` 폴더의 모든 프롬프트 파일 리스트업
- [ ] 각 프롬프트 파일의 Frontmatter 확인 (title, abbreviation, category)
- [ ] EIC 프롬프트를 다른 에이전트(Claude, Gemini)로 각각 실행해보고 결과 비교
- [ ] 실행 중 생성되는 로그 위치 확인 (`_Settings_/Logs/`)

### 🌆 오후 세션 (2-3시간): Command 실행과 에이전트 이해

#### 실습 3: Command 실행 (90분)

```bash
# 1. Command 목록 확인
# commands/command_runner.py 파일 열어서 사용 가능한 명령어 확인

# 2. 사진 처리 명령어 실행
ai4pkm -cmd process_photos

# 3. 노트 처리 명령어 실행
ai4pkm -cmd process_notes

# 4. 인자가 필요한 명령어 실행
ai4pkm -cmd sync-limitless -args '{"date": "2025-11-21"}'
```

**실습 과제**:
- [ ] `commands/command_runner.py` 파일 분석하여 사용 가능한 모든 명령어 리스트업
- [ ] 각 명령어가 어떤 모듈을 호출하는지 매핑 테이블 작성
- [ ] `process_photos`, `process_notes` 명령어 실행 후 결과물 확인
- [ ] 명령어 실행 흐름 다이어그램 그리기

#### 실습 4: 에이전트 이해와 전환 (90분)

**이론 (30분)**:
- Multi-Agent 아키텍처 이해
- 각 에이전트의 특징과 적합한 작업
  - `claude_code`: 코드 품질, 복잡한 추론
  - `gemini_cli`: 리서치, 긴 컨텍스트
  - `codex_cli`: 코드 생성

**실습**:
```bash
# 1. 각 에이전트로 동일한 작업 실행
ai4pkm -p "Enrich Ingested Content (EIC)" -a claude
ai4pkm -p "Enrich Ingested Content (EIC)" -a gemini

# 2. 에이전트별 로그 비교
ls -la ai4pkm_vault/_Settings_/Logs/

# 3. 에이전트 가용성 확인
ai4pkm --list-agents
```

**실습 과제**:
- [ ] 동일한 클리핑 파일에 대해 Claude와 Gemini 실행 결과 비교
- [ ] 각 에이전트의 실행 시간, 품질, 토큰 사용량 비교 (가능한 경우)
- [ ] 어떤 작업에 어떤 에이전트가 적합한지 가이드라인 작성

### 📝 Day 1 마무리 (30분)

**복습 체크리스트**:
- [ ] AI4PKM CLI의 주요 옵션 5가지 설명 가능
- [ ] Prompt와 Command의 차이점 이해
- [ ] 3가지 에이전트의 특징과 차이점 이해
- [ ] 로그와 설정 파일 위치 파악

**과제**:
- 오늘 배운 명령어들을 정리한 치트시트 작성
- 내일 사용할 테스트 클리핑 파일 3개 준비 (`Ingest/Clippings/`)

---

## 📅 Day 2: Orchestrator 아키텍처 마스터하기

### 🌅 오전 세션 (3-4시간): Orchestrator 개념과 구조

#### 이론 (90분)
1. **Orchestrator 아키텍처 이해**
   - Orchestrator의 탄생 배경 (On-demand Task Processing → Agentic Architecture)
   - 핵심 개념:
     - 이벤트 기반 자동화
     - 멀티에이전트 라우팅
     - 파일 시스템 감시 (watchdog)
     - 태스크 생성과 상태 관리

2. **Orchestrator 구성요소**
   - `orchestrator.yaml`: 단일 진실 공급원 (Single Source of Truth)
   - 핵심 모듈:
     - `core.py`: 이벤트 루프, 큐 관리
     - `agent_registry.py`: 에이전트 로딩/매칭
     - `execution_manager.py`: 동시성 제어
     - `task_manager.py`: 태스크 파일 관리
     - `file_monitor.py`: 파일 감시

**참고 자료**:
- `VL_AI4PKM_Automation/vl_ai4pkm_materials/01 - Orchestrator 상세 해설.md`
- `VL_AI4PKM_Automation/vl_ai4pkm_materials/02 - Orchestrator 구현 스펙.md`
- `VL_AI4PKM_Automation/vl_ai4pkm_materials/03 - Agentic AI 아키텍처 해설.md`

#### 실습 5: orchestrator.yaml 파헤치기 (90분)

```bash
# 1. orchestrator.yaml 위치 확인
cat ai4pkm_vault/orchestrator.yaml

# 2. 구조 분석
# - orchestrator 블록
# - defaults 블록
# - nodes 블록
```

**실습 과제**:
- [ ] `orchestrator.yaml` 파일 각 섹션에 주석 추가
- [ ] 현재 설정된 모든 노드(agent) 리스트업
- [ ] 각 노드의 input_path, output_path, output_type 정리
- [ ] 다음 표 완성:

| Agent Name | Abbreviation | Input Path | Output Path | Output Type | Executor |
|------------|--------------|------------|-------------|-------------|----------|
| Enrich Ingested Content | EIC | Ingest/Clippings | AI/Articles | new_file | claude_code |
| ... | ... | ... | ... | ... | ... |

### 🌆 오후 세션 (2-3시간): Orchestrator 실행과 모니터링

#### 실습 6: Orchestrator 실행 (90분)

```bash
# 1. Orchestrator 상태 확인
ai4pkm --orchestrator-status

# 2. Orchestrator 실행 (기본 설정)
ai4pkm -o

# 3. 동시성 설정 변경하여 실행
ai4pkm -o --max-concurrent 5

# 4. 새 터미널에서 파일 변경 테스트
# (Orchestrator 실행 중)
# 새 클리핑 파일을 Ingest/Clippings/ 에 추가
```

**실습 과제**:
- [ ] Orchestrator 실행 후 콘솔 로그 패턴 분석
- [ ] 테스트 클리핑 파일 추가 시 자동 처리 확인
- [ ] `_Settings_/Tasks/` 폴더에 생성되는 태스크 파일 구조 분석
- [ ] 실시간으로 로그 파일 tail 해보기: `tail -f _Settings_/Logs/*.log`

#### 실습 7: 태스크 상태 관리 이해 (90분)

**태스크 라이프사이클 이해**:
```
파일 이벤트 발생
  ↓
QUEUED (용량 부족 시)
  ↓
IN_PROGRESS (실행 중)
  ↓
PROCESSED (완료) / FAILED (실패) / TIMEOUT (시간 초과)
```

**실습**:
```bash
# 1. 태스크 디렉터리 모니터링
watch -n 1 'ls -la ai4pkm_vault/_Settings_/Tasks/'

# 2. 태스크 파일 상세 분석
cat ai4pkm_vault/_Settings_/Tasks/2025-11-21-EIC-*.md

# 3. 다양한 상태의 태스크 파일 비교
# - QUEUED 상태 파일
# - IN_PROGRESS 상태 파일
# - PROCESSED 상태 파일
```

**실습 과제**:
- [ ] 태스크 파일의 Frontmatter 필드 전체 리스트업
- [ ] 각 상태(QUEUED, IN_PROGRESS, PROCESSED, FAILED)로 전이되는 조건 정리
- [ ] `generation_log`, `execution_log` 내용 분석
- [ ] 태스크 실패 시나리오 만들어보고 로그 확인

### 📝 Day 2 마무리 (30분)

**복습 체크리스트**:
- [ ] Orchestrator의 핵심 역할 3가지 설명 가능
- [ ] `orchestrator.yaml`의 3대 블록 이해
- [ ] 태스크 라이프사이클 5단계 암기
- [ ] 파일 이벤트 → 자동 처리 흐름 설명 가능

**과제**:
- Orchestrator 아키텍처 다이어그램 그리기
- 내일 만들 커스텀 에이전트 아이디어 구상

---

## 📅 Day 3: 실전 자동화 구현과 커스터마이징

### 🌅 오전 세션 (3-4시간): 커스텀 에이전트 생성

#### 실습 8: 새로운 프롬프트 작성 (90분)

**목표**: "학습 노트 요약(SNS - Summarize Note for Study)" 에이전트 만들기

**단계**:

1. **프롬프트 파일 생성**
```bash
# 1. 프롬프트 파일 생성
touch ai4pkm_vault/_Settings_/Prompts/"Summarize Note for Study (SNS).md"
```

2. **프롬프트 내용 작성**
```markdown
---
title: Summarize Note for Study (SNS)
abbreviation: SNS
category: learning
description: 학습 노트를 간결하게 요약하여 복습용 자료 생성
version: 1.0
---

# Summarize Note for Study (SNS)

## 목적
긴 학습 노트를 핵심 개념 중심으로 요약하여 빠른 복습이 가능하도록 합니다.

## 입력
- 학습 노트 마크다운 파일

## 출력 요구사항
1. **핵심 개념 (Key Concepts)**: 3-5개 bullet points
2. **상세 요약 (Summary)**: 2-3 문단
3. **실습 포인트 (Practice Points)**: 실제로 해볼 수 있는 것들
4. **연관 주제 (Related Topics)**: 링크로 연결

## 처리 절차
1. 노트 전체를 읽고 주요 주제 파악
2. 핵심 개념 추출 (중복 제거)
3. 전체 흐름을 유지하면서 요약
4. 실습 가능한 항목 정리
5. 관련 토픽 추천
```

3. **orchestrator.yaml에 노드 추가**
```yaml
nodes:
  # ... 기존 노드들 ...

  # Summarize Note for Study
  - type: agent
    name: Summarize Note for Study (SNS)
    input_path: Topics/Learning
    output_path: AI/Study
    output_type: new_file
    executor: gemini_cli  # 긴 컨텍스트에 적합
    timeout_minutes: 15
    max_parallel: 2
```

**실습 과제**:
- [ ] 위 프롬프트 파일 생성 및 커스터마이징
- [ ] `orchestrator.yaml`에 노드 추가
- [ ] Orchestrator 재시작 후 상태 확인: `ai4pkm --orchestrator-status`
- [ ] 테스트 학습 노트 만들어서 자동 처리 확인

#### 실습 9: 트리거 조건 커스터마이징 (90분)

**고급 트리거 설정 배우기**:

```yaml
nodes:
  - type: agent
    name: AI Research Notes (ARN)
    input_path: Topics/
    output_path: AI/Research
    # 특정 패턴 제외 (이미 처리된 파일)
    trigger_exclude_pattern: "*-processed*"
    # 파일 내용에 특정 마커가 있을 때만 실행
    trigger_content_pattern: "%% #ai-research %%"
    # 트리거 마커 처리 후 제거
    post_process_action: remove_trigger_content
    # 우선순위 높음
    task_priority: high
    # 동시 실행 1개로 제한 (리소스 절약)
    max_parallel: 1
```

**실습 과제**:
- [ ] `trigger_exclude_pattern` 사용하여 특정 파일 제외하기
- [ ] `trigger_content_pattern`로 마커 기반 트리거 설정
- [ ] `post_process_action: remove_trigger_content` 동작 확인
- [ ] 우선순위 다른 태스크들의 처리 순서 관찰

### 🌆 오후 세션 (2-3시간): 실전 워크플로우 구현

#### 실습 10: 완전한 자동화 파이프라인 구축 (120분)

**시나리오**: "웹 클리핑 → 정제 → 주제 태그 → SNS 포스트 생성" 자동화

**단계별 구현**:

1. **파이프라인 설계**
```
Ingest/Clippings (원본)
  ↓ [EIC]
AI/Articles (정제본)
  ↓ [Topic Tagger - TT (새로 만들기)]
AI/Articles (태그 추가)
  ↓ [CTP]
AI/Sharable (SNS 포스팅용)
```

2. **중간 에이전트 추가: Topic Tagger (TT)**

프롬프트 파일 생성:
```markdown
---
title: Topic Tagger (TT)
abbreviation: TT
category: enhancement
---

# Topic Tagger

## 목적
정제된 아티클에 적절한 토픽 태그를 자동으로 추가합니다.

## 입력
- AI/Articles의 정제된 마크다운 파일

## 출력
- 동일 파일에 토픽 태그 추가 (update_file 모드)

## 처리 절차
1. 아티클 내용 분석
2. 관련 토픽 3-5개 추천
3. Frontmatter에 topics 필드 추가
4. 본문에 토픽 링크 추가
```

orchestrator.yaml:
```yaml
nodes:
  # ... EIC ...

  # Topic Tagger
  - type: agent
    name: Topic Tagger (TT)
    input_path: AI/Articles
    output_path: AI/Articles
    output_type: update_file  # 원본 파일 수정
    trigger_content_pattern: "%% #needs-tagging %%"
    post_process_action: remove_trigger_content

  # ... CTP ...
```

3. **파이프라인 테스트**
```bash
# 1. Orchestrator 실행
ai4pkm -o

# 2. 새 클리핑 추가
# (자동으로 EIC → TT → CTP 순차 실행 관찰)

# 3. 각 단계별 결과물 확인
ls -la Ingest/Clippings/
ls -la AI/Articles/
ls -la AI/Sharable/
```

**실습 과제**:
- [ ] 3단계 파이프라인 구축 및 테스트
- [ ] 각 단계의 태스크 파일 생성 확인
- [ ] 연쇄 트리거 동작 확인 (EIC 완료 → TT 자동 시작)
- [ ] 전체 파이프라인 처리 시간 측정

#### 실습 11: 크론 작업과 배치 처리 (60분)

**이론 (20분)**:
- 크론 작업의 필요성 (Daily/Weekly Roundup)
- `ai4pkm_cli.json`의 `cron_jobs` 설정
- 배치 vs 이벤트 기반 처리

**실습**:
```bash
# 1. 크론 설정 확인
cat ai4pkm_cli.json | jq '.cron_jobs'

# 2. 크론 작업 수동 실행 (테스트)
ai4pkm -r
# 인터랙티브 메뉴에서 작업 선택

# 3. 크론 데몬 실행
ai4pkm -c
# (백그라운드에서 스케줄된 작업 실행)
```

**실습 과제**:
- [ ] 간단한 크론 작업 추가 (예: 매일 오전 1시 데일리 라운드업)
- [ ] `-r` 옵션으로 크론 작업 수동 실행 테스트
- [ ] 크론 실행 로그 확인

### 📝 Day 3 마무리 및 종합 복습 (60분)

#### 최종 프로젝트: 나만의 자동화 워크플로우

**요구사항**:
1. 최소 2단계 이상의 파이프라인
2. 커스텀 프롬프트 1개 이상 포함
3. 트리거 조건 커스터마이징
4. 실제로 동작하는 데모 가능

**예시 아이디어**:
- 학습 자료 → 요약 → 플래시카드 생성
- 회의록 → 액션 아이템 추출 → 태스크 생성
- 아이디어 노트 → 구조화 → 블로그 초안

**발표 준비**:
- [ ] 워크플로우 다이어그램
- [ ] `orchestrator.yaml` 설정
- [ ] 프롬프트 파일
- [ ] 실행 데모 영상 또는 스크린샷

#### 종합 복습 체크리스트

**Day 1 복습**:
- [ ] AI4PKM CLI 명령어 10개 이상 암기
- [ ] Prompt와 Command의 차이 설명
- [ ] 3개 에이전트 특징 비교

**Day 2 복습**:
- [ ] Orchestrator 6대 모듈 역할 설명
- [ ] `orchestrator.yaml` 구조 설명
- [ ] 태스크 상태 전이 다이어그램 그리기

**Day 3 복습**:
- [ ] 커스텀 프롬프트 작성 가능
- [ ] 멀티 스테이지 파이프라인 설계 가능
- [ ] 트리거 조건 커스터마이징 이해

---

## 📚 추가 학습 자료

### 심화 학습 주제

1. **Agentic AI 아키텍처 깊이 이해**
   - 참고: `03 - Agentic AI 아키텍처 해설.md`
   - 프롬프트 중심 에이전트 정의
   - 맥 앱 통합 (향후)

2. **On-demand Task Processing 원리**
   - 참고: `04 - 온디맨드 지식 태스크 아키텍처 해설.md`
   - KTG/KTP/KTE 3단계 이해
   - Multi-Agent Evaluation

3. **고급 트리거 패턴**
   - 정규식 기반 내용 매칭
   - Multi-input 에이전트
   - Cron + 이벤트 하이브리드

4. **성능 최적화**
   - 동시성 튜닝 (`max_concurrent`, `max_parallel`)
   - 타임아웃 설정
   - QUEUED 태스크 관리

### 참고 문서

- [Orchestrator 상세 가이드](../vl_ai4pkm_materials/01%20-%20Orchestrator%20상세%20해설.md)
- [구현 스펙](../vl_ai4pkm_materials/02%20-%20Orchestrator%20구현%20스펙.md)
- [아키텍처 해설](../vl_ai4pkm_materials/03%20-%20Agentic%20AI%20아키텍처%20해설.md)
- [온디맨드 태스크](../vl_ai4pkm_materials/04%20-%20온디맨드%20지식%20태스크%20아키텍처%20해설.md)

### 실습 팁

1. **작게 시작하기**: 복잡한 파이프라인보다 단순한 에이전트 하나부터
2. **로그 활용**: 문제 발생 시 `_Settings_/Logs/` 확인 습관화
3. **점진적 확장**: 동작 확인 후 하나씩 추가
4. **문서화**: 자신만의 설정과 워크플로우 문서 작성

---

## 🎓 학습 완료 후 체크리스트

### 기본 역량
- [ ] AI4PKM CLI 명령어를 자유롭게 사용 가능
- [ ] Orchestrator 실행 및 모니터링 가능
- [ ] 기본 에이전트들의 역할 이해
- [ ] 태스크 파일 구조 이해 및 디버깅 가능

### 중급 역량
- [ ] `orchestrator.yaml` 수정 및 재설정 가능
- [ ] 커스텀 프롬프트 작성 가능
- [ ] 2-3단계 자동화 파이프라인 구축 가능
- [ ] 트리거 조건 커스터마이징 가능

### 고급 역량
- [ ] 다중 에이전트 라우팅 전략 수립 가능
- [ ] 성능 최적화 (동시성, 타임아웃) 가능
- [ ] 크론 작업과 이벤트 기반 처리 통합
- [ ] 실전 프로젝트에 AI4PKM 적용 가능

---

## 💡 문제 해결 가이드

### 자주 발생하는 문제

1. **Orchestrator가 시작되지 않음**
   - `ai4pkm --orchestrator-status` 실행
   - `orchestrator.yaml` 문법 오류 확인
   - 필수 디렉터리 존재 확인

2. **에이전트가 트리거되지 않음**
   - `input_path` 경로 확인
   - `trigger_exclude_pattern` 확인
   - 파일 확장자 확인 (.md인지)
   - 로그 확인: `tail -f _Settings_/Logs/*.log`

3. **태스크가 QUEUED 상태에 멈춤**
   - `max_concurrent` 값 증가
   - 진행 중인 태스크 타임아웃 확인
   - 수동으로 QUEUED 태스크 제거 후 재시도

4. **에이전트 실행 실패**
   - 로그 파일에서 상세 에러 확인
   - 프롬프트 파일 Frontmatter 확인
   - 에이전트 CLI 설치 확인 (`--list-agents`)

---

## 🎯 다음 단계

3일 학습 완료 후:

1. **실전 적용**
   - 자신의 PKM 워크플로우에 AI4PKM 통합
   - 일일 루틴 자동화
   - 주간 리뷰 자동화

2. **커뮤니티 참여**
   - 커스텀 프롬프트 공유
   - 사용 사례 공유
   - 피드백 제공

3. **고급 기능 탐구**
   - Skills 시스템 (향후 기능)
   - MCP 통합 (향후 기능)
   - 맥 앱 활용 (향후 기능)

---

**Good Luck with Your AI4PKM Journey! 🚀**

*이 로드맵은 3일간의 집중 학습을 위해 설계되었습니다. 각자의 페이스에 맞춰 조절하세요.*
