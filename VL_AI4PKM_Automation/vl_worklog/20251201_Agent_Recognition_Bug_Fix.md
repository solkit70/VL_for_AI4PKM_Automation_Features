# WorkLog: Windows 환경 AI 에이전트 인식 문제 해결

**날짜**: 2025-12-01
**작업자**: ChangSoo (with Claude Code)
**환경**: Windows 11, Python 3.13.3, PowerShell
**작업 유형**: 버그 수정 및 크로스 플랫폼 호환성 개선

**유튜브 라이브 영상**: [재미로 하는 Vibe Coding 번외편 - 첫번째 실습시간 입니다. 처음 오신 분도 따라 할 수 있도록 설치부터 실행까지 입문 끝](https://youtube.com/live/eafzMCl87oM)

---

## 📋 작업 요약

이전 세션에서 발견된 AI 에이전트 인식 문제를 해결하고, 상세한 피드백 문서를 작성하여 GitHub에 push했습니다.

**핵심 성과**:
- ✅ Windows 환경에서 AI 에이전트가 인식되지 않던 3개의 버그 수정
- ✅ 크로스 플랫폼(Mac/Windows) 차이점 분석 문서 작성
- ✅ 개발자를 위한 상세한 피드백 문서 완성
- ✅ 모든 변경사항 GitHub에 commit 및 push 완료

---

## 🐛 발견된 문제

### 초기 증상

```powershell
PS C:\AI_study\PKM_Project\AI4PKM_2\AI4PKM> ai4pkm --list-agents

[2025-12-01 10:53:19] WARNING: Could not find claude in PATH: [WinError 2]
Available AI Agents:
🔥 claude_code: Claude Code - ❌ Not Available
   gemini_cli: Gemini CLI - ❌ Not Available
   codex_cli: Codex CLI - ❌ Not Available
```

**문제점**:
- Claude Code와 Gemini CLI가 시스템에 설치되어 있음에도 인식하지 못함
- 직접 실행하면 정상 작동하는 것 확인됨:
  ```powershell
  C:\Users\dougg\AppData\Roaming\npm\claude.cmd --version  # 정상
  C:\Users\dougg\AppData\Roaming\npm\gemini.cmd --version  # 0.18.4
  ```

---

## 🔍 근본 원인 분석

### 버그 1: `agent_factory.py` - 빈 설정 객체 전달 (치명적)

**위치**: `ai4pkm_cli/agent_factory.py:114-138`

**문제**:
```python
# ❌ 잘못된 코드
for agent_type, agent_class in cls.AGENT_CLASSES.items():
    temp_config = {}  # 빈 설정!
    agent = agent_class(logger, temp_config)
```

**결과**:
- 설정 파일(`ai4pkm_cli.json`)의 내용이 에이전트에 전달되지 않음
- 에이전트들이 설정 파일의 `command` 경로를 찾지 못함

**수정**:
```python
# ✅ 올바른 코드
config = Config()  # 실제 설정 파일 로드
for agent_type, agent_class in cls.AGENT_CLASSES.items():
    agent_config = config.get_agent_config(agent_type)
    agent = agent_class(logger, agent_config)
```

### 버그 2: `claude_agent.py` - 설정 파일 무시 & Unix 명령어 사용

**위치**: `ai4pkm_cli/agents/claude_agent.py:19-48`

**문제**:
1. 설정 파일의 `command` 필드를 확인하지 않음
2. Unix/Linux 명령어 `which` 사용 (Windows는 `where` 필요)
3. Unix 경로만 확인 (`/usr/local/bin/claude`)

**수정**:
```python
# ✅ 설정 파일 우선 확인
if self.config and "command" in self.config:
    cmd_path = self.config["command"]
    if Path(cmd_path).exists():
        return cmd_path

# ✅ Windows/Unix 환경 구분
cmd = "where" if os.name == "nt" else "which"
result = subprocess.run([cmd, "claude"], ...)
```

### 버그 3: `gemini_agent.py` - Windows .cmd 파일 실행 실패

**위치**: `ai4pkm_cli/agents/gemini_agent.py:19-30`

**문제**:
- Windows에서 `.cmd` 파일 실행 시 `shell=True` 옵션 필요
- 이 옵션 없이 실행하면 `FileNotFoundError` 발생

**수정**:
```python
# ✅ Windows .cmd 파일 처리
use_shell = os.name == 'nt' and self.command.endswith('.cmd')
result = subprocess.run([self.command, '--version'],
                       capture_output=True, text=True,
                       timeout=10, shell=use_shell)
```

---

## 🔧 수정한 파일

### 1. `ai4pkm_cli/agent_factory.py`
- **변경 내용**: 빈 설정 대신 실제 `Config()` 로드
- **영향**: 모든 에이전트가 설정 파일의 경로를 받을 수 있게 됨
- **중요도**: ⭐⭐⭐ (치명적 버그 수정)

### 2. `ai4pkm_cli/agents/claude_agent.py`
- **변경 내용**:
  - 설정 파일 `command` 필드 우선 확인
  - Windows `where` 명령어 지원
  - `.cmd` 파일 확장자 처리
- **중요도**: ⭐⭐⭐ (Windows 지원 추가)

### 3. `ai4pkm_cli/agents/gemini_agent.py`
- **변경 내용**:
  - Windows `.cmd` 파일에 `shell=True` 추가
  - 디버그 로깅 추가
  - 구체적인 예외 메시지
- **중요도**: ⭐⭐⭐ (Windows 지원 추가)

### 4. `ai4pkm_vault/ai4pkm_cli.json`
- **변경 내용**: Windows 전체 경로 추가
  ```json
  {
    "claude_code": {
      "command": "C:\\Users\\dougg\\AppData\\Roaming\\npm\\claude.cmd"
    },
    "gemini_cli": {
      "command": "C:\\Users\\dougg\\AppData\\Roaming\\npm\\gemini.cmd"
    }
  }
  ```

### 5. `AI4PKM_Onboarding_feedback.md`
- **변경 내용**: 섹션 4 추가 (약 635줄)
  - 문제 설명 및 재현 방법
  - 3개 버그의 근본 원인 분석
  - 코드 비교 (Before/After)
  - 문제 발견 과정 (6단계)
  - 개선 제안 (6개 우선순위)
  - **크로스 플랫폼 분석** (Mac vs Windows)
- **중요도**: ⭐⭐⭐ (개발자 피드백)

---

## 🌍 크로스 플랫폼 분석: Mac vs Windows

### 왜 Mac 개발자는 이 문제를 발견하지 못했을까?

#### Mac/Linux 환경
✅ **npm 설치 시**:
- 자동으로 `/usr/local/bin`에 설치
- 이 경로는 기본적으로 PATH에 포함됨
- `which claude` 명령어 정상 작동

✅ **파일 형식**:
- 실행 파일 형식: `claude` (직접 실행 가능)
- `.cmd` 확장자 없음
- `shell=True` 불필요

✅ **결과**: 모든 것이 자동으로 작동

#### Windows 환경
❌ **npm 설치 시**:
- `C:\Users\사용자명\AppData\Roaming\npm\`에 설치
- PATH에 자동으로 추가되지 않을 수 있음
- `which` 명령어 없음 (대신 `where` 사용)

❌ **파일 형식**:
- 실행 파일 형식: `claude.cmd` (배치 파일)
- `.cmd` 파일은 `shell=True` 필요
- Python `subprocess.run()`에서 직접 실행 불가

❌ **결과**: 수동 설정 필요

### 플랫폼별 차이 비교표

| 항목 | Mac/Linux | Windows |
|------|-----------|---------|
| **npm 글로벌 경로** | `/usr/local/bin` | `C:\Users\...\AppData\Roaming\npm` |
| **PATH 자동 설정** | ✅ 자동 | ⚠️ 수동 필요 |
| **실행 파일 형식** | `claude` | `claude.cmd` |
| **PATH 검색 명령어** | `which` | `where` |
| **subprocess 실행** | `shell=False` OK | `.cmd`는 `shell=True` 필수 |

### 교훈

**이 문제는 전형적인 크로스 플랫폼 호환성 이슈입니다**:
- Mac에서 잘 작동한다고 모든 플랫폼에서 작동하는 것은 아님
- 플랫폼별 차이점을 명시적으로 처리해야 함
- CI/CD에 Windows 환경 테스트 필수

---

## 📝 문제 해결 과정

### 1단계: 초기 증상 확인
```powershell
ai4pkm --list-agents
# 결과: 모든 에이전트 "Not Available"
```

### 2단계: 에이전트 직접 테스트
```powershell
C:\Users\dougg\AppData\Roaming\npm\claude.cmd --version  # 작동함!
C:\Users\dougg\AppData\Roaming\npm\gemini.cmd --version  # 0.18.4
```
→ 에이전트는 설치되어 있음. 코드 문제로 판단.

### 3단계: 설정 파일에 전체 경로 추가
```json
{
  "claude_code": {
    "command": "C:\\Users\\dougg\\AppData\\Roaming\\npm\\claude.cmd"
  }
}
```
→ 여전히 작동하지 않음!

### 4단계: 디버그 로깅 추가
```python
self.logger.debug(f"Checking Gemini CLI: command={self.command}")
```
출력:
```
[DEBUG] command=gemini  # ← 전체 경로가 아닌 기본값!
```
→ 설정 파일이 읽히지 않고 있음을 발견!

### 5단계: `agent_factory.py` 코드 확인
```python
temp_config = {}  # ← 여기가 문제!
```
→ 빈 설정 객체를 전달하고 있었음!

### 6단계: 모든 버그 수정 및 검증
```powershell
pip install -e . --force-reinstall --no-deps
ai4pkm --list-agents

# 결과:
Available AI Agents:
🔥 claude_code: Claude Code - ✅ Available
   gemini_cli: Gemini CLI - ✅ Available
   codex_cli: Codex CLI - ❌ Not Available
```
→ **성공!** ✅

---

## 💡 학습한 교훈

### 1. 설정 파일의 중요성
- 사용자가 설정 파일에 경로를 지정해도 코드가 읽지 않으면 무의미
- **설정 파일의 값을 최우선으로 사용**해야 함

### 2. 크로스 플랫폼 개발
- Mac에서 개발하면 Windows 문제를 놓치기 쉬움
- 플랫폼별 차이점을 명시적으로 처리 필요
- CI/CD에 다중 플랫폼 테스트 포함 필수

### 3. 디버깅의 중요성
- 적절한 로깅 없이는 문제 원인 파악 어려움
- "Not Available"만 표시하지 말고 **구체적인 이유** 제공해야 함

### 4. 신규 사용자 경험
- `--list-agents`는 초기 확인 명령어 중 하나
- 모든 에이전트가 "Not Available"이면 사용자는 매우 혼란스러움
- **온보딩 경험**이 프로젝트 성공에 중요

---

## 🚀 GitHub Commit 및 Push

### Commit 정보
```bash
Commit ID: 3a91cea
Message: fix: Resolve Windows agent recognition issues and add comprehensive feedback
```

### 변경 파일 목록
1. `ai4pkm_cli/agent_factory.py` - 실제 Config() 로드
2. `ai4pkm_cli/agents/claude_agent.py` - 설정 우선, Windows 지원
3. `ai4pkm_cli/agents/gemini_agent.py` - .cmd 파일 처리
4. `ai4pkm_vault/ai4pkm_cli.json` - Windows 경로 추가
5. `AI4PKM_Onboarding_feedback.md` - 상세 피드백 문서 (635줄 추가)

### Push 결과
```bash
To https://github.com/solkit70/VL_for_AI4PKM_Automation_Features.git
   cfa8550..3a91cea  main -> main
```

---

## 📊 작업 통계

- **수정한 코드 파일**: 3개
- **수정한 설정 파일**: 1개
- **추가한 문서**: 635줄 (AI4PKM_Onboarding_feedback.md)
- **발견한 버그**: 3개 (모두 수정 완료)
- **작업 시간**: 약 2시간
- **Git Commit**: 1개
- **Git Push**: 성공

---

## 🎯 AI4PKM 개발자를 위한 권장사항

### 우선순위 높음 (⭐⭐⭐)
1. ✅ **설정 파일 command 필드 우선 사용** → 완료
2. ✅ **Windows 환경 지원** (.cmd, where) → 완료
3. ✅ **agent_factory 빈 설정 버그 수정** → 완료

### 우선순위 중간 (⭐⭐)
4. ⚠️ **에러 메시지 개선** → 부분 완료 (더 개선 필요)
5. ❌ **설정 파일 가이드 문서화** → 필요
6. ❌ **`--check-agents` 명령어 추가** → 제안

### 우선순위 낮음 (⭐)
7. ❌ **플랫폼별 단위 테스트** → 필요
8. ❌ **CI/CD에 Windows 환경 추가** → 필요

---

## 📚 참고 자료

- **피드백 문서**: [AI4PKM_Onboarding_feedback.md](../AI4PKM_Onboarding_feedback.md) 섹션 4
- **수정된 코드**:
  - [agent_factory.py:114-141](../ai4pkm_cli/agent_factory.py#L114-L141)
  - [claude_agent.py](../ai4pkm_cli/agents/claude_agent.py)
  - [gemini_agent.py](../ai4pkm_cli/agents/gemini_agent.py)
- **설정 파일**: [ai4pkm_cli.json](../ai4pkm_vault/ai4pkm_cli.json)

---

## ✅ 다음 단계

1. **AI4PKM 개발팀에 피드백 전달**
   - GitHub Issue 생성 또는 Pull Request
   - 피드백 문서 공유

2. **Windows 환경 추가 테스트**
   - 다른 Windows 버전에서 테스트
   - PowerShell vs CMD 환경 차이 확인

3. **사용자 가이드 보완**
   - Windows 사용자를 위한 설치 가이드 작성
   - 설정 파일 작성 예제 추가

4. **다음 학습 단계 진행**
   - AI4PKM CLI 기본 명령어 실습
   - 에이전트를 활용한 프롬프트 실행 테스트

---

**작업 완료**: 2025-12-01
**상태**: ✅ 성공적으로 완료
**다음 세션**: AI4PKM CLI 명령어 실습 예정
