# Orchestrator 실행 실습

**작성일**: 2025-12-24
**학습 단계**: Day 2, 세션 3
**학습 목표**: Orchestrator를 실제로 실행하고 동작 확인

---

## 1. 실습 환경 확인

### 1.1 가상 환경 활성화

```bash
# AI4PKM 프로젝트 루트로 이동
cd C:/AI_study/PKM_Project/AI4PKM_2/AI4PKM

# 가상 환경 활성화 (Git Bash)
source venv/Scripts/activate

# 또는 (PowerShell)
.\venv\Scripts\activate
```

### 1.2 작업 디렉터리 이동

```bash
# VL_AI4PKM_Automation 폴더로 이동
cd VL_AI4PKM_Automation

# orchestrator.yaml이 있는지 확인
ls orchestrator.yaml
```

**중요**: AI4PKM은 현재 디렉터리에서 `orchestrator.yaml`을 찾으므로, 반드시 해당 폴더에서 명령어를 실행해야 합니다.

---

## 2. 실습 1: Orchestrator 상태 확인

### 2.1 명령어 실행

```bash
ai4pkm --orchestrator-status
```

### 2.2 실행 결과

```
+------------------------ Orchestrator Status ------------------------+
| Vault: C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM\VL_AI4PKM_Automation |
| Agents loaded: 2                                                    |
| Pollers loaded: 0                                                   |
| Max concurrent: 3                                                   |
+---------------------------------------------------------------------+

Available Agents:
  • [EIC] Enrich Ingested Content (EIC)
    Category: learning
  • [CTP] Create Thread Postings (CTP)
    Category: publishing
```

### 2.3 결과 분석

**✅ 정상 동작 확인**:
1. **Vault 경로**: `VL_AI4PKM_Automation` 폴더 인식 성공
2. **Agents loaded: 2**: EIC, CTP 에이전트 로드 성공
3. **Pollers loaded: 0**: Poller 설정 없음 (예상된 결과)
4. **Max concurrent: 3**: 최대 3개 에이전트 동시 실행 가능

**에이전트 정보**:
- **[EIC]**: Enrich Ingested Content - learning 카테고리
- **[CTP]**: Create Thread Postings - publishing 카테고리

**Poller**:
- 현재 orchestrator.yaml에 Poller 설정이 없음
- 필요 시 추가 가능

---

## 3. 실습 2: 설정 파일 확인

### 3.1 명령어 실행

```bash
ai4pkm --show-config
```

### 3.2 예상 결과

```
╭─ Configuration (orchestrator.yaml) ─╮
│ Orchestrator Settings:              │
│   prompts_dir: _Settings_/Prompts   │
│   tasks_dir: _Settings_/Tasks       │
│   logs_dir: _Settings_/Logs         │
│   skills_dir: _Settings_/Skills     │
│   bases_dir: _Settings_/Bases       │
│   max_concurrent: 3                 │
│   poll_interval: 1.0                │
│   executors: {...}                  │
│                                     │
│ Configured Agents: 2                │
│   • Enrich Ingested Content (EIC)   │
│   • Create Thread Postings (CTP)    │
╰─────────────────────────────────────╯
```

### 3.3 핵심 설정 항목

**디렉터리 설정**:
- `prompts_dir`: 프롬프트 파일 위치
- `tasks_dir`: 태스크 파일 저장 위치
- `logs_dir`: 로그 파일 저장 위치

**동시성 제어**:
- `max_concurrent`: 최대 3개 에이전트 동시 실행
- `poll_interval`: 1초마다 이벤트 큐 확인

**Executor**:
- `claude_code`: C:\\Users\\dougg\\AppData\\Roaming\\npm\\claude.cmd
- `gemini`: C:\\Users\\dougg\\AppData\\Roaming\\npm\\gemini.cmd

---

## 4. 실습 3: 에이전트 목록 확인

### 4.1 명령어 실행

```bash
ai4pkm --list-agents
```

### 4.2 예상 결과

```
                            Available Agents
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Abbreviation ┃ Name                          ┃ Category   ┃ Input Path          ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ EIC          │ Enrich Ingested Content (EIC) │ learning   │ vl_ai4pkm_clippings │
│ CTP          │ Create Thread Postings (CTP)  │ publishing │ vl_ai4pkm_materials │
└──────────────┴───────────────────────────────┴────────────┴─────────────────────┘
```

### 4.3 에이전트 상세

**EIC (Enrich Ingested Content)**:
- **Abbreviation**: `eic`
- **Category**: learning
- **Input Path**: `vl_ai4pkm_clippings/`
- **Output Path**: `vl_ai4pkm_materials/`
- **역할**: 웹 클리핑을 enriched content로 변환

