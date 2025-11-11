#!/bin/bash
#
# JAX-CTSM Translation Workflow Script
#
# This script runs the complete translation workflow:
# 1. Translate Fortran modules to JAX (translate_with_json.py)
# 2. Generate tests for translated modules (generate_tests.py)
# 3. Run tests and repair failures (repair_agent_example.py)
#
# Usage:
#   ./run_translation_workflow.sh [OPTIONS]
#   ./run_translation_workflow.sh --all
#   ./run_translation_workflow.sh --translate
#   ./run_translation_workflow.sh --test
#   ./run_translation_workflow.sh --repair
#   ./run_translation_workflow.sh --help

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
PROJECT_ROOT="/burg-archive/home/mck2199"
OUTPUT_DIR="$SCRIPT_DIR/translated_modules"
REPAIR_DIR="$SCRIPT_DIR/repair_outputs"

# Modules to process (can be overridden with --modules flag)
DEFAULT_MODULES=("clm_varctl" "SoilStateType" "SoilTemperatureMod")

# Function to print colored output
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
${CYAN}JAX-CTSM Translation Workflow Script${NC}

${YELLOW}Usage:${NC}
  $(basename $0) [OPTIONS]

${YELLOW}Options:${NC}
  --all                Run complete workflow (translate → test → repair)
  --translate          Run translation only
  --test               Run test generation only (requires translated modules)
  --repair             Run repair agent only (requires test failures)
  --interactive        Interactive mode - prompts for each step
  
  --modules MODULES    Comma-separated list of modules (default: clm_varctl,SoilStateType,SoilTemperatureMod)
  --output DIR         Output directory (default: ./translated_modules)
  --skip-tests         Skip test generation
  --auto-repair        Automatically repair if tests fail
  
  -h, --help           Show this help message

${YELLOW}Examples:${NC}
  # Run complete workflow with default modules
  $(basename $0) --all

  # Translate specific modules
  $(basename $0) --translate --modules "clm_varctl,WaterFluxType"

  # Generate tests for already-translated modules
  $(basename $0) --test

  # Interactive mode (prompts for each step)
  $(basename $0) --interactive

  # Translate and auto-repair if tests fail
  $(basename $0) --all --auto-repair

${YELLOW}Workflow Steps:${NC}
  1. ${GREEN}TRANSLATE${NC} - Convert Fortran modules to JAX Python
  2. ${GREEN}TEST${NC}      - Generate comprehensive test suites
  3. ${GREEN}REPAIR${NC}    - Fix any failing tests automatically

${YELLOW}Requirements:${NC}
  - Anthropic API key set: export ANTHROPIC_API_KEY="your-key"
  - Python environment with jax-agents installed
  - JSON analysis files in static_analysis_output/

EOF
}

