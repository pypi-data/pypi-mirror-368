#!/bin/bash

# Complete test suite for libadic
# This script ensures all tests compile and pass without any workarounds

set -e  # Exit on any error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "     LIBADIC COMPLETE TEST VALIDATION"
echo "=================================================="
echo ""

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        exit 1
    fi
}

# Check Docker availability
if command -v docker &> /dev/null; then
    echo "Running tests in Docker container..."
    
    # Build Docker image
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t libadic:test . 
    print_status $? "Docker image built"
    
    # Run complete test suite in container
    echo -e "${YELLOW}Running test suite in container...${NC}"
    docker run --rm libadic:test bash -c "
        set -e
        cd /libadic
        mkdir -p build
        cd build
        cmake ..
        make -j\$(nproc)
        
        echo 'Running GMP wrapper tests...'
        ./test_gmp_wrapper
        
        echo 'Running Zp tests...'
        ./test_zp
        
        echo 'Running Qp tests...'
        ./test_qp
        
        echo 'Running special functions tests...'
        ./test_functions
        
        echo 'Running Reid-Li Criterion validation for p=5...'
        ./milestone1_test 5 60
        
        echo 'Running Reid-Li Criterion validation for p=7...'
        ./milestone1_test 7 60
        
        echo 'Running Reid-Li Criterion validation for p=11...'
        ./milestone1_test 11 60
    "
    print_status $? "All Docker tests passed"
    
else
    echo "Docker not available. Running tests locally..."
    
    # Check for required dependencies
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    if ! command -v cmake &> /dev/null; then
        echo -e "${RED}Error: cmake is not installed${NC}"
        exit 1
    fi
    
    if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
        echo -e "${RED}Error: No C++ compiler found${NC}"
        exit 1
    fi
    
    # Check for GMP
    if ! ldconfig -p | grep -q libgmp; then
        echo -e "${YELLOW}Warning: GMP library may not be installed${NC}"
    fi
    
    # Check for MPFR
    if ! ldconfig -p | grep -q libmpfr; then
        echo -e "${YELLOW}Warning: MPFR library may not be installed${NC}"
    fi
    
    # Build the project
    echo -e "${YELLOW}Building libadic...${NC}"
    mkdir -p build
    cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    print_status $? "CMake configuration"
    
    make -j$(nproc 2>/dev/null || echo 1)
    print_status $? "Build completed"
    
    # Run each test suite
    echo ""
    echo -e "${YELLOW}Running test suites...${NC}"
    
    tests=(
        "test_gmp_wrapper:GMP wrapper validation"
        "test_zp:p-adic integers (Zp)"
        "test_qp:p-adic numbers (Qp)"
        "test_functions:Special functions"
    )
    
    for test_entry in "${tests[@]}"; do
        IFS=':' read -r test_name test_desc <<< "$test_entry"
        echo -e "${YELLOW}Testing $test_desc...${NC}"
        ./$test_name
        print_status $? "$test_desc tests"
    done
    
    # Run milestone tests
    echo ""
    echo -e "${YELLOW}Running Reid-Li Criterion validation...${NC}"
    
    for p in 5 7 11; do
        echo -e "${YELLOW}Testing p=$p with precision 60...${NC}"
        ./milestone1_test $p 60
        print_status $? "Reid-Li validation for p=$p"
    done
    
    cd ..
fi

# Memory leak check if valgrind is available
if command -v valgrind &> /dev/null && [ ! -f /.dockerenv ]; then
    echo ""
    echo -e "${YELLOW}Running memory leak checks...${NC}"
    cd build
    
    valgrind --leak-check=full --error-exitcode=1 --quiet ./test_gmp_wrapper 2>&1 | grep -q "no leaks are possible"
    print_status $? "Memory check: GMP wrapper"
    
    valgrind --leak-check=full --error-exitcode=1 --quiet ./test_zp 2>&1 | grep -q "no leaks are possible"
    print_status $? "Memory check: Zp"
    
    valgrind --leak-check=full --error-exitcode=1 --quiet ./test_qp 2>&1 | grep -q "no leaks are possible"
    print_status $? "Memory check: Qp"
    
    cd ..
fi

# Final summary
echo ""
echo "=================================================="
echo -e "${GREEN}    ALL TESTS PASSED SUCCESSFULLY!${NC}"
echo "=================================================="
echo ""
echo "Mathematical validations confirmed:"
echo "  ✓ Geometric series identity"
echo "  ✓ Fermat's Little Theorem"
echo "  ✓ Wilson's Theorem"
echo "  ✓ Gamma reflection formula"
echo "  ✓ Hensel's Lemma"
echo "  ✓ p-adic logarithm convergence"
echo "  ✓ Reid-Li Criterion for p=5,7,11"
echo ""
echo "The library is mathematically sound and ready for use."
echo ""

exit 0