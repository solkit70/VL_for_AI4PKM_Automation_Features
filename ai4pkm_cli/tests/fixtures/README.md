# Test Fixtures

This folder contains test data files used by the integration tests.

## Files

### test_clipping_template.md

Template for test clipping files used in the EIC integration test.

**Purpose**: 
- Provides a realistic clipping file format
- Easy to edit for different test scenarios
- Intentionally minimal to ensure quick processing

**Key Features**:
- No Summary section (requires EIC processing)
- Simple frontmatter with required fields
- Short content for fast processing
- Includes blockquotes for testing quote extraction

**Usage**:
Used by `test_ktg_ktp_eic_integration.py` when creating test clipping files.

**Editing**:
You can modify this file to test different scenarios:
- Add/remove sections to test different EIC paths
- Change content length to test performance
- Modify tags to test categorization
- Add complexity to test edge cases

**Note**: Keep content short to ensure tests run quickly (<60s total).
