# Task Management Improvements & Agent Configuration

## Summary

Improves task management system with complete audit trails, flexible agent configuration, and fixes critical timeout issues.

## Key Changes

### 1. ✅ All Tasks Create Task Files
- **Simple tasks**: Execute immediately, set `COMPLETED`/`FAILED` status
- **Complex tasks**: Defer to TaskProcessor with `TBD` status  
- **Exceptions**: Update existing tasks instead of creating new ones (#AI tags, outcome updates)
- **Benefit**: Complete audit trail of all work

### 2. ✅ Remove Hardcoded Agent Configurations
- All agents now respect `default-agent` setting
- Change one setting to affect all agents (generation, processing, evaluation)
- Granular control still available per task type
- **Benefit**: Consistent, flexible agent configuration

### 3. ✅ Fix Agent Timeout (CRITICAL)
- **Problem**: Agents had hardcoded 5-minute timeout, ignoring configured 30 minutes
- **Evidence**: Tasks timing out at 5 min but Codex completing at 30+ min
- **Fix**: Agents now use configured `timeout_minutes` (default 30 min)
- **Benefit**: Long-running tasks (EIC, research) complete successfully

### 4. ✅ Informative Task File Naming
- System prompt now guides descriptive naming
- Example: `2025-10-22 EIC Process Article on AI Agents.md`
- **Benefit**: Easy task identification and history browsing

## Configuration Examples

**Minimal** (use default for everything):
```json
{
  "default-agent": "codex_cli"
}
```

**Granular** (override specific agents):
```json
{
  "default-agent": "codex_cli",
  "task_management": {
    "generation_agent": "claude_code",
    "processing_agent": {
      "EIC": "claude_code"
    },
    "timeout_minutes": 30
  }
}
```

## Files Changed

**Core Configuration**:
- `ai4pkm_cli/config.py` - Remove hardcoded agents, add timeout config
- `ai4pkm_cli/agents/codex_agent.py` - Use configured timeout
- `ai4pkm_cli/agents/gemini_agent.py` - Use configured timeout

**Task Management**:
- `ai4pkm_cli/prompts/task_generation.md` - Simplified prompt, task creation rules
- `_Settings_/Templates/Task Template.md` - Added required fields
- `README_KTG.md` - Updated workflow and execution policy
- `README_KTM.md` - Updated workflow steps

## Impact

**Before**: 
- Simple tasks executed without record 📝❌
- 5-min timeout caused failures ⏱️❌
- Agent config required multiple keys 🔧❌
- Generic task names 📛❌

**After**:
- Complete audit trail ✅
- 30-min timeout for complex tasks ✅
- Single default-agent setting ✅
- Informative task names ✅

## Verification

```bash
# Confirm 30-minute timeout
$ python3 -c "from ai4pkm_cli.config import Config; \
  print(Config().get_agent_config('codex_cli')['timeout_seconds'])"
1800  # 30 minutes in seconds
```

## Commits

1. `701b5ee` - Task file creation improvements
2. `b15af95` - Fix agent timeout (5 min → 30 min)

---

**Status**: ✅ Ready to merge  
**Breaking Changes**: None (backward compatible)  
**Tests**: Manual verification complete
