# 커스텀 에이전트 생성 가이드

AI4PKM Orchestrator에서 자신만의 에이전트를 만들고 설정하는 완전한 가이드입니다.

---

## 목차

1. [에이전트 생성 개요](#에이전트-생성-개요)
2. [프롬프트 파일 작성](#프롬프트-파일-작성)
3. [Orchestrator 설정](#orchestrator-설정)
4. [고급 트리거 조건](#고급-트리거-조건)
5. [테스트 및 디버깅](#테스트-및-디버깅)
6. [Best Practices](#best-practices)
7. [실전 예제](#실전-예제)

---

## 에이전트 생성 개요

### 에이전트란?

에이전트는 특정 작업을 자동으로 수행하는 AI 기반 워커입니다. 파일 변경, 스케줄, 외부 이벤트 등에 반응하여 자동 실행됩니다.

### 에이전트 구성 요소

```
에이전트 = 프롬프트 파일 + Orchestrator 설정

1. 프롬프트 파일 (_Settings_/Prompts/*.md)
   - 에이전트가 무엇을 할지 정의
   - AI에게 전달되는 지시사항

2. Orchestrator 설정 (orchestrator.yaml)
   - 언제, 어떻게 실행할지 정의
   - 입력/출력 경로, 트리거 조건 등
```

### 에이전트 생성 절차

```
1. 아이디어 구상
   ↓
2. 프롬프트 파일 작성 (_Settings_/Prompts/)
   ↓
3. orchestrator.yaml에 노드 추가
   ↓
4. 출력 폴더 생성
   ↓
5. Orchestrator 상태 확인 (--orchestrator-status)
   ↓
6. 테스트 실행
   ↓
7. 프로덕션 배포 (enabled: true)
```

---

## 프롬프트 파일 작성

### 파일 위치

```
VL_AI4PKM_Automation/
└── _Settings_/
    └── Prompts/
        └── Your Agent Name (YAN).md
```

### 기본 구조

```markdown
---
title: Your Agent Name
abbreviation: YAN
category: learning|publishing|automation|analysis
description: 간단한 설명 (1문장)
version: 1.0
---

# Your Agent Name

에이전트의 목적을 1-2문장으로 설명합니다.

## Input
- Source: input/path/*.md
- 입력 파일 형식 및 요구사항

## Output
- File: output/path/{{filename}}_result.md
- 출력 파일 형식 및 내용

## Main Process
\```
1. 단계 1
   - 세부 작업 1-1
   - 세부 작업 1-2

2. 단계 2
   - 세부 작업 2-1
   - 세부 작업 2-2

3. 단계 3
   - 세부 작업 3-1
\```

## Output Format
\```markdown
# 출력 형식 예시

## 섹션 1
내용...

## 섹션 2
내용...
\```

## Important Notes
1. 주의사항 1
2. 주의사항 2
```

### Front Matter 필드

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `title` | ✅ | 에이전트 전체 이름 | "Summarize Note for Study" |
| `abbreviation` | ✅ | 짧은 약어 (2-4자) | "SNS" |
| `category` | ✅ | 카테고리 | learning, publishing, automation |
| `description` | ⬜ | 짧은 설명 | "학습 노트를 요약하여 복습용 자료 생성" |
| `version` | ⬜ | 버전 번호 | "1.0", "2.1" |

### 프롬프트 작성 Tips

#### 1. 명확한 목적 정의

**좋은 예**:
```markdown
# Email Summary Generator

긴 이메일 스레드를 읽고 핵심 내용만 3-5 bullet points로 요약합니다.
```

**나쁜 예**:
```markdown
# Email Processor

이메일을 처리합니다.
```

#### 2. 구체적인 입출력 명시

**좋은 예**:
```markdown
## Input
- Source: inbox/*.eml
- 이메일 파일 (.eml 형식)
- 최소 100자 이상의 본문 필요

## Output
- File: summaries/{{date}}_email_summary.md
- Markdown 형식
- 핵심 내용 bullet points + 액션 아이템
```

**나쁜 예**:
```markdown
## Input
- 이메일

## Output
- 요약 파일
```

#### 3. 단계별 프로세스

**좋은 예**:
```markdown
## Main Process
\```
1. 이메일 파싱
   - 제목, 발신자, 날짜 추출
   - 본문 텍스트 정리 (HTML 제거)
   - 첨부파일 목록 확인

2. 내용 분석
   - 주요 주제 파악
   - 핵심 포인트 3-5개 식별
   - 액션 아이템 찾기

3. 요약 생성
   - Markdown 형식으로 구조화
   - 우선순위 높은 내용 강조
   - 관련 링크 추가
\```
```

#### 4. 출력 형식 예시

실제 출력을 보여주는 템플릿 제공:

```markdown
## Output Format
\```markdown
# Email Summary: {{subject}}

**From**: {{sender}}
**Date**: {{date}}
**Priority**: 🔴 High / 🟡 Medium / 🟢 Low

## Key Points
- 핵심 포인트 1
- 핵심 포인트 2
- 핵심 포인트 3

## Action Items
- [ ] 액션 1 (담당자: {{name}}, 기한: {{date}})
- [ ] 액션 2

## Context
[2-3문장으로 전체 맥락 설명]

## Related
- [[관련 이메일 1]]
- [[관련 프로젝트 1]]
\```
```

---

## Orchestrator 설정

### orchestrator.yaml 위치

```
VL_AI4PKM_Automation/
└── orchestrator.yaml
```

### 기본 노드 구조

```yaml
nodes:
  - type: agent
    name: Your Agent Name (YAN)
    abbreviation: yan
    executor: claude_code
    input_path: input/folder
    output_path: output/folder
    enabled: true
```

### 필수 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| `type` | 노드 타입 | `agent` (고정) |
| `name` | 에이전트 이름 (프롬프트 title과 동일) | "Summarize Note for Study (SNS)" |
| `abbreviation` | 약어 (프롬프트 abbreviation과 동일) | "sns" |
| `executor` | 사용할 AI 실행기 | `claude_code`, `gemini` |
| `input_path` | 입력 파일 경로 | `vl_ai4pkm_materials` |
| `output_path` | 출력 파일 경로 | `AI/Study` |

### 선택 필드

| 필드 | 기본값 | 설명 |
|------|-------|------|
| `enabled` | `true` | 에이전트 활성화 여부 |
| `output_type` | `update_file` | `new_file` 또는 `update_file` |
| `timeout_minutes` | `30` | 실행 타임아웃 (분) |
| `max_parallel` | `3` | 최대 동시 실행 수 |
| `task_priority` | `medium` | `low`, `medium`, `high` |
| `task_create` | `true` | Task 파일 생성 여부 |

### 입력 경로 설정

#### 단일 경로

```yaml
input_path: vl_ai4pkm_materials
```

#### 여러 경로 (리스트)

```yaml
input_path:
  - vl_ai4pkm_materials
  - 01-AI4PKM_CLI_Structure
  - 02-Basic_Commands
  - 03-Orchestrator_Deep_Dive
```

#### 하위 폴더 포함

```yaml
input_path: Projects/**  # Projects의 모든 하위 폴더 포함
```

### 출력 타입

#### new_file (새 파일 생성)

```yaml
output_type: new_file
output_path: AI/Study

# 결과:
# AI/Study/original_filename_enriched.md (새 파일)
```

#### update_file (원본 업데이트)

```yaml
output_type: update_file
output_path: vl_ai4pkm_materials

# 결과:
# vl_ai4pkm_materials/original_filename.md (기존 파일 업데이트)
```

### 완전한 노드 예시

```yaml
nodes:
  - type: agent
    name: Summarize Note for Study (SNS)
    abbreviation: sns
    executor: claude_code
    input_path:
      - vl_ai4pkm_materials
      - 01-AI4PKM_CLI_Structure
      - 02-Basic_Commands
      - 03-Orchestrator_Deep_Dive
    output_path: AI/Study
    output_type: new_file
    timeout_minutes: 15
    max_parallel: 2
    task_priority: medium
    enabled: true
```

---

## 고급 트리거 조건

기본적으로 에이전트는 `input_path`의 모든 파일 변경에 반응합니다. 고급 트리거 조건을 사용하면 더 세밀한 제어가 가능합니다.

### 1. 파일 패턴 필터

#### 특정 확장자만

```yaml
nodes:
  - type: agent
    name: Markdown Processor
    input_path: Documents
    input_pattern: "*.md"  # .md 파일만 처리
```

#### 복수 패턴

```yaml
input_pattern: "*.{md,txt,pdf}"  # .md, .txt, .pdf 파일
```

#### 제외 패턴

```yaml
nodes:
  - type: agent
    name: Content Enricher
    input_path: Articles
    input_pattern: "*.md"
    exclude_pattern: "*_enriched.md"  # 이미 처리된 파일 제외
```

### 2. 내용 기반 트리거

파일 내용에 특정 마커가 있을 때만 실행:

```yaml
nodes:
  - type: agent
    name: AI Research Processor
    input_path: Research
    trigger_content_pattern: "%% #ai-research %%"  # 이 마커가 있을 때만 실행
```

**사용 예시**:

```markdown
# My Research Note

%% #ai-research %%

여기에 AI 연구 내용 작성...
```

### 3. 후처리 액션

#### 트리거 마커 제거

처리 후 트리거 마커를 자동으로 제거:

```yaml
nodes:
  - type: agent
    name: One-time Processor
    trigger_content_pattern: "%% #process %%"
    post_process_action: remove_trigger_content  # 처리 후 마커 제거
```

**동작**:
1. 파일에 `%% #process %%` 추가
2. 에이전트 실행
3. 처리 완료 후 마커 자동 제거
4. 다시 트리거되지 않음

#### 파일 이동

```yaml
post_process_action: move_to_archive  # 처리 후 아카이브로 이동
archive_path: _Archive_/Processed
```

### 4. 파일 나이 조건

#### 최근 파일만

```yaml
nodes:
  - type: agent
    name: Recent Content Analyzer
    trigger_max_age_hours: 24  # 24시간 이내 생성/수정된 파일만
```

#### 오래된 파일만

```yaml
trigger_min_age_hours: 168  # 7일 이상 된 파일만 (7*24=168)
```

### 5. 파일 크기 조건

```yaml
nodes:
  - type: agent
    name: Large File Processor
    trigger_min_size_kb: 100  # 100KB 이상 파일만
    trigger_max_size_kb: 10000  # 10MB 이하 파일만
```

### 6. 우선순위 설정

```yaml
nodes:
  - type: agent
    name: Urgent Task Processor
    task_priority: high  # 다른 에이전트보다 먼저 실행
```

우선순위 레벨:
- `high`: 우선 처리
- `medium`: 일반 (기본값)
- `low`: 나중에 처리

### 7. 동시 실행 제어

#### 리소스 절약

```yaml
nodes:
  - type: agent
    name: Heavy Task Agent
    max_parallel: 1  # 한 번에 하나만 실행 (리소스 많이 사용하는 작업)
```

#### 병렬 처리

```yaml
max_parallel: 5  # 최대 5개까지 동시 실행 (가벼운 작업)
```

### 8. 스케줄 기반 트리거

Cron 표현식 사용:

```yaml
nodes:
  - type: agent
    name: Daily Report Generator
    cron: "0 9 * * *"  # 매일 오전 9시
    input_path: DailyLogs
```

**Cron 표현식 예시**:

| 패턴 | 의미 |
|------|------|
| `0 9 * * *` | 매일 오전 9시 |
| `0 */2 * * *` | 2시간마다 |
| `0 9 * * 1` | 매주 월요일 오전 9시 |
| `0 0 1 * *` | 매월 1일 자정 |
| `0 9 1,15 * *` | 매월 1일, 15일 오전 9시 |

### 고급 트리거 조합 예시

```yaml
nodes:
  - type: agent
    name: AI Research Analyzer
    abbreviation: ara
    executor: claude_code
    input_path: Research

    # 파일 필터
    input_pattern: "*.md"
    exclude_pattern: "*_analyzed.md"

    # 내용 기반 트리거
    trigger_content_pattern: "%% #ai-research %%"

    # 조건
    trigger_min_size_kb: 50  # 50KB 이상
    trigger_max_age_hours: 72  # 3일 이내

    # 후처리
    post_process_action: remove_trigger_content

    # 성능
    max_parallel: 1  # 한 번에 하나씩 (집중 분석)
    task_priority: high  # 우선 처리
    timeout_minutes: 30  # 긴 타임아웃

    output_path: Research/Analyzed
    output_type: new_file
    enabled: true
```

---

## 테스트 및 디버깅

### 1. Orchestrator 상태 확인

```bash
cd VL_AI4PKM_Automation
source ../venv/Scripts/activate
ai4pkm --orchestrator-status
```

**출력 예시**:
```
+------------------------ Orchestrator Status ------------------------+
| Vault: /path/to/VL_AI4PKM_Automation                              |
| Agents loaded: 3                                                   |
| Pollers loaded: 0                                                  |
| Max concurrent: 3                                                  |
+--------------------------------------------------------------------+

Available Agents:
  ✓ [EIC] Enrich Ingested Content (EIC)
    Category: learning
  ✓ [CTP] Create Thread Postings (CTP)
    Category: publishing
  ✓ [SNS] Summarize Note for Study (SNS)
    Category: learning
```

### 2. 에이전트 목록 확인

```bash
ai4pkm --list-agents
```

### 3. 설정 검증

```bash
ai4pkm --show-config
```

### 4. 수동 트리거 테스트

```bash
# 대화형 모드
cd VL_AI4PKM_Automation
ai4pkm -t sns

# 테스트 파일을 input_path에 배치하고 자동 감지 대기
```

### 5. 로그 확인

```bash
# Orchestrator 로그
tail -f _Settings_/Logs/orchestrator.log

# 특정 실행 로그
ls _Settings_/Logs/
cat _Settings_/Logs/2025-12-24-153805-SNS.log
```

### 6. Task 파일 확인

```bash
# 최근 Task 파일
ls -lt _Settings_/Tasks/*.md | head -5

# 실패한 Task 찾기
grep -l "status: \"FAILED\"" _Settings_/Tasks/*.md
```

### 7. 일반적인 문제 해결

#### 에이전트가 로드되지 않음

**증상**:
```
Available Agents: 0
```

**해결**:
1. 프롬프트 파일 위치 확인:
   ```bash
   ls _Settings_/Prompts/*.md
   ```

2. Front Matter 확인:
   ```markdown
   ---
   title: Agent Name
   abbreviation: AN
   ---
   ```

3. orchestrator.yaml의 `name` 필드가 프롬프트 `title`과 정확히 일치하는지 확인

#### 에이전트가 실행되지 않음

**증상**:
- 파일을 input_path에 넣어도 반응 없음

**해결**:
1. `enabled: true` 확인
2. input_path 경로 확인:
   ```bash
   ls vl_ai4pkm_materials/
   ```
3. exclude_pattern 확인
4. 로그 확인:
   ```bash
   tail _Settings_/Logs/orchestrator.log
   ```

#### Executor 오류

**증상**:
```
status: "FAILED"
Error: Executor not found
```

**해결**:
1. Executor 설치 확인:
   ```bash
   where claude  # Windows
   which claude  # Linux/Mac
   ```

2. orchestrator.yaml의 executor 경로 확인:
   ```yaml
   executors:
     claude_code:
       command: /path/to/claude
   ```

3. API 키 환경 변수 확인:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

#### 파일 인코딩 오류 (Windows)

**증상**:
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**해결**:
```bash
export PYTHONIOENCODING=utf-8
ai4pkm -t sns 2>&1 | cat
```

---

## Best Practices

### 1. 에이전트 설계 원칙

#### 단일 책임 원칙 (Single Responsibility)

**좋은 예**:
```
- SNS: 학습 노트 요약 (한 가지 작업)
- EIC: 웹 클리핑 정리 (한 가지 작업)
```

**나쁜 예**:
```
- MegaAgent: 클리핑 정리 + 요약 + 발행 + 태그 추가 (너무 많은 작업)
```

#### 명확한 입출력 분리

```yaml
# 좋은 예
input_path: vl_ai4pkm_clippings    # 원본
output_path: vl_ai4pkm_materials   # 정리된 자료

# 나쁜 예
input_path: Documents
output_path: Documents  # 같은 폴더 (혼란 가능성)
```

#### 재사용 가능한 프롬프트

프롬프트를 일반화하여 다양한 상황에 적용:

```markdown
# 좋은 예
## Input
- 학습 노트 마크다운 파일 (강의 노트, 튜토리얼, 기술 문서 등)

# 나쁜 예
## Input
- "Orchestrator 학습 노트"만 처리
```

### 2. 성능 최적화

#### max_concurrent 조정

```yaml
# CPU/메모리 많이 사용하는 작업
max_parallel: 1

# 가벼운 작업
max_parallel: 5
```

#### timeout 설정

```yaml
# 짧은 작업 (요약, 태그 추가)
timeout_minutes: 5

# 긴 작업 (분석, 번역)
timeout_minutes: 30
```

#### 파일 필터링

불필요한 파일 제외:

```yaml
input_pattern: "*.md"
exclude_pattern: "*_processed.md|*_archived.md"
```

### 3. 유지보수성

#### 버전 관리

프롬프트 파일에 버전 명시:

```markdown
---
title: Content Enricher
version: 2.1
changelog:
  - 2.1: 태그 자동 추가 기능
  - 2.0: 출력 형식 개선
  - 1.0: 초기 버전
---
```

#### 문서화

```yaml
nodes:
  - type: agent
    name: SNS
    # Purpose: 학습 노트를 요약하여 복습용 자료 생성
    # Updated: 2025-12-24
    # Author: ChangSoo
```

#### 점진적 배포

새 에이전트는 처음에 비활성화:

```yaml
nodes:
  - type: agent
    name: New Experimental Agent
    enabled: false  # 먼저 테스트
```

테스트 후:

```yaml
enabled: true  # 프로덕션 배포
```

### 4. 에러 처리

#### 로깅 활용

```bash
# 정기적으로 로그 확인
tail -f _Settings_/Logs/orchestrator.log

# 에러 검색
grep "ERROR" _Settings_/Logs/orchestrator.log
```

#### Task 모니터링

```bash
# 실패한 Task 찾기
find _Settings_/Tasks -name "*.md" -exec grep -l "FAILED" {} \;

# 주간 리포트
grep "status:" _Settings_/Tasks/*.md | sort | uniq -c
```

### 5. 보안

#### API 키 관리

환경 변수 사용 (하드코딩 금지):

```bash
# .bashrc 또는 .zshrc
export ANTHROPIC_API_KEY="your-api-key"
export GOOGLE_API_KEY="your-api-key"
```

orchestrator.yaml에 키 넣지 말 것:

```yaml
# ❌ 나쁜 예
executors:
  claude_code:
    api_key: "sk-ant-xxx..."  # 절대 금지!

# ✅ 좋은 예
executors:
  claude_code:
    command: claude  # 환경 변수에서 자동으로 읽음
```

#### 민감 정보 필터

```yaml
nodes:
  - type: agent
    name: Email Processor
    # 민감 정보 (비밀번호, 카드번호 등) 필터링 로직 필요
    exclude_pattern: "*_private.md"
```

---

## 실전 예제

### 예제 1: 블로그 포스트 생성기

**목적**: 학습 노트를 블로그 포스트 형식으로 변환

#### 프롬프트 파일

`_Settings_/Prompts/Blog Post Generator (BPG).md`:

```markdown
---
title: Blog Post Generator (BPG)
abbreviation: BPG
category: publishing
description: 학습 노트를 블로그 포스트 형식으로 변환
version: 1.0
---

# Blog Post Generator

학습 노트를 독자 친화적인 블로그 포스트로 변환합니다.

## Input
- Source: vl_ai4pkm_materials/*.md
- 정리된 학습 자료

## Output
- File: Publish/Blog/{{filename}}.md
- 블로그 포스트 형식 (제목, 소개, 본문, 결론)

## Main Process
\```
1. 노트 분석
   - 주요 주제 파악
   - 독자 대상 결정 (초급/중급/고급)

2. 구조 변환
   - 눈길을 끄는 제목 생성
   - 흥미로운 서론 작성
   - 본문을 논리적 섹션으로 구성
   - 행동 유도 결론

3. 스타일 조정
   - 전문 용어 설명 추가
   - 실생활 예시 포함
   - 시각적 요소 제안 (이미지, 다이어그램 위치)

4. SEO 최적화
   - 키워드 추천
   - 메타 설명 생성
   - 태그 제안
\```

## Output Format
\```markdown
---
title: "눈길을 끄는 블로그 제목"
date: {{date}}
tags: [tag1, tag2, tag3]
description: "SEO 최적화 메타 설명 (150-160자)"
---

# 눈길을 끄는 블로그 제목

**TL;DR**: [2-3문장 요약]

## 서론

[독자의 관심을 끄는 질문이나 시나리오]

## 본문

### 주요 개념 1
[설명 + 예시]

### 주요 개념 2
[설명 + 예시]

### 실전 활용
[실제 사용 예시]

## 결론

[핵심 요약 + 행동 유도]

## 추가 자료
- [관련 링크 1]
- [관련 링크 2]

---
**Keywords**: keyword1, keyword2, keyword3
\```
```

#### orchestrator.yaml 설정

```yaml
nodes:
  - type: agent
    name: Blog Post Generator (BPG)
    abbreviation: bpg
    executor: claude_code
    input_path: vl_ai4pkm_materials
    input_pattern: "*_enriched.md"  # EIC 처리된 파일만
    output_path: Publish/Blog
    output_type: new_file
    timeout_minutes: 20
    max_parallel: 2
    task_priority: medium
    enabled: true
```

### 예제 2: 주간 학습 리뷰

**목적**: 일주일 동안의 학습 노트를 요약한 주간 리뷰 생성

#### 프롬프트 파일

`_Settings_/Prompts/Weekly Learning Review (WLR).md`:

```markdown
---
title: Weekly Learning Review (WLR)
abbreviation: WLR
category: analysis
description: 주간 학습 활동을 요약하고 다음 주 계획 제안
version: 1.0
---

# Weekly Learning Review

지난 주의 모든 학습 노트를 분석하여 종합 리뷰를 생성합니다.

## Input
- Source: vl_ai4pkm_materials/*.md (지난 7일)
- 모든 학습 관련 마크다운 파일

## Output
- File: Reviews/Weekly_{{year}}_W{{week_number}}.md
- 주간 학습 종합 리뷰

## Main Process
\```
1. 학습 노트 수집
   - 지난 7일간 생성된 모든 노트 찾기
   - 카테고리별 분류 (프로그래밍, 도구, 이론 등)

2. 패턴 분석
   - 가장 많이 학습한 주제
   - 학습 시간 분포
   - 난이도 분포

3. 성과 요약
   - 새로 배운 핵심 개념 (Top 5)
   - 완료한 실습 프로젝트
   - 해결한 문제들

4. 다음 주 계획
   - 복습이 필요한 주제
   - 심화 학습 추천
   - 실전 적용 아이디어
\```

## Output Format
\```markdown
# 주간 학습 리뷰 - {{year}}년 {{week}}주차

**기간**: {{start_date}} ~ {{end_date}}
**총 학습 노트**: {{count}}개
**주요 카테고리**: {{top_categories}}

## 📊 학습 통계

| 카테고리 | 노트 수 | 주요 주제 |
|---------|--------|----------|
| 프로그래밍 | X개 | Python, JavaScript |
| 도구 | Y개 | Git, Docker |

## 🎯 주요 성과

### 새로 배운 핵심 개념
1. **개념 1**: 간단한 설명
2. **개념 2**: 간단한 설명
3. **개념 3**: 간단한 설명

### 완료한 실습
- [x] 프로젝트 1
- [x] 프로젝트 2

## 💡 인사이트

[이번 주 학습에서 얻은 통찰]

## 📅 다음 주 계획

### 복습
- [ ] 개념 X 복습 (이해도 강화)
- [ ] 실습 Y 재실행

### 심화 학습
- [ ] 주제 A 깊이 파기
- [ ] 관련 프로젝트 시작

### 실전 적용
- [ ] 아이디어 1 구현
- [ ] 아이디어 2 프로토타입

## 🔗 관련 노트
- [[주간 리뷰 지난주]]
- [[월간 학습 목표]]
\```
```

#### orchestrator.yaml 설정

```yaml
nodes:
  - type: agent
    name: Weekly Learning Review (WLR)
    abbreviation: wlr
    executor: claude_code
    cron: "0 18 * * 0"  # 매주 일요일 오후 6시
    input_path: vl_ai4pkm_materials
    trigger_max_age_hours: 168  # 7일 (7*24)
    output_path: Reviews/Weekly
    output_type: new_file
    timeout_minutes: 30
    task_priority: high
    enabled: true
```

### 예제 3: 코드 스니펫 추출기

**목적**: 학습 노트에서 코드 예제를 추출하여 재사용 가능한 스니펫 생성

#### 프롬프트 파일

`_Settings_/Prompts/Code Snippet Extractor (CSE).md`:

```markdown
---
title: Code Snippet Extractor (CSE)
abbreviation: CSE
category: automation
description: 학습 노트에서 코드 예제를 추출하고 문서화
version: 1.0
---

# Code Snippet Extractor

학습 노트의 코드 블록을 추출하여 재사용 가능한 스니펫으로 정리합니다.

## Input
- Source: vl_ai4pkm_materials/*.md
- 코드 블록이 포함된 학습 노트

## Output
- File: CodeSnippets/{{language}}/{{snippet_name}}.md
- 언어별로 분류된 코드 스니펫

## Main Process
\```
1. 코드 블록 탐지
   - 마크다운 코드 펜스 (```) 찾기
   - 언어 식별 (python, javascript, etc.)
   - 인라인 코드 무시

2. 코드 분석
   - 코드의 목적 파악
   - 입력/출력 확인
   - 의존성 파악

3. 문서화
   - 설명 추가
   - 사용 예시
   - 주의사항

4. 분류 및 저장
   - 언어별 폴더에 저장
   - 적절한 이름 부여
   - 태그 추가
\```

## Output Format
\```markdown
# {{snippet_name}}

**언어**: {{language}}
**카테고리**: {{category}}
**난이도**: 초급/중급/고급

## 설명
[이 코드가 하는 일]

## 코드
\```{{language}}
// 주석이 추가된 코드
{{code}}
\```

## 사용 예시
\```{{language}}
// 실제 사용 예
{{usage_example}}
\```

## 의존성
- {{dependency1}}
- {{dependency2}}

## 주의사항
- 주의사항 1
- 주의사항 2

## 출처
[[{{source_note}}]]

## 태그
#{{language}} #{{category}} #snippet
\```
```

#### orchestrator.yaml 설정

```yaml
nodes:
  - type: agent
    name: Code Snippet Extractor (CSE)
    abbreviation: cse
    executor: claude_code
    input_path: vl_ai4pkm_materials
    trigger_content_pattern: "```"  # 코드 블록 있는 파일만
    output_path: CodeSnippets
    output_type: new_file
    timeout_minutes: 10
    max_parallel: 3
    enabled: true
```

---

## 다음 단계

1. ✅ 커스텀 에이전트 생성 방법 학습
2. ✅ 프롬프트 작성 Best Practices 이해
3. ✅ orchestrator.yaml 설정 마스터
4. ✅ 고급 트리거 조건 활용
5. ⬜ 실전 프로젝트 적용
6. ⬜ 워크플로우 체인 구성
7. ⬜ 성능 최적화 및 모니터링

## 관련 문서

- [[02_trigger_patterns_reference.md]] - 트리거 패턴 완전 레퍼런스
- [[03_prompt_writing_best_practices.md]] - 프롬프트 작성 가이드
- [[../03-Orchestrator_Deep_Dive/01_orchestrator_architecture.md]] - Orchestrator 아키텍처
- [[../03-Orchestrator_Deep_Dive/02_poller_system_guide.md]] - Poller 시스템

## 체크리스트

- [ ] 프롬프트 파일 구조를 이해한다
- [ ] Front Matter 필드를 올바르게 작성할 수 있다
- [ ] orchestrator.yaml에 노드를 추가할 수 있다
- [ ] input_path와 output_path를 적절히 설정할 수 있다
- [ ] 파일 패턴 필터를 사용할 수 있다
- [ ] 내용 기반 트리거를 구현할 수 있다
- [ ] 후처리 액션을 설정할 수 있다
- [ ] Cron 스케줄을 설정할 수 있다
- [ ] --orchestrator-status로 에이전트를 확인할 수 있다
- [ ] 로그와 Task 파일을 통해 디버깅할 수 있다