**CTP (Create Thread Postings)**:
- **Abbreviation**: `ctp`
- **Category**: publishing
- **Input Path**: `vl_ai4pkm_materials/`
- **Output Path**: `Publish/`
- **역할**: Enriched content를 소셜 미디어 스레드로 변환

---

## 5. Orchestrator 데몬 실행 (이론)

### 5.1 실행 명령어

```bash
# 포어그라운드 실행 (권장)
ai4pkm -o

# 또는 디버그 모드
ai4pkm -o -d
```

### 5.2 예상 실행 흐름

```
1. Orchestrator 시작
   ╭──────────────────────────────────╮
   │ AI4PKM Orchestrator              │
   │ Vault: VL_AI4PKM_Automation      │
   │ Max concurrent: 3                │
   ╰──────────────────────────────────╯

2. 에이전트 로딩
   ✓ Loaded 2 agent(s):
     • [EIC] Enrich Ingested Content (learning)
     • [CTP] Create Thread Postings (publishing)

3. Poller 로딩
   ✓ Loaded 0 poller(s)

4. 이벤트 루프 시작
   [cyan]Starting orchestrator...[/cyan]
   [green]Orchestrator running[/green]

5. 파일 감시 시작
   - FileSystemMonitor 활성화
   - vl_ai4pkm_clippings/ 감시
   - vl_ai4pkm_materials/ 감시

6. 대기 상태
   [Ctrl+C로 종료 가능]
```

### 5.3 동작 확인 방법

**파일 생성 테스트**:
```bash
# 새 터미널에서
echo "# Test Article" > VL_AI4PKM_Automation/vl_ai4pkm_clippings/test.md

# Orchestrator가 감지하고 EIC 에이전트 트리거
# vl_ai4pkm_materials/test_enriched.md 생성
```

**로그 확인**:
```bash
# 로그 디렉터리 확인
ls _Settings_/Logs/

# 최신 로그 조회
tail -f _Settings_/Logs/YYYYMMDD-HHmmss-eic.log
```

---

## 6. 실습 제약사항 및 다음 단계

### 6.1 현재 실습 제약

**Orchestrator 데몬 실행은 생략**:
- 이유: 포어그라운드에서 실행되어 학습 진행 중단
- 대안: 세션 4에서 `-t` (trigger-agent) 옵션으로 수동 실행

### 6.2 다음 실습 (세션 4)

**수동 에이전트 실행**:
```bash
# EIC 에이전트 수동 트리거
ai4pkm -t eic

# 테스트 파일로 워크플로우 확인
```

---

## 7. 주요 학습 포인트

### 7.1 Orchestrator 상태 명령어

| 명령어 | 용도 |
|--------|------|
| `--orchestrator-status` | 현재 상태 조회 |
| `--show-config` | 설정 파일 내용 확인 |
| `--list-agents` | 에이전트 목록 |
| `-o` | Orchestrator 데몬 실행 |
| `-t <agent>` | 에이전트 수동 실행 |

### 7.2 설정 확인 체크리스트

실행 전 확인 사항:
- [ ] `orchestrator.yaml` 파일 존재
- [ ] 프롬프트 파일 생성 완료
- [ ] Executor 경로 설정 (Windows)
- [ ] 작업 디렉터리 올바름
- [ ] 가상 환경 활성화

### 7.3 문제 해결

**"No configuration found"**:
```bash
# 현재 디렉터리 확인
pwd

# orchestrator.yaml 위치 확인
ls orchestrator.yaml

# 올바른 디렉터리로 이동
cd VL_AI4PKM_Automation
```

**"No agents found"**:
```bash
# 프롬프트 파일 확인
ls _Settings_/Prompts/

# orchestrator.yaml의 nodes 섹션 확인
```

---

## 8. 실습 결과 요약

### 8.1 성공적으로 확인한 항목

✅ **Orchestrator 설정 로드**
- orchestrator.yaml 파일 정상 인식
- 설정값 적용 확인

✅ **에이전트 로딩**
- EIC, CTP 에이전트 로드 성공
- 프롬프트 파일 연결 확인

✅ **디렉터리 구조**
- prompts_dir, tasks_dir, logs_dir 설정 확인
- 상대 경로 정상 동작

✅ **Executor 설정**
- Windows 경로 정상 설정
- claude_code, gemini executor 준비

### 8.2 다음 세션 준비 사항

**세션 4 준비**:
1. 테스트 파일 준비
   - `vl_ai4pkm_clippings/test_sample.md`

2. 수동 실행 테스트
   - `ai4pkm -t eic` 명령어 실행
   - 결과 확인 및 분석

---

**학습 완료**: 2025-12-24
**다음 학습**: 수동 에이전트 실행 실습
