---
title: "Next Steps in AI4PKM: Generalized Multi-Agent Architecture"
created: 2025-10-24
status: HISTORICAL
tags:
  - architecture
  - planning
  - multi-agent
author:
  - "[[Claude]]"
related:
  - "[[2025-10-25 Orchestrator Detailed Design]]"
  - "[[2025-11-01 Orchestrator Implementation Spec]]"
---

## Generalized Multi-Agent Architecture
KTM is an multi-agent architecture where multiple agents collaborate using file system as interface. (e.g. Task Processor agent write output file, which Task Evaluation agent take as an input.) We want to take this idea further to build an architecture where 

![[general-agent-archi.png]]

### Agents
Agent takes certain input, process it, and create the output. Depending on a situation, input can be one or multiple files, and the same can be said for the output.

**Input**
Certain change in input file system 
- A new file is created
- Existing file is updated

**Process**
Pre-defined set of actions  
Roughly equivalent to existing [[Prompts]]

**Output**
Output file or files with certain specification 

### Skills
Extract the reusable skills from existing prompts. Load skills as needed for prompt execution. 

**도메인별 특화 스킬:**
- 📥 **컨텐츠 수집**: Clippings, Limitless, Photolog 처리
- 📤 **퍼블리싱**: Substack, Thread, LinkedIn 채널별 포맷
- 🗂️ **지식 조직화**: Topic 업데이트, Wiki 링크 검증
- 📝 **Obsidian 규칙**: 링크 포맷, 폴더 구조, Property 표준

### Orchestrator
Orchestrator manage task-level agents  to accomplish goals. Orchestrator also interact with user for status reporting and planning improvements.

**Task Management** 
Orchestrator monitor the file system and spawn one or more agents to process the task. Orchestrator also check the output of the task and determine whether it's completed or needs more work. 

**User Interaction**
Orchestrator is also interact with user to notify the completion of a task and collect feedback if needed. 

**Process Improvement**
Orchestrator also perform routine status report where the issues are diagnosed.
Use these results to improve the agent and skill definition over time.

### Configurable Repo
Repo will be simplified to contain only
- Agent Definitions
	- Input/Output location needed to be created
- Skill Definitions
- Templates (use existing if needed)
- Global Agent Rule files

At installation, users can select which agents they like to use, and input/output locations

