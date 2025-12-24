# Vibe Learning - 범용 학습 프롬프트

이 프롬프트는 **Vibe Learning 방법론**을 사용하여 오픈소스 프로젝트나 지속적으로 변화하는 프로젝트를 학습할 때 사용하는 범용 프롬프트입니다.

## 프로젝트 정보

**학습 중인 프로젝트**: AI4PKM (AI-powered Personal Knowledge Management)
**프로젝트 Repository**: https://github.com/jykim/AI4PKM

**학습 자료 Repository**: https://github.com/solkit70/VL_for_AI4PKM_Automation_Features.git
**학습 자료 폴더**: `VL_AI4PKM_Automation/`

**학습 RoadMap 위치**: `VL_AI4PKM_Automation/vl_roadmap/` 폴더
**학습 프롬프트 위치**: `VL_AI4PKM_Automation/vl_prompts/` 폴더
**학습 WorkLog 위치**: `VL_AI4PKM_Automation/vl_worklog/` 폴더
**학습 산출물 위치**: `VL_AI4PKM_Automation/01-xxx/`, `02-xxx/`, `03-xxx/` ... (번호순 폴더)

---

## Continuous Vibe Learning - 지속적 학습 프로세스 (매우 중요!)

많은 프로젝트들이 활발하게 개발 중입니다. 학습 중에도 프로젝트가 계속 업데이트되므로, **매 학습 세션 시작 전 Remote Repository와의 동기화 확인**이 필요합니다.

