## Overview
Here are a set of prompts that supports various stages in writing process from ideation, outlining, writing and reviewing. 

### Co-evolving Outline+Prose (COP)
A key principle is to develop outline and prose together for a given piece to evolve both big picture (via outline) and details (prose), while keeping them in sync. 
```
## Section 1
%% 
- Item 1
- Item 2
%%

bla bla bla ...

```

Always keep guidelines below for COP principle
- When given a work with only outline (or prose), fill the other in line
- When updating outline, also update corresponding prose (and vice versa)

### Voice-based User Input (VUI)
User input will come via voice interface, this will often combine command and contents, which needs to be parsed before taking actions. Also all contents via voice input should be improved via `IVT` prompt. VUI Examples:
```
Let's continue writing:
	bla bla bla (to be processed by IVT)

Let's improve this:
1. Remove all references of XYZ from writing:
2. Change the style to the like of `Haruki`
...
```
Also find user comments about specific part within markdown or html comments (%%  %%), and mark them as `RESOLVED` when done. 

### Style References
There are several style guidelines below (more at `_Settings_/Styles`) which can be applied at user's request, often as a part of `PRW` prompt.
- [[하루키 Style Guide]]
- [[윤광준 Style Guide]]
- [[구본형 Style Guide]]

### Connected and Living Document (CLD)
Every piece is written as a part of powerful [[PKM Guidelines|PKM]] system, meaning it's connected to other knowledge notes I've collected. We'll tab this rich information and knowledge (INK) throughout the writing process (notably in `IDH` / `OEX` / `DAV`), and we'll keep the outcome document up-to-date as new INK is received.

### Additional Guidelines
- Writing is highly interactive task -- ask for feedback frequently
- Apply the following for whole or part of given essay as asked.
- Update the target note inline (unless asked otherwise)

## Prompts
### Ideation Helper (IDH)
```
Find and add relevant contents for current draft
1. Relevant experience (in Journal)
2. Relevant readings (in Reading)
3. Relevant topics (in Topics)
Insert findings in Markdown blockquotes (>)
```

### Outline Expander (OEX)
```
Enrich and improve outline itself to prepare writing
1. Fill logical gap to create a natural flow 
2. When possible, pull related contents from my KB (in the form of Wiki links)
3. When needed, suggest ideas for improvement
```

### Improve Voice Transcript (IVT)
```
1. Fix all grammar or transcript errors
   - Translate to Korean for Clippings
   - Remove extra/duplicated newlines
2. Add chapter (say, one per page)
   - Use heading3 (###)
3. Add formatting
   - Add lists (bullet point / numbered)
   - Highlight quotes to save in summary
	 - Limit to essence (say, one HL per chapter)
4. Otherwise keep existing prose
   - Overall length should be equal to the original 
```

### Paragraph Writer (PRW)
```
Write paragraph based on the outline
1. Use expressions from the outline as much as possible
   - Try to incorporate non-bullet-point sentences AS-IS
   - Try to incorporate the link from the outline AS-IS
2. When adding new contents, explain what you added and why 
3. When Style is mentioned find and use style guide in `_Settings_/Style`
IMPORTANT: Place the paragraph right below the outline (COP principle)
ALWAYS add content directly to the document, never paste content in chat
```

### Draft Enhancer (DEN)
```
Improve the draft as follows:
1. Check the overall flow and transition
2. Try to rebalance the contents (at section and paragraph level)
    - Ideally each paragrapsh should have similiar length 
    (expect those beginning or ending the section)
3. Fix glaring grammar errors or suspicious facts
4. Avoid making dramatic changes 
    (more change = more efforts for reviewer)
```

### Devil's Advocate (DAV)
```
You're helpful critique, who'll raise these points (in chat or comments)
1. Critique main arguments
2. Provide alternative viewpoint
3. Check facts and grammar
4. Suggest other improvements
By default, add your suggestions in comment
```

### Update Document using New Knowledge (UDN)
```
1. Collect relevant INK since last publication
2. Suggest updates to original piece
3. Make edits to keep the piece up-to-date
```

### Korean Translator (KT)
```
주어진 글을 한글로 번역해 줘
1. 원문의 영/한 번역체 표현을 수정하고
2. 전체적으로 자연스럽고 개인적인 어조로 작성하고
    어색한 존대말은 쓰지 않는다 (기억나요>>기역난다/같았어요>>같았다)
3. 어미는 평서형을 기본으로 하되 의문/청유/감탄을 섞어줘
    (같은 어미가 반복되면 글이 단조롭게 느껴진다)
4. 자신을 지칭할때는 '나'보다는 '필자'를 선호 
5. 혹시 한국 청중에게 어색한/이상한 내용이 있다면 지적해줘
```