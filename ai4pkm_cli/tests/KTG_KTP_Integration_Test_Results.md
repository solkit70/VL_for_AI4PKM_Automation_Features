# KTG/KTP/KTE Integration Test Results

Generated: 2025-10-17 21:23:43


================================================================================
KTG/KTP/KTE INTEGRATION TEST RESULTS
================================================================================

Test Start: 2025-10-17 21:18:03
Test End:   2025-10-17 21:23:43
Duration:   339.5s

Overall Result: ✗ FAILED

================================================================================
STAGE RESULTS
================================================================================

WATCHDOG_STARTED: ✓ PASSED

CLIPPING_CREATED: ✓ PASSED
  File: /Users/lifidea/dev/AI4PKM/Ingest/Clippings/2025-10-17 Test Integration Article 2025-10-17-211803.md

TASK_REQUEST_CREATED: ✓ PASSED
  Time: 0.0s
  File: /Users/lifidea/dev/AI4PKM/AI/Tasks/Requests/Clipping/2025-10-17-1760761094775.json

TASK_CREATED: ✓ PASSED
  Time: 26.1s
  File: /Users/lifidea/dev/AI4PKM/AI/Tasks/2025-10-17 EIC - Test Integration Article.md

TASK_PROCESSING: ✗ FAILED
  Status transitions:
    - TBD at 0.0s

================================================================================
ISSUES FOUND (2)
================================================================================
1. Task missing properties: ['priority', 'source']
2. Task timeout after 300s, status: TBD

================================================================================
