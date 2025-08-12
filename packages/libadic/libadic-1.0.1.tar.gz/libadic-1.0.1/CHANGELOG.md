# Changelog

All notable changes to libadic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🚀 Added
- Complete p-adic arithmetic implementation (Zp and Qp classes)
- Morita's p-adic Gamma function with reflection formula validation
- Convergent p-adic logarithm with series expansion
- Teichmüller character computation
- Hensel lifting for square roots
- Docker containerization for reproducible builds
- Comprehensive mathematical test framework
- Reid-Li Criterion validation (milestone1_test)

### 🔬 Mathematical Validations
- Geometric series identity: (1-p)(1+p+p²+...) = 1
- Fermat's Little Theorem: a^(p-1) ≡ 1 (mod p)
- Wilson's Theorem: (p-1)! ≡ -1 (mod p)
- Gamma reflection formula: Γ_p(x)·Γ_p(1-x) = ±1
- Hensel's Lemma for solution lifting
- Logarithm convergence conditions
- Chinese Remainder Theorem

### 🏗️ Infrastructure
- CMake build system with GMP/MPFR integration
- GitHub Actions CI/CD pipeline
- Valgrind memory leak detection
- Test coverage analysis
- Multi-platform support (Linux, macOS)

## [1.0.0] - TBD

### Phase 1 Completion
- Core p-adic arithmetic fully implemented
- Special functions (log, Gamma) validated
- Reid-Li Criterion framework established
- All tests passing for p=5,7,11 at precision O(p^60)

### Known Limitations
- L-functions implementation pending (Phase 2)
- Dirichlet character enumeration incomplete
- Cyclotomic field operations not yet optimized

## Versioning Strategy

- **Major (X.0.0)**: Mathematical algorithm changes, API breaking changes
- **Minor (0.X.0)**: New features, performance improvements
- **Patch (0.0.X)**: Bug fixes, documentation updates

## Future Roadmap

### Version 2.0.0 (Phase 2)
- [ ] Complete Kubota-Leopoldt L-function implementation
- [ ] Full Dirichlet character enumeration
- [ ] Cyclotomic field arithmetic optimization
- [ ] Distributed computation support

### Version 3.0.0 (Phase 3)
- [ ] Global Reid-Li computation
- [ ] Parallel processing with MPI
- [ ] GPU acceleration for large-scale computations
- [ ] Web API for remote computation

### Version 4.0.0 (Phase 4)
- [ ] Formal verification with Coq/Lean
- [ ] Automated theorem proving integration
- [ ] Complete Riemann Hypothesis validation framework

---

For detailed release notes, see [GitHub Releases](https://github.com/IguanAI/libadic/releases).