**중요**: Repository 동기화는 **학습 대상 프로젝트**(예: https://github.com/jykim/AI4PKM)와 비교합니다. 학습 자료 폴더(예: `VL_AI4PKM_Automation/`)는 별도 Repository에서 관리되므로 비교 대상에서 제외합니다.

### 학습 시작 전 필수 단계

**매번 학습을 시작할 때마다 다음 순서로 진행하세요:**

1. **Remote Repository 동기화 확인 여부 판단**
   - Remote Repository를 참고하는 프로젝트인가?
   - 예: 오픈소스 프로젝트, 팀 프로젝트, 지속 업데이트되는 프로젝트
   - 아니오: 개인 프로젝트, 정적 학습 자료, 완료된 프로젝트

2. **동기화가 필요한 경우 실행**
   ```bash
   # 예시 1: Fork한 오픈소스 프로젝트 (upstream)
   git fetch upstream
   git status

   # 예시 2: 팀 Repository (origin)
   git fetch origin
   git status

   # 예시 3: 다른 remote
   git fetch [remote-name]
   git status
   ```

3. **변경사항 분석**
   - Remote와 로컬의 차이 확인
   - 어떤 파일이 변경되었는지 파악
   - **학습 자료 폴더는 분석 대상에서 제외** (별도 Repository에서 관리)
   - 학습 대상 프로젝트의 코어 코드 변경만 평가
   - 변경 내용의 규모와 영향도 평가

4. **사용자에게 변경사항 보고**
   - 변경된 파일 목록
   - 주요 변경 내용 요약
   - 기존 학습 자료에 미치는 영향도
   - 권장 조치사항

5. **동기화 결정**
   - **대규모 변경**: 학습 자료 전면 업데이트 필요 → 별도 작업 세션
   - **중간 변경**: 관련 학습 자료만 부분 업데이트 → 오늘 학습 전 처리
   - **소규모 변경**: 현재 학습 자료 유지 → 학습 계속 진행

### 동기화 워크플로우

#### 단계 1: 변경사항 확인

```bash
# Remote 최신 커밋 가져오기 (프로젝트에 맞게 조정)
git fetch [remote-name]  # upstream, origin, 등

# 현재 상태 확인
git status

# Remote와의 차이 확인
git log HEAD..[remote-name]/[branch-name] --oneline

# 변경된 파일 목록 (학습 자료 폴더 제외)
git diff --name-status HEAD [remote-name]/[branch-name] -- . ':!VL_*' ':!**/vl_*'
```

#### 단계 2: 변경 내용 분석 및 보고

**AI가 사용자에게 보고할 내용:**

```markdown
## 🔄 Repository 동기화 상태 보고

**날짜**: [오늘 날짜]
**Remote 상태**: [최신 커밋 해시 및 메시지]
**로컬 상태**: [현재 커밋 해시]

### 📊 변경 내용 요약

**변경된 파일 수**: X개
**주요 변경 영역**:
- [주요 폴더/모듈]: [변경 사항]
- [기타 영역]: [변경 사항]

### 🎯 영향도 평가

**기존 학습 자료 영향**:
- [ ] 01-xxx: [영향 없음/부분 업데이트 필요/전면 업데이트 필요]
- [ ] 02-xxx: [영향 없음/부분 업데이트 필요/전면 업데이트 필요]
- [ ] WorkLog: [영향 없음/참고사항 추가 필요]

### 💡 권장 조치

**옵션 A**: [즉시 동기화 및 학습 자료 업데이트]
**옵션 B**: [학습 자료 유지하고 학습 계속]
**옵션 C**: [별도 세션에서 업데이트 작업 진행]

**추천**: [AI의 권장사항과 이유]
```

#### 단계 3: 동기화 실행 (사용자 승인 후)

**대규모 변경 시**:
```bash
# 로컬 변경사항 보존 (학습 자료)
# .gitignore에 학습 자료 폴더들이 설정되어 있는지 확인

# Remote 최신 코드로 업데이트
git reset --hard [remote-name]/[branch-name]

# 상태 확인
git status
```

**소규모 변경 시**:
```bash
# 선택적 파일만 업데이트
git checkout [remote-name]/[branch-name] -- [특정 파일들]

# 또는 merge
git merge [remote-name]/[branch-name]
```

#### 단계 4: 학습 자료 업데이트 (필요시)

**업데이트 필요 여부 판단 기준**:

1. **전면 업데이트 필요** (별도 작업 세션):
   - 핵심 아키텍처 변경
   - 주요 API/인터페이스 변경
   - 파일 구조 재구성
   - **예상 작업 시간**: 2-4시간
   - **작업 내용**: 학습 문서 다수 전면 개정

2. **부분 업데이트 필요** (오늘 학습 전 30-60분):
   - 새로운 기능 추가
   - 함수/클래스 이름 변경
   - 버그 수정으로 인한 동작 변경
   - **작업 내용**: 관련 문서 1-2개 섹션 수정

3. **업데이트 불필요** (학습 계속):
   - 테스트 코드 변경
   - 문서(README) 업데이트
   - 마이너 버그 수정
   - 학습 중인 영역과 무관한 변경
   - **작업 내용**: WorkLog에 참고사항만 기록

### 변경사항 추적 및 기록

**WorkLog에 기록할 내용**:
```markdown
## 🔄 Continuous Vibe Learning - Repository 동기화

**동기화 일시**: [날짜 시간]
**Remote 커밋**: [해시] - [메시지]
**이전 로컬**: [해시] - [메시지]

### 주요 변경사항
1. [변경 내용 1]
2. [변경 내용 2]

### 학습 자료 업데이트
- [ ] 01-xxx: [작업 내용 또는 "변경 없음"]
- [ ] 02-xxx: [작업 내용 또는 "변경 없음"]

### 오늘 학습에 미치는 영향
- [영향 없음 / 참고사항 / 주의사항]
```

### Continuous Vibe Learning의 핵심 원칙

1. **항상 최신 상태 유지 (필요시)**
   - 매 학습 시작 전 동기화 필요성 판단
   - 변경사항을 학습의 일부로 통합

2. **변화를 학습 기회로 활용**
   - 변경 사항을 분석하며 더 깊이 이해
   - 프로젝트의 진화 과정 학습

3. **학습 자료의 신선도 유지**
   - 최신 코드와 문서의 일치성 유지
   - Obsolete 정보 제거

4. **유연한 학습 계획**
   - 예정된 학습과 업데이트 작업 균형
   - 필요시 학습 계획 조정

### 예상 시나리오별 대응

**시나리오 1**: "Remote Repository 사용 안 함"
- 동기화 단계 건너뛰기
- 바로 학습 계획 수립

**시나리오 2**: "큰 변화 없음"
- 동기화 상태만 확인
- WorkLog에 "변경 없음" 기록
- 예정된 학습 계속 진행

**시나리오 3**: "새 기능 추가"
- 변경 내용 분석
- 관련 문서에 새 기능 추가
- 실습 예제 업데이트

**시나리오 4**: "Breaking Change"
- 즉시 사용자에게 보고
- 별도 업데이트 세션 일정 협의
- 오늘은 기존 자료로 학습 또는 업데이트 작업

---

## Vibe Learning 프로젝트 구조

Vibe Learning 방법론을 따르는 모든 프로젝트는 다음 구조를 사용합니다:

**중요**: 학습 자료는 **별도 폴더**에서 관리되며, 학습 대상 프로젝트와 구분됩니다.

```
학습_대상_프로젝트_루트/        # 예: AI4PKM (https://github.com/jykim/AI4PKM)
├── ai4pkm_cli/                # 학습 대상 코드
├── orchestrator/              # 학습 대상 코드
├── ...
│
└── VL_학습자료_폴더/           # 예: VL_AI4PKM_Automation (별도 Repository 관리)
    ├── vl_roadmap/           # 학습 로드맵 파일들
    │   └── YYYYMMDD_RoadMap_Title.md
    │
    ├── vl_prompts/           # 학습 프롬프트 파일들
    │   ├── YYYYMMDD_Prompt_Name.md
    │   └── 20251121_Each_Day_Learning_prompt.md  (이 파일)
    │
    ├── vl_worklog/           # 학습 작업 로그
    │   ├── YYYYMMDD_Day1_Topic.md
    │   ├── YYYYMMDD_Day2_Topic.md
    │   └── YYYYMMDD_Update_Work.md
    │
    ├── 01-TopicName/         # 학습 산출물 폴더 (순서대로 번호)
    │   ├── document1.md
    │   └── example_code.py
    │
    ├── 02-NextTopic/         # 다음 주제 산출물
    │   └── ...
    │
    └── ...
```

**Repository 관리 원칙**:
- 학습 대상 프로젝트: 원본 Repository (예: jykim/AI4PKM)
- 학습 자료 폴더: 별도 Repository (예: solkit70/VL_for_AI4PKM_Automation_Features)
- 동기화 시 학습 자료 폴더는 비교 대상에서 제외

---

## Git 워크플로우 (매우 중요!)

이 프로젝트는 **두 개의 Repository**를 사용합니다. 혼동하지 않도록 명확하게 구분하세요.

### Repository 구조

```
로컬 프로젝트 루트
├── ai4pkm_cli/              ← upstream (jykim/AI4PKM)에서 동기화
├── orchestrator/            ← upstream (jykim/AI4PKM)에서 동기화
├── ...                      ← upstream (jykim/AI4PKM)에서 동기화
│
└── VL_AI4PKM_Automation/    ← 학습 자료 (동기화 대상 제외)
    ├── vl_roadmap/
    ├── vl_worklog/
    ├── 01-xxx/
    └── ...

Git Remotes:
- upstream: https://github.com/jykim/AI4PKM (학습 대상 프로젝트)
- origin: https://github.com/solkit70/VL_for_AI4PKM_Automation_Features (학습 자료 저장소)
```

### 워크플로우 1: 학습 시작 전 - Upstream 동기화 확인

**목적**: 학습 대상 프로젝트(jykim/AI4PKM)의 최신 변경사항 확인

```bash
# 1. upstream에서 최신 코드 가져오기
git fetch upstream

# 2. 변경사항 확인 (VL_AI4PKM_Automation 폴더 제외)
git log HEAD..upstream/main --oneline
git diff --name-status HEAD upstream/main -- . ':!VL_*' ':!**/vl_*'

# 3. 필요시 upstream 변경사항을 로컬에 병합
# (주의: VL_AI4PKM_Automation은 .gitignore로 보호되므로 영향 없음)
git merge upstream/main
```

**중요**:
- VL_AI4PKM_Automation 폴더는 동기화 분석에서 **반드시 제외**
- upstream은 **읽기 전용** - 동기화만 하고 push하지 않음

### 워크플로우 2: 학습 완료 후 - Origin에 Push

**목적**: 학습 자료와 모든 변경사항을 학습 Repository에 저장

```bash
# 1. 변경된 파일 확인
git status

# 2. 학습 자료 추가 (VL_AI4PKM_Automation 폴더는 .gitignore에 있으므로 -f 필요)
git add -f VL_AI4PKM_Automation/

# 3. 기타 변경된 파일도 추가 (필요시)
git add [다른_파일들]

# 4. Commit 생성
git commit -m "docs: [학습 내용 요약]

[상세 설명]

🤖 Generated with Claude Code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 5. origin에 push
git push origin main
```

**중요**:
- origin은 **학습 자료 저장소** - 여기에만 push
- VL_AI4PKM_Automation 폴더와 upstream에서 동기화된 모든 파일 포함
- upstream에서 가져온 코드도 origin에 함께 push됨

### 워크플로우 요약표

| 작업 | Repository | 명령어 | 포함 범위 |
|------|-----------|--------|----------|
| **학습 전 동기화** | upstream (jykim/AI4PKM) | `git fetch upstream`<br>`git merge upstream/main` | 학습 대상 프로젝트 코드만<br>(VL_ 폴더 제외) |
| **학습 후 저장** | origin (solkit70/VL_...) | `git add -f VL_AI4PKM_Automation/`<br>`git commit`<br>`git push origin main` | **전체 프로젝트**<br>(VL_ 폴더 + upstream 코드) |

### 주의사항

1. **절대 upstream에 push하지 마세요**
   - upstream은 학습 대상 프로젝트 (jykim/AI4PKM)
   - 읽기 전용으로만 사용

2. **origin에만 push하세요**
   - origin은 학습 자료 저장소 (solkit70/VL_for_AI4PKM_Automation_Features)
   - 모든 학습 성과를 여기에 저장

3. **VL_AI4PKM_Automation은 force add 필요**
   - `.gitignore`에 포함되어 있음
   - `git add -f VL_AI4PKM_Automation/` 사용

4. **동기화 시 VL_ 폴더 제외**
   - upstream과 비교 시 학습 자료는 제외
   - `':!VL_*' ':!**/vl_*'` 패턴 사용

---

## WorkLog 파일 관리 규칙 (중요!)

### WorkLog 파일명 규칙
- **위치**: `vl_worklog/` 폴더
- **파일명 형식**: `YYYYMMDD_작업내용설명.md`
  - 예: `20251121_Day1_Basics.md`
  - 예: `20251122_Day2_Advanced.md`
  - 예: `20251203_Documentation_Update.md`
- **중요**: 매번 학습할 때마다 **오늘 날짜(YYYYMMDD)로 시작하는 새 WorkLog 파일**을 생성

### WorkLog 생성 규칙
1. **첫 학습 시작 시**:
   - `vl_worklog/` 폴더 확인
   - 오늘 날짜(`YYYYMMDD_`)로 시작하는 파일이 없으면 새로 생성
   - 파일명: `YYYYMMDD_` + RoadMap의 해당 날짜 학습 주제
   - 예: `20251212_Day1_Setup.md`

2. **같은 날 계속 작업 시**:
   - 오늘 날짜로 시작하는 기존 WorkLog 파일에 추가 작성
   - 새 파일을 만들지 말고 기존 파일 업데이트

3. **다음 날 학습 시작 시**:
   - 새로운 날짜(`YYYYMMDD_`)로 시작하는 새 WorkLog 파일 생성
   - 이전 날의 WorkLog를 참조하여 이어서 진행

### WorkLog 작성 내용
매 작업마다 다음을 기록:
- ✅ 완료한 작업 목록
- 📝 작업 상세 내용
- 💡 학습한 주요 포인트
- ⚠️ 발생한 문제와 해결 방법
- 🚀 다음에 해야 할 작업 (매우 중요!)

### WorkLog 마무리
그날 학습 종료 시:
1. 전체 WorkLog를 Review
2. 누락된 내용 추가
3. 다음 학습 세션을 위한 준비사항 명시
4. 다음 세션에서 바로 시작할 수 있도록 구체적인 시작점 기록

---

## 학습 산출물 관리

### 산출물 폴더 구조
- **위치**: 프로젝트 루트 또는 지정된 학습 폴더
- **폴더명 형식**: `NN-TopicName/`
  - NN: 01, 02, 03, ... (학습 순서)
  - TopicName: 학습 주제를 나타내는 설명적인 이름
  - 예: `01-Installation_Setup/`, `02-Basic_Commands/`, `03-Advanced_Features/`

### 산출물 폴더 생성 규칙
1. **학습 순서대로 번호 부여**
   - 첫 번째 주제: `01-Topic1/`
   - 두 번째 주제: `02-Topic2/`
   - 세 번째 주제: `03-Topic3/`

2. **명확한 주제명 사용**
   - 폴더명만 보고 무엇을 학습했는지 알 수 있도록
   - 띄어쓰기는 언더스코어(_)로 대체
   - 영문 또는 한글 사용 가능

3. **산출물 종류**
   - 학습 문서 (`.md` 파일)
   - 실습 코드 (`.py`, `.js`, `.java`, 등)
   - 설정 파일 예제
   - 스크린샷/다이어그램
   - 참고 자료

---

## 실습 진행 (Hands-On Practice)

**중요**: 문서 작성만으로 끝내지 말고, **핵심적인 명령어와 기능은 반드시 직접 실행하면서 학습을 진행**해야 합니다.

### 실습 진행 원칙

1. **환경 확인**:
   - 사용자의 운영체제 확인 (Windows/macOS/Linux)
   - 프로젝트 설치 상태 확인
   - 필요한 도구 설치 여부 확인

2. **문서 작성 + 실습 병행**:
   - 먼저 학습 내용을 문서로 정리
   - **그 다음 핵심 명령어를 직접 실행**하여 결과 확인
   - 실행 결과를 WorkLog에 기록
   - 실행 중 발생한 문제와 해결 방법 문서화

3. **핵심 명령어 우선 실행**:
   - 모든 명령어를 실행할 필요는 없음
   - **필수적이고 자주 사용하는 핵심 명령어**만 선별하여 실행
   - 고급 옵션이나 드물게 사용하는 명령어는 문서로만 정리

4. **실습 워크플로우**:
   ```
   단계 1: 문서 작성 (개념 설명, 명령어 설명)
   단계 2: 핵심 명령어 실행 (AI가 적절한 도구 사용)
   단계 3: 실행 결과 분석 및 설명
   단계 4: 결과를 WorkLog에 기록
   단계 5: 문제가 있으면 해결 과정 문서화
   ```

5. **실습 결과 기록**:
   - WorkLog의 각 단계별 섹션에 실습 결과 추가
   - 성공한 명령어와 출력 결과
   - 실패한 명령어와 오류 메시지
   - 문제 해결 과정
   - 학습한 교훈

### 실습 제외 대상

다음 항목은 문서로만 정리하고 실행하지 않아도 됩니다:
- 시스템 설정을 변경하는 위험한 명령어
- 외부 API를 호출하는 명령어 (API 키가 없는 경우)
- 장시간 실행되는 자동화 작업
- 고급 옵션이나 특수한 상황에서만 사용하는 명령어
- 테스트 환경이 갖춰지지 않은 기능

---

## 학습 시작 프로세스 (Continuous Vibe Learning)

**매 학습 세션마다 반드시 다음 순서로 진행하세요:**

### Step 1: Repository 동기화 (Remote 사용 시)
1. Remote Repository 사용 여부 확인
2. 사용하는 경우:
   - `git fetch [remote-name]` 실행
   - 변경사항 확인 및 분석
   - 사용자에게 동기화 상태 보고
   - 사용자 승인 후 필요시 동기화 및 학습 자료 업데이트
3. 사용하지 않는 경우: 다음 단계로

### Step 2: 오늘의 학습 계획 수립
1. 이전 WorkLog 확인 (어디까지 학습했는지)
2. RoadMap 참조 (오늘 진행할 내용)
3. 학습 목표와 계획을 사용자에게 설명
   - **중요**: 프로그래밍이나 스크립트 실행은 하지 말 것
   - 오늘 학습할 내용만 자세하게 설명

### Step 3: 사용자 승인 후 학습 진행
1. 사용자가 학습 계획을 승인하면
2. 오늘 날짜로 WorkLog 파일 생성 (없는 경우)
3. 학습 진행 및 실습
4. WorkLog에 지속적으로 기록

### Step 4: 학습 종료 시
1. WorkLog 최종 업데이트
2. 다음 세션 준비사항 기록
3. 필요시 개인 Repository에 커밋

---

## AI에게 요청하는 작업 방식

오늘 학습을 어떻게 진행하면 좋을지 저에게 알려 주세요.

**학습 시작 시 AI가 해야 할 일:**
1. ✅ Repository 동기화 필요성 판단 (Remote Repository 사용 여부)
2. ✅ 필요시 동기화 상태 확인 및 보고 (Continuous Vibe Learning)
3. ✅ 변경사항이 학습 자료에 미치는 영향 평가 (동기화 필요 시)
4. ✅ 이전 WorkLog 확인하여 진행 상황 파악
5. ✅ 오늘 학습할 내용을 자세하게 설명 (프로그래밍/스크립트 실행 제외)
6. ✅ 사용자 승인 대기

일단 오늘 할일을 미리 숙지 한 후 학습을 진행하고 싶습니다.
프로그래밍을 하거나 스크립트를 실행하거나 하는 일은 진행하지 말고 오늘 학습할 내용을 자세하게 설명해 주세요.

---

## 학습 자료의 역할

이 학습 방법론에서 사용자는 AI가 만든 자료를 보고 학습하는 것이 목표입니다:

1. **자료 조사**: AI가 프로젝트를 분석하고 필요한 정보를 수집
2. **문서 작성**: AI가 학습하기 좋은 형태로 문서 작성
3. **샘플 코드 작성**: AI가 실습 가능한 완전한 예제 코드 작성
4. **코드 분석**: 필요시 AI가 코드 분석 문서 작성

**사용자는**:
- AI가 작성한 문서를 읽고 이해
- AI가 준비한 샘플 코드를 실행
- 실습 중 문제 발생 시 AI에게 도움 요청

이를 통해 사용자는 효율적이고 체계적으로 학습할 수 있습니다.