# Function to check requirements
check_requirements() {
    print_info "Checking requirements..."
    
    # Check Python
    if ! command -v python &> /dev/null; then
        print_error "Python not found. Please install Python 3.9+"
        exit 1
    fi
    
    # Check API key
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        print_warning "ANTHROPIC_API_KEY not set. Some operations may fail."
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check JSON files
    if [ ! -f "static_analysis_output/analysis_results.json" ]; then
        print_error "analysis_results.json not found in static_analysis_output/"
        print_info "Please ensure JSON analysis files are available"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Function to run translation
run_translation() {
    local modules=("$@")
    
    print_header "STEP 1: Translation (Fortran → JAX Python)"
    
    print_info "Translating modules: ${modules[*]}"
    print_info "Output directory: $OUTPUT_DIR"
    echo
    
    # Run translate_with_json.py
    if python examples/translate_with_json.py; then
        print_success "Translation completed successfully"
        
        # List translated modules
        echo
        print_info "Translated modules:"
        for module in "${modules[@]}"; do
            if [ -d "$OUTPUT_DIR/$module" ]; then
                print_success "$module → $OUTPUT_DIR/$module/"
            else
                print_warning "$module - translation may have failed"
            fi
        done
        return 0
    else
        print_error "Translation failed"
        return 1
    fi
}

# Function to generate tests
run_test_generation() {
    print_header "STEP 2: Test Generation"
    
    print_info "Generating tests for all translated modules..."
    echo
    
    # Run generate_tests.py --all
    if python examples/generate_tests.py --all; then
        print_success "Test generation completed successfully"
        
        # List generated tests
        echo
        print_info "Generated test files:"
        find "$OUTPUT_DIR" -name "test_*.py" -type f | while read test_file; do
            print_success "$(basename $(dirname $test_file))/tests/$(basename $test_file)"
        done
        return 0
    else
        print_error "Test generation failed"
        return 1
    fi
}

# Function to run tests and check for failures
run_tests() {
    print_header "Running Tests"
    
    local has_failures=false
    local failed_modules=()
    
    # Find all test files
    test_files=$(find "$OUTPUT_DIR" -name "test_*.py" -type f 2>/dev/null)
    
    if [ -z "$test_files" ]; then
        print_warning "No test files found"
        return 1
    fi
    
    # Run each test file
    while IFS= read -r test_file; do
        module=$(basename $(dirname $(dirname $test_file)))
        print_info "Testing $module..."
        
        # Run pytest and capture output
        test_output_file="${test_file%.py}_output.txt"
        if pytest "$test_file" -v --tb=short > "$test_output_file" 2>&1; then
            print_success "$module - all tests passed"
        else
            print_warning "$module - tests failed"
            has_failures=true
            failed_modules+=("$module:$test_file:$test_output_file")
        fi
    done <<< "$test_files"
    
    # Return failure info
    if [ "$has_failures" = true ]; then
        echo
        print_warning "Some tests failed:"
        for item in "${failed_modules[@]}"; do
            module="${item%%:*}"
            print_error "  - $module"
        done
        
        # Export for use by repair function
        export FAILED_MODULES="${failed_modules[*]}"
        return 1
    else
        print_success "All tests passed!"
        return 0
    fi
}

# Function to run repair agent
run_repair() {
    print_header "STEP 3: Repair Agent"
    
    # Check if we have failed modules from previous run
    if [ -z "$FAILED_MODULES" ]; then
        print_info "Running tests to identify failures..."
        if run_tests; then
            print_success "All tests pass - no repair needed"
            return 0
        fi
    fi
    
    # Parse failed modules
    IFS=' ' read -ra failed_array <<< "$FAILED_MODULES"
    
    if [ ${#failed_array[@]} -eq 0 ]; then
        print_info "No failed tests found - nothing to repair"
        return 0
    fi
    
    print_info "Repairing ${#failed_array[@]} module(s) with failures..."
    echo
    
    # Repair each failed module
    for item in "${failed_array[@]}"; do
        IFS=':' read -r module test_file test_output <<< "$item"
        
        print_info "Repairing $module..."
        
        # Find Fortran reference
        module_dir="$OUTPUT_DIR/$module"
        python_file="$module_dir/${module}.py"
        fortran_ref="$module_dir/tests/FORTRAN_REFERENCE.F90"
        
        # Check if files exist
        if [ ! -f "$python_file" ]; then
            print_warning "Python file not found: $python_file"
            continue
        fi
        
        if [ ! -f "$test_output" ]; then
            print_warning "Test output not found: $test_output"
            continue
        fi
        
        # Use test_SoilTemperatureMod_FAILING.py if available, else use regular test
        if [ -f "$module_dir/tests/test_${module}_FAILING.py" ]; then
            python_file_to_repair="$module_dir/tests/test_${module}_FAILING.py"
        else
            python_file_to_repair="$python_file"
        fi
        
        # Run repair agent
        repair_output="$REPAIR_DIR/${module}"
        mkdir -p "$repair_output"
        
        if [ -f "$fortran_ref" ]; then
            # With Fortran reference
            python examples/repair_agent_example.py \
                --module "$module" \
                --fortran "$fortran_ref" \
                --python "$python_file_to_repair" \
                --test-report "$test_output" \
                --test-file "$test_file" \
                --max-iterations 5 \
                -o "$repair_output"
        else
            # Without Fortran reference (less effective)
            print_warning "No Fortran reference found for $module"
            python examples/repair_agent_example.py \
                --module "$module" \
                --fortran "$python_file" \
                --python "$python_file_to_repair" \
                --test-report "$test_output" \
                --max-iterations 5 \
                -o "$repair_output"
        fi
        
        if [ $? -eq 0 ]; then
            print_success "$module repaired - check $repair_output/"
        else
            print_error "$module repair failed"
        fi
        
        echo
    done
    
    print_success "Repair process completed"
    print_info "Review results in: $REPAIR_DIR/"
}

# Function for interactive mode
interactive_mode() {
    print_header "Interactive Mode"
    
    echo -e "${YELLOW}What would you like to do?${NC}"
    echo "1) Run complete workflow (translate → test → repair)"
    echo "2) Translate modules only"
    echo "3) Generate tests only"
    echo "4) Run tests only"
    echo "5) Repair failed tests"
    echo "6) Exit"
    echo
    read -p "Enter choice [1-6]: " choice
    
    case $choice in
        1)
            print_info "Running complete workflow..."
            check_requirements
            run_translation "${DEFAULT_MODULES[@]}"
            run_test_generation
            run_tests
            read -p "Repair failed tests? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_repair
            fi
            ;;
        2)
            check_requirements
            run_translation "${DEFAULT_MODULES[@]}"
            ;;
        3)
            run_test_generation
            ;;
        4)
            run_tests
            ;;
        5)
            run_repair
            ;;
        6)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Main script logic
