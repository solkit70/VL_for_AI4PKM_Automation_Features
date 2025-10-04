## Overview
Here's how daily contents are ingested and processed into daily roundup, which is essentially episodic memory for my PKM.

### Process
1. [[Pick and Process Photos (PPP)]]
	- Photos from each day are processed into photo log
	- Photos are ingested from iCloud Photos (via Applescript)
2. [[Process Life Logs (PLL)]] 
	- Voice-based life log (from Limitless.AI) is processed
	- Need to trigger [sync w/  Limitless.AI](https://github.com/Maclean-D/obsidian-limitless-lifelogs) first
3. [[Enrich Ingested Content (EIC)]]
	- Ingested from [Readwise Reader](https://read.readwise.io/new) and [Obsidian Web Clipper](https://obsidian.md/clipper)
	- Skip if already processed within [[Continuous Knowledge Upkeep (CKU)]]
4. [[Generate Daily Roundup (GDR)]]
	- Build episodic knowledge for day
5. [[Topic Knowledge Addendum (TKA)]]
	- Add updates to topic knowledge
6. [[Create Thread Postings (CTP)]]
	- Generate ideas for social media posting

### Guidelines
 - `DIR` can be run multiple times per day, in which case only updated contents will be added to existing notes
![[Daily Roundup 2025-07-20 17.29.29.excalidraw.svg]]
%%[[Daily Roundup 2025-07-20 17.29.29.excalidraw.md|🖋 Edit in Excalidraw]]%%

## Prompts
![[Process Life Logs (PLL)]]

![[Generate Daily Roundup (GDR)]]

![[Topic Knowledge Addendum (TKA)]]
