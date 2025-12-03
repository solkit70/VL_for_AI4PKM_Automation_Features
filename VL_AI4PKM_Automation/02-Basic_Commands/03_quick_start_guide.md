# AI4PKM CLI 빠른 시작 가이드 (최신 버전)

**업데이트:** 2025-12-03
**버전:** Orchestrator 중심 아키텍처 (v1.0)

AI4PKM CLI를 처음 사용하는 분들을 위한 실전 튜토리얼입니다. 이 가이드를 따라하면 30분 안에 첫 번째 자동화 워크플로우를 실행할 수 있습니다.

---

## 📋 목차
1. [시작하기 전에](#시작하기-전에)
2. [5분 퀵스타트](#5분-퀵스타트)
3. [단계별 튜토리얼](#단계별-튜토리얼)
4. [첫 번째 워크플로우 실습](#첫-번째-워크플로우-실습)
5. [고급 사용 예제](#고급-사용-예제)
6. [문제 해결 팁](#문제-해결-팁)
7. [다음 단계](#다음-단계)

---

## 시작하기 전에

### 필수 준비사항

이 가이드를 시작하기 전에 다음 항목을 완료하세요:

✅ **AI4PKM CLI 설치 완료**
- [01_installation_guide.md](./01_installation_guide.md) 참조
- `ai4pkm --help` 명령어가 작동하는지 확인

✅ **최소 1개 이상의 Executor 설치**
- Claude Code (권장): `npm install -g @anthropic-ai/claude-code`
- `claude --version` 명령어가 작동하는지 확인

✅ **Obsidian Vault 준비**
- 기존 Vault 또는 새 Vault 준비
- Vault 경로 확인

---

## 5분 퀵스타트

가장 빠르게 AI4PKM을 체험하는 방법입니다.

### 1. 예제 Vault 사용

```bash
# AI4PKM 저장소 클론 (아직 안 했다면)
git clone https://github.com/jykim/AI4PKM.git
cd AI4PKM

# 예제 Vault로 이동
cd ai4pkm_vault
```

### 2. Orchestrator 시작

```bash
# Orchestrator 시작
ai4pkm orchestrator run
```

**예상 출력:**
```
[2025-12-03 10:00:00] Orchestrator starting...
[2025-12-03 10:00:00] Loading agents from orchestrator.yaml
[2025-12-03 10:00:00] Registered agent: Enrich Ingested Content (EIC)
[2025-12-03 10:00:00] Monitoring: Ingest/Clippings
[2025-12-03 10:00:00] Orchestrator running. Press Ctrl+C to stop.
```

### 3. 테스트 파일 생성

**새 터미널을 열고** (Orchestrator는 계속 실행):

```bash
cd AI4PKM/ai4pkm_vault

# 테스트 클리핑 생성
echo "# My First Article

This is a test article for AI4PKM.

## Key Points
- Point 1
- Point 2
" > Ingest/Clippings/test-article.md
```

### 4. 결과 확인

**Orchestrator 터미널에서 로그 확인:**
```
[2025-12-03 10:01:00] File created: Ingest/Clippings/test-article.md
[2025-12-03 10:01:01] Matched agent: Enrich Ingested Content (EIC)
[2025-12-03 10:01:01] Creating task: _Settings_/Tasks/2025-12-03-EIC-test-article.md
[2025-12-03 10:01:02] Executing agent: EIC
[2025-12-03 10:01:30] Agent completed successfully
[2025-12-03 10:01:30] Output: AI/Articles/test-article-enriched.md
```

**생성된 파일 확인:**
```bash
ls AI/Articles/
# 출력: test-article-enriched.md

cat AI/Articles/test-article-enriched.md
```

🎉 **축하합니다!** 첫 번째 AI4PKM 워크플로우가 완료되었습니다.

---

## 단계별 튜토리얼

이제 자신만의 Vault에서 AI4PKM을 설정해봅시다.

### 단계 1: Vault 준비

**옵션 A: 새 Vault 생성**
```bash
mkdir ~/MyVault
cd ~/MyVault
```

**옵션 B: 기존 Obsidian Vault 사용**
```bash
cd /path/to/your/existing/vault
```

---

### 단계 2: 폴더 구조 생성

필수 폴더를 생성합니다:

```bash
# 설정 폴더
mkdir -p _Settings_/Prompts
mkdir -p _Settings_/Tasks
mkdir -p _Settings_/Logs

# 입력 폴더
mkdir -p Ingest/Clippings

# 출력 폴더
mkdir -p AI/Articles
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "_Settings_\Prompts"
New-Item -ItemType Directory -Force -Path "_Settings_\Tasks"
New-Item -ItemType Directory -Force -Path "_Settings_\Logs"
New-Item -ItemType Directory -Force -Path "Ingest\Clippings"
New-Item -ItemType Directory -Force -Path "AI\Articles"
```

**폴더 구조 확인:**
```bash
tree -L 2
# 또는 Windows에서: tree /F
```

---

### 단계 3: 프롬프트 파일 생성

에이전트에게 작업 지시를 제공하는 프롬프트 파일을 생성합니다.

**`_Settings_/Prompts/EIC.md` 생성:**

```markdown
# Enrich Ingested Content (EIC)

You are an AI assistant specialized in enriching web clippings and articles for personal knowledge management.

## Your Task

1. **Read the input file** provided in the Ingest/Clippings folder
2. **Analyze the content** to identify:
   - Main topic and key themes
   - Important insights and takeaways
   - Relevant tags for categorization
3. **Enrich the content** by:
   - Adding a concise summary (2-3 sentences)
   - Extracting key points as bullet list
   - Suggesting relevant tags
   - Improving formatting for readability
4. **Save the enriched version** to the output path

## Output Format

Use Markdown with frontmatter:

```yaml
---
title: [Original Title]
tags: [tag1, tag2, tag3]
summary: [Brief summary]
source: [Original URL if available]
created: [ISO 8601 date]
enriched: [ISO 8601 date]
---

# [Title]

## Summary
[2-3 sentence summary]

## Key Points
- [Point 1]
- [Point 2]
- [Point 3]

## Content
[Original content with improved formatting]

## My Notes
[Placeholder for user's personal notes]
```

## Guidelines

- Keep the original meaning and content intact
- Add value through organization and structure
- Use clear, concise language
- Make it easy to scan and review later
- Preserve any existing metadata
```

**파일 생성 명령:**

**macOS/Linux:**
```bash
cat > _Settings_/Prompts/EIC.md << 'EOF'
[위 내용 붙여넣기]
EOF
```

**Windows:**
```powershell
notepad _Settings_\Prompts\EIC.md
# 위 내용을 복사해서 붙여넣고 저장
```

---

### 단계 4: orchestrator.yaml 생성

Orchestrator 설정 파일을 생성합니다.

**`orchestrator.yaml` 생성:**

```yaml
version: "1.0"

orchestrator:
  # 프롬프트 파일 위치
  prompts_dir: "_Settings_/Prompts"

  # 태스크 파일 저장 위치
  tasks_dir: "_Settings_/Tasks"

  # 로그 파일 위치
  logs_dir: "_Settings_/Logs"

  # 동시 실행 가능한 에이전트 수
  max_concurrent: 2

  # Windows 사용자: Executor 경로 명시 (필요시)
  # executors:
  #   claude:
  #     command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"

defaults:
  # 기본 executor (claude_code 또는 gemini)
  executor: claude_code

  # 에이전트 실행 제한 시간 (분)
  timeout_minutes: 30

nodes:
  # 첫 번째 에이전트: 웹 클리핑 강화
  - type: agent
    name: Enrich Ingested Content (EIC)

    # 입력 폴더 (파일 감시 대상)
    input_path: Ingest/Clippings

    # 출력 폴더
    output_path: AI/Articles

    # 출력 타입 (new_file: 새 파일 생성)
    output_type: new_file

# Poller 설정 (향후 추가 가능)
pollers: {}
```

**파일 생성 명령:**

**macOS/Linux:**
```bash
cat > orchestrator.yaml << 'EOF'
[위 내용 붙여넣기]
EOF
```

**Windows:**
```powershell
notepad orchestrator.yaml
# 위 내용을 복사해서 붙여넣고 저장
```

---

### 단계 5: 설정 확인

모든 설정이 올바른지 확인합니다.

```bash
# 설정 파일 확인
ai4pkm show-config
```

**예상 출력:**
```yaml
Configuration:
  Vault Path: /Users/username/MyVault
  Prompts Dir: _Settings_/Prompts
  Tasks Dir: _Settings_/Tasks
  Logs Dir: _Settings_/Logs
  Max Concurrent: 2

Defaults:
  Executor: claude_code
  Timeout: 30 minutes

Agents:
  1. Enrich Ingested Content (EIC)
     - Executor: claude_code
     - Input: Ingest/Clippings
     - Output: AI/Articles
     - Status: Active
```

**문제가 있다면:**
- `orchestrator.yaml` 파일이 현재 디렉터리에 있는지 확인
- YAML 문법 오류가 없는지 확인 (들여쓰기 주의)
- 폴더 경로가 올바른지 확인

---

## 첫 번째 워크플로우 실습

실제로 웹 클리핑을 강화하는 워크플로우를 실행해봅시다.

### 실습 1: 웹 클리핑 처리

#### 1️⃣ Orchestrator 시작

**터미널 1번:**
```bash
cd ~/MyVault  # 또는 your vault path
ai4pkm orchestrator run
```

**실행 확인:**
```
[2025-12-03 10:30:00] Orchestrator starting...
[2025-12-03 10:30:00] Registered agent: Enrich Ingested Content (EIC)
[2025-12-03 10:30:00] Monitoring: Ingest/Clippings
[2025-12-03 10:30:00] Orchestrator running. Press Ctrl+C to stop.
```

---

#### 2️⃣ 테스트 클리핑 생성

**터미널 2번 (새 터미널 열기):**

```bash
cd ~/MyVault

# 샘플 클리핑 생성
cat > Ingest/Clippings/ai-trends-2025.md << 'EOF'
# AI Trends in 2025

Source: https://example.com/ai-trends-2025

The field of artificial intelligence continues to evolve rapidly. Here are some key developments to watch in 2025:

## Multimodal AI
AI systems are becoming increasingly capable of processing and understanding multiple types of data simultaneously - text, images, audio, and video. This enables more natural and versatile interactions.

## AI Agents
We're seeing a shift from simple chatbots to sophisticated AI agents that can plan, reason, and execute complex tasks autonomously. These agents can use tools, interact with APIs, and maintain context over extended conversations.

## Open Source Movement
The open source AI community is thriving, with powerful models becoming freely available. This democratization of AI technology is accelerating innovation across all sectors.

## Personalization
AI systems are becoming better at adapting to individual users' preferences, communication styles, and needs. Personal AI assistants are moving beyond generic responses to truly personalized experiences.

## Regulatory Frameworks
Governments worldwide are establishing frameworks to ensure responsible AI development and deployment. This includes guidelines for transparency, accountability, and ethical use.
EOF
```

---

#### 3️⃣ 자동 실행 관찰

**터미널 1번 (Orchestrator)에서 로그 확인:**

```
[2025-12-03 10:31:00] File created: Ingest/Clippings/ai-trends-2025.md
[2025-12-03 10:31:01] Matched agent: Enrich Ingested Content (EIC)
[2025-12-03 10:31:01] Creating task: _Settings_/Tasks/2025-12-03-EIC-ai-trends-2025.md
[2025-12-03 10:31:02] Executing agent: EIC with claude_code
[2025-12-03 10:31:02] Task file: _Settings_/Tasks/2025-12-03-EIC-ai-trends-2025.md
[2025-12-03 10:31:45] Agent completed successfully
[2025-12-03 10:31:45] Output: AI/Articles/ai-trends-2025-enriched.md
```

---

#### 4️⃣ 결과 확인

**터미널 2번:**

```bash
# 생성된 파일 확인
ls -l AI/Articles/

# 내용 보기
cat AI/Articles/ai-trends-2025-enriched.md
```

**예상 결과 (샘플):**

```markdown
---
title: AI Trends in 2025
tags: [artificial-intelligence, ai-trends, technology, machine-learning, 2025]
summary: Overview of key AI developments in 2025 including multimodal systems, autonomous agents, open source movement, personalization, and regulatory frameworks.
source: https://example.com/ai-trends-2025
created: 2025-12-03T10:31:00Z
enriched: 2025-12-03T10:31:45Z
---

# AI Trends in 2025

## Summary
This article explores five major trends shaping artificial intelligence in 2025: the rise of multimodal AI systems, the evolution from chatbots to autonomous agents, the democratization through open source, advances in personalization, and the emergence of regulatory frameworks worldwide.

## Key Points
- **Multimodal AI**: Systems processing text, images, audio, and video simultaneously for more natural interactions
- **AI Agents**: Shift to sophisticated agents capable of planning, reasoning, and executing complex tasks autonomously
- **Open Source Movement**: Powerful models becoming freely available, accelerating innovation
- **Personalization**: AI adapting to individual users' preferences and communication styles
- **Regulatory Frameworks**: Government guidelines ensuring responsible AI development and ethical use

## Content

[Original content preserved with improved formatting...]

## My Notes
[Add your personal reflections and connections here]
```

---

#### 5️⃣ 태스크 파일 확인

```bash
# 태스크 파일 확인
cat _Settings_/Tasks/2025-12-03-EIC-ai-trends-2025.md
```

**태스크 파일 구조:**
```yaml
---
agent: Enrich Ingested Content (EIC)
status: done
input_file: Ingest/Clippings/ai-trends-2025.md
output_file: AI/Articles/ai-trends-2025-enriched.md
started_at: 2025-12-03T10:31:02Z
completed_at: 2025-12-03T10:31:45Z
priority: normal
---

[Task execution log...]
```

---

### 실습 2: 여러 파일 동시 처리

Orchestrator는 여러 파일을 동시에 처리할 수 있습니다.

```bash
# 3개 파일 동시 생성
echo "# Article 1" > Ingest/Clippings/article1.md
echo "# Article 2" > Ingest/Clippings/article2.md
echo "# Article 3" > Ingest/Clippings/article3.md
```

**Orchestrator 로그:**
```
[2025-12-03 10:35:00] File created: Ingest/Clippings/article1.md
[2025-12-03 10:35:00] File created: Ingest/Clippings/article2.md
[2025-12-03 10:35:00] File created: Ingest/Clippings/article3.md
[2025-12-03 10:35:01] Executing 2 agents concurrently (max_concurrent: 2)
[2025-12-03 10:35:01] Agent 1: EIC (article1.md)
[2025-12-03 10:35:01] Agent 2: EIC (article2.md)
[2025-12-03 10:35:45] Agent 1 completed
[2025-12-03 10:35:46] Agent 3: EIC (article3.md) [queued → executing]
```

**동시 실행 제한** (`max_concurrent: 2`)으로 인해:
- 파일 1, 2: 즉시 처리
- 파일 3: 대기 후 처리

---

### 실습 3: 디버그 모드 사용

문제가 발생했을 때 디버그 모드로 실행합니다.

**Orchestrator 중지:**
```bash
# 터미널 1번에서 Ctrl+C
```

**디버그 모드로 재시작:**
```bash
ai4pkm orchestrator run --debug
```

**디버그 출력 예:**
```
[DEBUG] Loading orchestrator.yaml
[DEBUG] Parsing orchestrator section
[DEBUG] prompts_dir: _Settings_/Prompts
[DEBUG] tasks_dir: _Settings_/Tasks
[DEBUG] Parsing nodes section
[DEBUG] Found agent: Enrich Ingested Content (EIC)
[DEBUG] Input path: Ingest/Clippings
[DEBUG] Output path: AI/Articles
[DEBUG] Executor: claude_code
[DEBUG] Resolving executor path: claude
[DEBUG] Found in PATH: /usr/local/bin/claude
[DEBUG] Starting file monitor
[DEBUG] Watching: /Users/username/MyVault/Ingest/Clippings
[INFO] Orchestrator running
```

**디버그 모드가 유용한 경우:**
- Executor를 찾을 수 없을 때
- 파일 감지가 작동하지 않을 때
- 에이전트 실행이 실패할 때

---

## 고급 사용 예제

### 예제 1: 멀티 에이전트 파이프라인

여러 에이전트를 연결하여 파이프라인을 구성합니다.

**orchestrator.yaml 수정:**

```yaml
nodes:
  # 1단계: 클리핑 강화
  - type: agent
    name: Enrich Ingested Content (EIC)
    input_path: Ingest/Clippings
    output_path: AI/Articles
    output_type: new_file

  # 2단계: 소셜 미디어 포스팅 생성
  - type: agent
    name: Create Thread Postings (CTP)
    input_path: AI/Articles
    output_path: AI/Sharable
    output_type: new_file
```

**프롬프트 파일 생성:** `_Settings_/Prompts/CTP.md`

```markdown
# Create Thread Postings (CTP)

Convert enriched articles into engaging social media thread posts.

## Task
- Read the enriched article
- Create a Twitter/X thread (8-10 tweets)
- Each tweet max 280 characters
- Include relevant hashtags

## Output Format
```markdown
---
title: [Original Title] - Thread
source_article: [Path to original enriched article]
platform: twitter
created: [ISO date]
---

# Thread: [Title]

## Tweet 1 (Hook)
[Attention-grabbing opening]

## Tweet 2
[Main point 1]

...

## Tweet 10 (CTA)
[Call to action]

Hashtags: #AI #Technology
```
```

**워크플로우:**
1. `Ingest/Clippings/article.md` 생성
2. EIC 자동 실행 → `AI/Articles/article-enriched.md` 생성
3. CTP 자동 실행 (AI/Articles 감시) → `AI/Sharable/article-thread.md` 생성

---

### 예제 2: Cron 스케줄링 (데일리 라운드업)

매일 정해진 시간에 자동 실행되는 에이전트를 추가합니다.

**orchestrator.yaml에 추가:**

```yaml
nodes:
  # ... (기존 EIC 에이전트)

  # 데일리 라운드업 (매일 새벽 1시)
  - type: agent
    name: Generate Daily Roundup (GDR)
    cron: "0 1 * * *"  # 분 시 일 월 요일
    output_path: AI/Roundup
    output_type: new_file
```

**프롬프트 파일:** `_Settings_/Prompts/GDR.md`

```markdown
# Generate Daily Roundup (GDR)

Create a daily summary of all enriched articles from yesterday.

## Task
- Find all articles in AI/Articles/ from yesterday
- Summarize each article briefly
- Organize by topic/theme
- Create a consolidated daily roundup

## Output Format
```markdown
---
title: Daily Roundup - [Date]
type: roundup
created: [ISO date]
articles_count: [number]
---

# Daily Roundup: [Date]

## Summary
[1-2 sentence overview]

## Articles Processed

### [Topic 1]
- **[Article 1 Title]**: [1 sentence summary]
- **[Article 2 Title]**: [1 sentence summary]

### [Topic 2]
...

## Key Insights
- [Insight 1]
- [Insight 2]
```
```

**동작:**
- Orchestrator가 실행 중일 때, 매일 새벽 1시에 GDR 에이전트가 자동 실행됩니다.
- 수동 테스트: `ai4pkm trigger-agent "GDR"`

---

### 예제 3: Poller 설정 (외부 데이터 동기화)

외부 소스에서 주기적으로 데이터를 가져옵니다.

**orchestrator.yaml에 추가:**

```yaml
pollers:
  gobi:
    enabled: true
    target_dir: "Ingest/Gobi"
    poll_interval: 3600  # 1시간마다 (초 단위)
    tags:
      - "daily"
      - "important"
```

**동작:**
- Gobi 앱에서 `daily`, `important` 태그가 있는 메모를 1시간마다 가져옵니다.
- `Ingest/Gobi/` 폴더에 Markdown 파일로 저장됩니다.
- EIC 에이전트가 자동으로 처리합니다 (input_path가 `Ingest/`로 시작하면).

---

### 예제 4: 수동 에이전트 실행

Orchestrator를 실행하지 않고 특정 파일만 처리합니다.

```bash
# 특정 파일에 대해 EIC 실행
ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/specific-article.md"

# 데일리 라운드업 즉시 실행
ai4pkm trigger-agent "GDR"
```

**사용 사례:**
- 특정 파일만 재처리하고 싶을 때
- Cron 에이전트를 예정 시간 외에 실행하고 싶을 때
- 테스트 및 디버깅할 때

---

## 문제 해결 팁

### 문제 1: Orchestrator가 파일을 감지하지 못함

**증상:**
- 파일을 `Ingest/Clippings/`에 생성해도 아무 반응 없음

**체크리스트:**

1. **Orchestrator가 실행 중인지 확인**
   ```bash
   # 터미널에 "Orchestrator running" 메시지가 보이나요?
   ```

2. **파일 경로 확인**
   ```bash
   # orchestrator.yaml의 input_path와 실제 폴더 경로가 일치하나요?
   cat orchestrator.yaml | grep input_path
   ls -la Ingest/Clippings/
   ```

3. **디버그 모드로 실행**
   ```bash
   ai4pkm orchestrator run --debug
   # "Watching: ..." 메시지에 올바른 경로가 보이나요?
   ```

4. **파일 생성 방법 확인**
   - 파일을 "이동"하지 말고 "생성"하세요 (move 대신 copy 또는 새로 작성)
   - watchdog는 `create` 이벤트를 감지합니다

---

### 문제 2: Executor를 찾을 수 없음 (Windows)

**증상:**
```
ERROR: Could not resolve path for executor: claude
```

**해결 방법:**

1. **Executor 경로 찾기**
   ```powershell
   where.exe claude
   # 출력 예: C:\Users\YourName\AppData\Roaming\npm\claude.cmd
   ```

2. **orchestrator.yaml에 경로 명시**
   ```yaml
   orchestrator:
     executors:
       claude:
         command: "C:\\Users\\YourName\\AppData\\Roaming\\npm\\claude.cmd"
   ```

3. **Orchestrator 재시작**
   ```bash
   ai4pkm orchestrator run --debug
   # "Found executor: ..." 메시지 확인
   ```

---

### 문제 3: 에이전트 실행이 실패함

**증상:**
```
[ERROR] Agent execution failed: EIC
```

**디버깅 단계:**

1. **로그 파일 확인**
   ```bash
   cat _Settings_/Logs/ai4pkm.log
   # 또는
   tail -50 _Settings_/Logs/ai4pkm.log
   ```

2. **태스크 파일 확인**
   ```bash
   cat _Settings_/Tasks/[최신-태스크-파일].md
   # 에러 메시지가 기록되어 있습니다
   ```

3. **프롬프트 파일 확인**
   - `_Settings_/Prompts/EIC.md` 파일이 존재하나요?
   - 내용이 비어있지 않나요?

4. **Executor 인증 확인**
   ```bash
   claude --version
   # 인증이 필요하면 자동으로 프롬프트가 나타납니다
   ```

5. **수동 테스트**
   ```bash
   # Orchestrator 없이 직접 실행
   ai4pkm trigger-agent "EIC" --file "Ingest/Clippings/test.md"
   ```

---

### 문제 4: 출력 파일이 생성되지 않음

**증상:**
- 에이전트가 성공했다고 나오지만 출력 파일이 없음

**체크리스트:**

1. **출력 폴더 존재 확인**
   ```bash
   ls -la AI/Articles/
   # 폴더가 없으면:
   mkdir -p AI/Articles
   ```

2. **orchestrator.yaml의 output_path 확인**
   ```yaml
   nodes:
     - name: EIC
       output_path: AI/Articles  # 이 경로가 맞나요?
   ```

3. **프롬프트에 저장 지시 명시**
   - 프롬프트에 "Save to output path" 지시가 있나요?

4. **Executor 권한 확인**
   - 출력 폴더에 쓰기 권한이 있나요?

---

### 문제 5: 동시 실행이 작동하지 않음

**증상:**
- 여러 파일을 생성해도 하나씩만 처리됨

**확인 사항:**

```yaml
orchestrator:
  max_concurrent: 2  # 이 값이 1보다 큰가요?
```

**로그 확인:**
```bash
ai4pkm orchestrator run --debug
# "Executing N agents concurrently" 메시지 확인
```

---

### 문제 6: orchestrator.yaml 문법 오류

**증상:**
```
ERROR: Failed to parse orchestrator.yaml
```

**일반적인 실수:**

1. **들여쓰기 오류** (YAML은 공백 2칸 사용)
   ```yaml
   # 잘못된 예:
   orchestrator:
   prompts_dir: "_Settings_/Prompts"  # 들여쓰기 없음!

   # 올바른 예:
   orchestrator:
     prompts_dir: "_Settings_/Prompts"
   ```

2. **따옴표 누락**
   ```yaml
   # Windows 경로는 따옴표 필수:
   prompts_dir: "C:\\Users\\Name\\Vault\\_Settings_\\Prompts"
   ```

3. **리스트 형식 오류**
   ```yaml
   # 잘못된 예:
   nodes:
   - type: agent

   # 올바른 예:
   nodes:
     - type: agent
   ```

**검증 도구:**
```bash
# YAML 문법 검사 (온라인)
# https://www.yamllint.com/
```

---

## 다음 단계

축하합니다! 이제 AI4PKM CLI의 기본 워크플로우를 익혔습니다. 다음 단계를 확인하세요:

### 학습 자료

1. **[01_installation_guide.md](./01_installation_guide.md)**
   - 추가 Executor 설치 (Gemini, Codex)
   - 고급 설정 옵션

2. **[02_command_cheatsheet.md](./02_command_cheatsheet.md)**
   - 모든 CLI 명령어 레퍼런스
   - 실전 예제 및 패턴

3. **[../01-AI4PKM_CLI_Structure/03_config_file_guide.md](../01-AI4PKM_CLI_Structure/03_config_file_guide.md)**
   - orchestrator.yaml 상세 설정
   - Poller 설정
   - Secrets 관리

4. **[../01-AI4PKM_CLI_Structure/02_module_overview.md](../01-AI4PKM_CLI_Structure/02_module_overview.md)**
   - 내부 모듈 구조
   - 개발자 가이드

---

### 다음 실습 아이디어

#### 📝 커스텀 에이전트 만들기
자신만의 에이전트를 추가해보세요:
- 프롬프트: 번역 에이전트, 요약 에이전트, 태그 추출 에이전트
- 입력/출력 폴더 설계

#### 🔄 멀티 에이전트 파이프라인
3단계 이상의 파이프라인:
1. 클리핑 강화 (EIC)
2. 주요 인사이트 추출 (Extract Insights)
3. 소셜 미디어 포스팅 생성 (CTP)
4. 데일리 라운드업 (GDR)

#### 🌐 Poller 통합
외부 데이터 소스 연결:
- Gobi 메모
- Limitless 녹취록
- Apple Photos 로그
- RSS 피드 (커스텀 Poller)

#### ⏰ 스케줄링 활용
Cron을 사용한 주기적 작업:
- 매일 아침 뉴스 요약
- 주간 리뷰 생성
- 월간 통계 리포트

---

### 커뮤니티 및 지원

- **GitHub 저장소**: https://github.com/jykim/AI4PKM
- **Issue 보고**: https://github.com/jykim/AI4PKM/issues
- **문서**: [AI4PKM Documentation](../01-AI4PKM_CLI_Structure/)

---

### 팁과 베스트 프랙티스

1. **프롬프트 반복 개선**
   - 에이전트가 원하는 결과를 내지 못하면 프롬프트 수정
   - 예시를 프롬프트에 추가하면 품질 향상

2. **폴더 구조 계획**
   - Ingest: 원시 데이터
   - AI: AI 처리 결과
   - Journal: 수동 노트
   - Projects: 프로젝트별 구조

3. **백업 자동화**
   - Vault를 Git으로 버전 관리
   - 중요한 `orchestrator.yaml`과 프롬프트는 반드시 백업

4. **로그 모니터링**
   ```bash
   tail -f _Settings_/Logs/ai4pkm.log
   ```

5. **태스크 파일 보관**
   - 태스크 파일은 실행 이력을 담고 있음
   - 주기적으로 아카이브 폴더로 이동

---

**문서 버전:** 2025-12-03
**대상 코드 버전:** upstream/main @ 7d205ca