main() {
    # Parse command line arguments
    RUN_ALL=false
    RUN_TRANSLATE=false
    RUN_TEST=false
    RUN_REPAIR=false
    INTERACTIVE=false
    AUTO_REPAIR=false
    SKIP_TESTS=false
    MODULES=("${DEFAULT_MODULES[@]}")
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                RUN_ALL=true
                shift
                ;;
            --translate)
                RUN_TRANSLATE=true
                shift
                ;;
            --test)
                RUN_TEST=true
                shift
                ;;
            --repair)
                RUN_REPAIR=true
                shift
                ;;
            --interactive)
                INTERACTIVE=true
                shift
                ;;
            --auto-repair)
                AUTO_REPAIR=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --modules)
                IFS=',' read -ra MODULES <<< "$2"
                shift 2
                ;;
            --output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Show banner
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════╗"
    echo "║  JAX-CTSM Translation Workflow Script ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Interactive mode
    if [ "$INTERACTIVE" = true ]; then
        interactive_mode
        exit 0
    fi
    
    # Run all
    if [ "$RUN_ALL" = true ]; then
        check_requirements
        run_translation "${MODULES[@]}" || exit 1
        
        if [ "$SKIP_TESTS" = false ]; then
            run_test_generation || exit 1
            
            if run_tests; then
                print_success "All tests passed - no repair needed!"
            elif [ "$AUTO_REPAIR" = true ]; then
                run_repair
            else
                print_info "Tests failed. Run with --auto-repair to fix automatically"
                print_info "Or run: $(basename $0) --repair"
            fi
        fi
        exit 0
    fi
    
    # Run individual steps
    if [ "$RUN_TRANSLATE" = true ]; then
        check_requirements
        run_translation "${MODULES[@]}"
        exit 0
    fi
    
    if [ "$RUN_TEST" = true ]; then
        run_test_generation
        exit 0
    fi
    
    if [ "$RUN_REPAIR" = true ]; then
        run_repair
        exit 0
    fi
    
    # No options provided - show usage
    show_usage
}

# Run main function
main "$@"

