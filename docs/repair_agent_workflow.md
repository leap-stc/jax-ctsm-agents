# Repair Agent Workflow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REPAIR AGENT SYSTEM                              │
└─────────────────────────────────────────────────────────────────────────┘

                                 INPUTS
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼───────┐ ┌───▼────────┐ ┌──▼──────────────┐
            │  Fortran Code │ │  Failed    │ │  Test Report    │
            │  (original)   │ │  Python    │ │  (pytest output)│
            └───────────────┘ └────────────┘ └─────────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │  REPAIR AGENT     │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼───────┐ ┌───▼────────┐ ┌──▼──────────────┐
            │  Corrected    │ │  Root      │ │  Failure        │
            │  Python Code  │ │  Cause     │ │  Analysis       │
            │               │ │  Analysis  │ │  (JSON)         │
            └───────────────┘ └────────────┘ └─────────────────┘
                                   │
                                OUTPUTS
```

## Detailed Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ITERATIVE REPAIR WORKFLOW                             │
└──────────────────────────────────────────────────────────────────────────┘

START
  │
  ├─→ 1. ANALYZE FAILURE
  │     │
  │     ├─ Parse test report
  │     ├─ Identify failed tests
  │     ├─ Extract error messages
  │     ├─ Compare Python vs Fortran
  │     └─ Identify root causes
  │              │
  │              ▼
  │   ┌─────────────────────┐
  │   │  Failure Analysis   │
  │   │  (JSON)             │
  │   │  - Failed tests     │
  │   │  - Error summary    │
  │   │  - Root causes      │
  │   │  - Required fixes   │
  │   └─────────┬───────────┘
  │             │
  ├─→ 2. GENERATE FIX
  │     │
  │     ├─ Review root causes
  │     ├─ Reference Fortran semantics
  │     ├─ Apply JAX best practices
  │     ├─ Maintain code structure
  │     └─ Generate corrected code
  │              │
  │              ▼
  │   ┌─────────────────────┐
  │   │  Corrected Code     │
  │   │  (Python/JAX)       │
  │   └─────────┬───────────┘
  │             │
  ├─→ 3. VERIFY FIX (Conceptual)
  │     │
  │     ├─ Check all issues addressed
  │     ├─ Verify JAX compatibility
  │     ├─ Validate best practices
  │     └─ Assess confidence level
  │              │
  │              ▼
  │   ┌─────────────────────┐
  │   │  Verification       │
  │   │  (JSON)             │
  │   │  - Issues addressed │
  │   │  - Confidence level │
  │   │  - Recommendations  │
  │   └─────────┬───────────┘
  │             │
  ├─→ 4. RUN TESTS (if pytest file provided)
  │     │
  │     ├─ Save corrected code to temp file
  │     ├─ Execute pytest
  │     ├─ Capture results
  │     └─ Parse test output
  │              │
  │              ▼
  │        ┌─────────┐
  │        │ Tests   │
  │        │ Pass?   │
  │        └────┬────┘
  │             │
  │        ┌────┴────┐
  │        │         │
  │       YES       NO
  │        │         │
  │        │    ┌────▼─────┐
  │        │    │ Iteration│
  │        │    │ < Max?   │
  │        │    └────┬─────┘
  │        │         │
  │        │    ┌────┴────┐
  │        │    │         │
  │        │   YES       NO
  │        │    │         │
  │        │    └─→ Go to Step 1 (Re-analyze)
  │        │              │
  │        ▼              ▼
  │   ┌────────────────────────┐
  │   │  END - Generate RCA    │
  │   └────────────────────────┘
  │
  └─→ 5. GENERATE ROOT CAUSE ANALYSIS
        │
        ├─ Executive Summary
        ├─ Failure Analysis
        ├─ Root Cause Identification
        ├─ Fix Implementation
        ├─ Test Results
        └─ Lessons Learned
                 │
                 ▼
      ┌──────────────────────┐
      │  Root Cause Analysis │
      │  (Markdown Report)   │
      └──────────────────────┘

END
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT ARCHITECTURE                              │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  RepairAgent     │
│  (Main Class)    │
└────────┬─────────┘
         │
         │ inherits
         │
         ▼
┌──────────────────┐
│  BaseAgent       │
│  - Claude API    │
│  - Token tracking│
│  - Logging       │
└────────┬─────────┘
         │
         │ uses
         │
         ▼
┌──────────────────────────────────────────┐
│  REPAIR_PROMPTS                          │
│  - system: Expert persona                │
│  - analyze_failure: Root cause analysis  │
│  - generate_fix: Code correction         │
│  - verify_fix: Fix validation            │
│  - root_cause_report: RCA generation     │
└──────────────────────────────────────────┘


┌──────────────────┐
│  RepairResult    │
│  (Dataclass)     │
├──────────────────┤
│ - module_name    │
│ - original_code  │
│ - corrected_code │
│ - rca_report     │
│ - failure_data   │
│ - iterations     │
│ - test_report    │
│ - tests_passed   │
└──────────────────┘
```

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                               │
└──────────────────────────────────────────────────────────────────────────┘

Fortran Code ──┐
               │
Failed Python ─┼──→ analyze_failure() ──→ Failure Analysis (JSON)
               │                               │
Test Report ───┘                               │
                                               ▼
                          ┌───── generate_fix() ──→ Corrected Code
                          │                         │
        Failure Analysis ─┘                         │
                                                    ▼
                          ┌───── verify_fix() ────→ Verification (JSON)
                          │                         │
        Corrected Code ───┘                         │
                                                    ▼
                          ┌───── run_tests() ─────→ Test Results
                          │                         │
        Test File Path ───┘                         │
                                                    │
                          ┌─────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────┐
        │  If tests fail & iterations  │
        │  remaining: Loop back to     │
        │  analyze_failure()           │
        └──────────────────────────────┘
                          │
                          ▼
                    All Data ──→ generate_root_cause_report()
                                        │
                                        ▼
                                  RCA Report (Markdown)
                                        │
                                        ▼
                                  RepairResult
