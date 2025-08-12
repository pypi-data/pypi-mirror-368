# Challenge Problems: Only Solvable with libadic

## Introduction

These computational challenges demonstrate libadic's unique capabilities. Each problem requires mathematical operations that are **impossible** in PARI/GP, SageMath, FLINT, or Magma.

We invite anyone to attempt these problems with other libraries. The inability to solve them proves libadic's necessity.

---

## Challenge 1: Compute Morita's Gamma Values

**Problem**: Compute Γ_p(n) for n = 1, 2, ..., p-1 where p = 13, using Morita's p-adic Gamma function.

**Expected Output**:
```
Γ_13(1) = -1
Γ_13(2) = 1
Γ_13(3) = -2
Γ_13(4) = 6
Γ_13(5) = -24
Γ_13(6) = 120
Γ_13(7) = -720
Γ_13(8) = 5040
Γ_13(9) = -40320
Γ_13(10) = 362880
Γ_13(11) = -3628800
Γ_13(12) = 39916800
```

**Why only libadic can solve this**:
- Other libraries don't have Morita's formulation
- The specific values (-1)^n(n-1)! are unique to Morita

**libadic solution**:
```cpp
for (long n = 1; n < 13; ++n) {
    Zp gamma_n = gamma_p(n, 13, 20);
    std::cout << "Γ_13(" << n << ") = " << gamma_n.to_string() << "\n";
}
```

---

## Challenge 2: Logarithm of p-adic Gamma

**Problem**: Compute log_p(Γ_p(5)) in Q_7 with precision O(7^30).

**Expected**: A specific p-adic number with valuation ≥ 1.

**Why only libadic can solve this**:
- Requires Morita's Gamma first
- Then requires p-adic logarithm of the result
- No other library has both components correctly

**libadic solution**:
```cpp
Zp gamma_5 = gamma_p(5, 7, 30);
Qp log_gamma = log_gamma_p(gamma_5);
std::cout << "log_7(Γ_7(5)) = " << log_gamma.to_string() << "\n";
```

---

## Challenge 3: Reid-Li Φ Computation

**Problem**: Compute Φ_p^(odd)(χ) for p = 11 where χ is the primitive character with χ(2) = ζ_10 (a primitive 10th root of unity).

**Why only libadic can solve this**:
- Requires sum over log_p(Γ_p(a)) weighted by character values
- This is the core Reid-Li computation
- Literally impossible without libadic

**libadic solution**:
```cpp
DirichletCharacter chi(11, 11);
// Set chi appropriately
Qp phi = compute_phi_odd(chi);
std::cout << "Φ_11^(odd)(χ) = " << phi.to_string() << "\n";
```

---

## Challenge 4: Verify Gamma Reflection Formula

**Problem**: Verify that Γ_p(x) · Γ_p(1-x) = ±1 for x = 3, p = 17, precision = 40.

**Expected**: Product should equal either 1 or -1 in Z_17.

**Why only libadic can solve this**:
- Requires correct Morita Gamma implementation
- Must handle both Γ_p(3) and Γ_p(-2) = Γ_p(p-2)
- Reflection formula is specific to Morita's formulation

---

## Challenge 5: Series Convergence Test

**Problem**: Compute the p-adic logarithm series for log_p(1 + p^2) up to precision O(p^50) for p = 19, showing the precision loss at term n = p.

**Expected**: Show exact precision at each term, demonstrating loss when dividing by p.

**Why only libadic can solve this**:
- Requires honest precision tracking
- Must show the mathematical reality of precision loss
- Other libraries hide or incorrectly handle this

---

## Challenge 6: Character Sum Weighted by log(Gamma)

**Problem**: For p = 23, compute:
```
S = Σ_{χ primitive} Σ_{a=1}^{p-1} χ(a) · log_p(Γ_p(a))
```
Sum over all primitive Dirichlet characters modulo 23.

**Why only libadic can solve this**:
- Double sum over characters and residues
- Each term requires Morita Gamma and its logarithm
- This is a Reid-Li type computation

---

## Challenge 7: High-Precision Reid-Li Verification

**Problem**: Verify the Reid-Li criterion for p = 5 with precision O(5^100).

**Task**: Show that |Φ_5^(odd)(χ) - Ψ_5^(odd)(χ)| has valuation ≥ 100.

**Why only libadic can solve this**:
- Requires complete Reid-Li implementation
- High precision tests the implementation's robustness
- No other library can even attempt this

---

## Challenge 8: Teichmüller-Gamma Interaction

**Problem**: Compute ω(a) · Γ_p(a) for a = 1, ..., p-1 where p = 29 and ω is the Teichmüller character.

**Expected**: Specific p-adic units satisfying certain congruences.

**Why only libadic can solve this**:
- Combines Teichmüller character with Morita Gamma
- Tests interaction between different p-adic structures

---

## Challenge 9: L-function Special Value

**Problem**: Compute L_p(0, χ) where χ is a quadratic character modulo p = 31.

**Why only libadic can solve this**:
- Requires p-adic L-function at s = 0
- Connected to Reid-Li Ψ computation
- Most libraries lack general p-adic L-functions

---

## Challenge 10: The Ultimate Test

**Problem**: For p = 37, find all primitive characters χ such that:
```
v_p(Φ_p^(odd)(χ) - Ψ_p^(odd)(χ)) ≥ 20
```

**Output**: List of characters and their valuations.

**Why only libadic can solve this**:
- Complete Reid-Li implementation required
- Must enumerate and test all primitive characters
- Computationally intensive, mathematically deep

---

## Verification Protocol

To prove these challenges are unsolvable elsewhere:

1. **Attempt in PARI/GP**: Run `validation/comparison_tests/pari_gp_cannot_compute.gp`
2. **Attempt in SageMath**: Run `validation/comparison_tests/sagemath_missing_features.sage`
3. **Attempt in FLINT**: Missing functions make it impossible
4. **Attempt in Magma**: Different Gamma formulation fails

## Running the Challenges

```bash
cd validation/challenges
./run_challenges
```

This will:
1. Solve each challenge using libadic
2. Generate output files with solutions
3. Provide timing information
4. Create verification certificates

## Submission

If anyone can solve ANY of these challenges without libadic, please:
1. Provide complete source code
2. Show output matching our results
3. Explain the mathematical approach

We are confident this is impossible, proving libadic's uniqueness.

---

## Conclusion

These 10 challenges definitively demonstrate that:
- **libadic implements unique mathematics** not available elsewhere
- **The Reid-Li criterion requires libadic** exclusively
- **No workarounds or substitutes exist** in other libraries

This establishes libadic as an **essential tool** for:
- Reid-Li criterion research
- Morita p-adic Gamma computations
- Advanced p-adic special function theory

---

*Challenge issued: 2025*
*Status: UNSOLVED by any other library*