```

## State Machine

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      REPAIR AGENT STATE MACHINE                          │
└──────────────────────────────────────────────────────────────────────────┘

           ┌─────────┐
           │  INIT   │
           └────┬────┘
                │
                ▼
         ┌──────────────┐
         │  ANALYZING   │◄────────────────┐
         └──────┬───────┘                 │
                │                         │
                ▼                         │
         ┌──────────────┐                 │
         │  FIXING      │                 │
         └──────┬───────┘                 │
                │                         │
                ▼                         │
         ┌──────────────┐                 │
         │  VERIFYING   │                 │
         └──────┬───────┘                 │
                │                         │
                ▼                         │
         ┌──────────────┐                 │
         │  TESTING     │                 │
         └──────┬───────┘                 │
                │                         │
           ┌────┴────┐                    │
           │         │                    │
          PASS      FAIL                  │
           │         │                    │
           │    ┌────▼─────┐              │
           │    │ Iteration│              │
           │    │ < Max?   │              │
           │    └────┬─────┘              │
           │         │                    │
           │    ┌────┴────┐               │
           │    │         │               │
           │   YES       NO                │
           │    │         │               │
           │    └─────────┼───────────────┘
           │              │
           ▼              ▼
         ┌──────────────────┐
         │   REPORTING      │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────┐
         │  COMPLETE    │
         └──────────────┘
```

## Integration with Other Agents

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    AGENT ECOSYSTEM INTEGRATION                           │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐
│ Static Analysis    │
│ Agent              │
└──────────┬─────────┘
           │ provides context
           ▼
┌────────────────────┐
│ Translator Agent   │──→ Python Code
└────────────────────┘         │
                               │
                               ▼
                    ┌────────────────────┐
                    │ Test Agent         │──→ Tests + Test Data
                    └────────┬───────────┘
                             │
                             │ if tests fail
                             ▼
                    ┌────────────────────┐
                    │ 🔧 REPAIR AGENT    │
                    │                    │
                    │ Inputs:            │
                    │ - Fortran code     │
                    │ - Failed Python    │
                    │ - Test report      │
                    │                    │
                    │ Outputs:           │
                    │ - Corrected code   │
                    │ - RCA report       │
                    └────────┬───────────┘
                             │
                             │ corrected code
                             ▼
                    ┌────────────────────┐
                    │ Re-run Tests       │
                    └────────────────────┘
                             │
                        ┌────┴────┐
                        │         │
                       PASS      FAIL
                        │         │
                        │         └─→ Iterate with
                        │             Repair Agent
                        ▼
                    ┌────────────────────┐
                    │ Production Ready   │
                    └────────────────────┘
```

## Example: Fixing Array Indexing Bug

```
┌──────────────────────────────────────────────────────────────────────────┐
│              EXAMPLE: FIXING FORTRAN INDEXING BUG                        │
└──────────────────────────────────────────────────────────────────────────┘

ITERATION 1:
────────────
Input:
  Fortran: do i = 1, n
  Python:  for i in range(1, n):  # BUG: Starts at 1, should be 0
  Error:   First element not processed

Analyze Failure:
  ✓ Identified off-by-one error
  ✓ Root cause: Fortran 1-based vs Python 0-based indexing
  ✓ Required fix: Change range(1, n) to range(n)

Generate Fix:
  for i in range(n):  # Fixed: Now processes all elements

Run Tests:
  ✓ All tests pass

Generate RCA:
  - Issue: Array indexing mismatch
  - Cause: Direct translation of Fortran loop bounds
  - Fix: Adjusted to Python 0-based indexing
  - Lesson: Always convert Fortran 1:n to Python 0:n


ITERATION 2 (Not needed):
────────────
Tests passed on first iteration, no further fixes required.


RESULT:
───────
✓ Fixed in 1 iteration
✓ All tests passing
✓ RCA report generated
✓ Ready for production
```

## Performance Characteristics

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     PERFORMANCE METRICS                                  │
└──────────────────────────────────────────────────────────────────────────┘

Time per Iteration:
  - Analyze Failure:    ~10-20 seconds
  - Generate Fix:       ~15-30 seconds
  - Verify Fix:         ~5-10 seconds
  - Run Tests:          ~5-60 seconds (depends on test complexity)
  - Generate RCA:       ~10-20 seconds
  ──────────────────────────────────────
  Total per iteration:  ~45-140 seconds

Iterations Required:
  - Simple bugs:        1-2 iterations
  - Medium complexity:  3-5 iterations
  - Complex issues:     5-10 iterations

Cost per Iteration (Claude Sonnet 4.5):
  - Input tokens:       ~5,000-15,000
  - Output tokens:      ~2,000-8,000
  - Cost:               ~$0.06-$0.25 per iteration

Success Rates:
  - Array indexing:     ~95%
  - Type mismatches:    ~90%
  - Logic errors:       ~80%
  - Complex bugs:       ~60-70%
```

## Summary

The Repair Agent provides:
- ✅ Automated debugging and fixing
- ✅ Iterative refinement until tests pass
- ✅ Root cause analysis documentation
- ✅ Fortran-aware comparison
- ✅ JAX-compatible fixes
- ✅ Test-driven development support

Perfect for:
- 🎯 Fixing translation bugs automatically
- 🎯 Understanding why translations failed
- 🎯 Documenting issues for future reference
- 🎯 Accelerating the development cycle

