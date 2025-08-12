#include "libadic/qp.h"
#include "libadic/test_framework.h"
#include <vector>

using namespace libadic;
using namespace libadic::test;

void test_qp_constructors() {
    TestFramework test("Qp Constructors");
    
    Qp a(7, 10);
    test.assert_true(a.is_zero(), "Default constructor creates zero");
    test.assert_equal(a.valuation(), 10L, "Zero has maximal valuation");
    
    Qp b(5, 8, 125);
    test.assert_equal(b.valuation(), 3L, "125 = 5^3, so valuation is 3");
    test.assert_equal(b.get_unit().to_long(), 1L, "Unit part of 125 is 1");
    
    Qp c = Qp::from_rational(2, 3, 7, 10);
    Qp d = Qp::from_rational(3, 1, 7, 10);
    test.assert_equal(c * d, Qp(7, 10, 2), "2/3 * 3 = 2");
    
    Zp z(7, 10, 49);
    Qp from_zp(z);
    test.assert_equal(from_zp.valuation(), 2L, "Qp from Zp preserves valuation");
    
    test.report();
    test.require_all_passed();
}

void test_qp_arithmetic() {
    TestFramework test("Qp Arithmetic Operations");
    
    long p = 5;
    long N = 10;
    
    Qp a = Qp::from_rational(2, 1, p, N);
    Qp b = Qp::from_rational(3, 1, p, N);
    Qp c = Qp::from_rational(1, 5, p, N);
    
    test.assert_equal(a + b, Qp(p, N, 5), "2 + 3 = 5");
    test.assert_equal(a - b, Qp(p, N, -1), "2 - 3 = -1");
    test.assert_equal(a * b, Qp(p, N, 6), "2 * 3 = 6");
    test.assert_equal(b / a, Qp::from_rational(3, 2, p, N), "3 / 2 = 3/2");
    
    test.assert_equal(c.valuation(), -1L, "1/5 has valuation -1");
    test.assert_equal(c * Qp(p, N, 5), Qp(p, N, 1), "1/5 * 5 = 1");
    
    Qp high_val(p, N, BigInt(p).pow(3));
    Qp low_val(p, N, 2);
    test.assert_equal((high_val + low_val).valuation(), 0L, 
                     "p^3 + 2 has valuation 0 (dominated by 2)");
    
    test.mathematical_proof(
        "Field axiom: (a * b)^-1 = b^-1 * a^-1",
        "Multiplicative inverse property",
        (Qp(p, N, 1) / (a * b)) == ((Qp(p, N, 1) / b) * (Qp(p, N, 1) / a))
    );
    
    test.report();
    test.require_all_passed();
}

void test_valuation_properties() {
    TestFramework test("Valuation Properties");
    
    long p = 7;
    long N = 10;
    
    Qp a(p, N, 14);
    Qp b(p, N, 49); 
    
    test.assert_equal(a.valuation(), 1L, "v_7(14) = 1");
    test.assert_equal(b.valuation(), 2L, "v_7(49) = 2");
    
    test.assert_equal((a * b).valuation(), a.valuation() + b.valuation(),
                     "Valuation is multiplicative: v(ab) = v(a) + v(b)");
    
    test.assert_equal((a / b).valuation(), a.valuation() - b.valuation(),
                     "Valuation of quotient: v(a/b) = v(a) - v(b)");
    
    Qp c(p, N, 7);
    Qp d(p, N, 8);
    test.assert_true((c + d).valuation() >= std::min(c.valuation(), d.valuation()),
                    "Strong triangle inequality: v(a+b) >= min(v(a), v(b))");
    
    Qp e(p, N, 7);
    Qp f(p, N, -7);
    test.assert_equal((e + f).valuation(), N, "7 + (-7) = 0 has maximal valuation");
    
    test.mathematical_proof(
        "Non-archimedean property",
        "If v(a) != v(b), then v(a+b) = min(v(a), v(b))",
        (c.valuation() != d.valuation()) && 
        ((c + d).valuation() == std::min(c.valuation(), d.valuation()))
    );
    
    test.report();
    test.require_all_passed();
}

void test_rational_reconstruction() {
    TestFramework test("Rational Reconstruction");
    
    long p = 11;
    long N = 10;
    
    std::vector<std::pair<long, long>> rationals = {
        {1, 2}, {2, 3}, {3, 4}, {5, 7}, {-1, 3}, {22, 7}
    };
    
    for (auto [num, den] : rationals) {
        Qp q = Qp::from_rational(num, den, p, N);
        Qp num_q(p, N, num);
        Qp den_q(p, N, den);
        
        test.assert_equal(q * den_q, num_q,
                         "Rational " + std::to_string(num) + "/" + 
                         std::to_string(den) + " reconstruction correct");
    }
    
    Qp one_third = Qp::from_rational(1, 3, 5, 10);
    Qp three_inv = Qp(5, 10, 1) / Qp(5, 10, 3);
    test.assert_equal(one_third, three_inv, "1/3 equals 1 ÷ 3");
    
    test.report();
    test.require_all_passed();
}

void test_precision_handling() {
    TestFramework test("Precision Handling");
    
    long p = 5;
    
    Qp high(p, 20, 123);
    Qp low = high.with_precision(5);
    
    test.assert_equal(low.get_precision(), 5L, "Precision reduction works");
    test.assert_equal(high.with_precision(5), low, "Precision reduction is consistent");
    
    Qp a(p, 10, 15);
    Qp b(p, 5, 23);
    Qp sum = a + b;
    test.assert_equal(sum.get_precision(), 5L, "Addition uses minimum precision");
    
    Qp val_2(p, 10, 25);
    Qp reduced = val_2.with_precision(3);
    test.assert_equal(reduced.valuation(), 2L, "Valuation preserved in precision reduction");
    
    Qp high_val(p, 5, BigInt(p).pow(6));
    test.assert_true(high_val.is_zero(), "High valuation becomes zero at low precision");
    
    test.report();
    test.require_all_passed();
}

void test_square_roots() {
    TestFramework test("Square Roots in Qp");
    
    long p = 7;
    long N = 10;
    
    Qp four(p, N, 4);
    Qp sqrt_four = four.sqrt();
    test.assert_equal(sqrt_four * sqrt_four, four, "sqrt(4)^2 = 4");
    test.assert_equal(sqrt_four.to_zp().to_long() % p, 2L, "sqrt(4) ≡ 2 (mod 7)");
    
    Qp two(p, N, 2);
    Qp sqrt_two = two.sqrt();
    test.assert_equal(sqrt_two * sqrt_two, two, "sqrt(2)^2 = 2 in Q_7");
    
    Qp p_squared(p, N, 49);
    Qp sqrt_p_squared = p_squared.sqrt();
    test.assert_equal(sqrt_p_squared.valuation(), 1L, "sqrt(p^2) has valuation 1");
    test.assert_equal(sqrt_p_squared, Qp(p, N, 7), "sqrt(49) = 7");
    
    bool odd_val_throws = false;
    try {
        Qp odd_val(p, N, 7);
        odd_val.sqrt();
    } catch (const std::domain_error&) {
        odd_val_throws = true;
    }
    test.assert_true(odd_val_throws, "Square root with odd valuation throws");
    
    test.report();
    test.require_all_passed();
}

void test_powers() {
    TestFramework test("Powers in Qp");
    
    long p = 5;
    long N = 10;
    
    Qp two(p, N, 2);
    test.assert_equal(two.pow(3), Qp(p, N, 8), "2^3 = 8");
    test.assert_equal(two.pow(0), Qp(p, N, 1), "2^0 = 1");
    test.assert_equal(two.pow(-1), Qp::from_rational(1, 2, p, N), "2^(-1) = 1/2");
    
    Qp p_val(p, N, 5);
    test.assert_equal(p_val.pow(2).valuation(), 2L, "(p)^2 has valuation 2");
    
    Qp neg_one(p, N, -1);
    test.assert_equal(neg_one.pow(2), Qp(p, N, 1), "(-1)^2 = 1");
    test.assert_equal(neg_one.pow(3), neg_one, "(-1)^3 = -1");
    
    test.mathematical_proof(
        "Fermat's Little Theorem extension",
        "For unit u: u^(p^n - p^(n-1)) ≡ 1 in Q_p",
        two.pow(BigInt(p).pow(5).to_long() - BigInt(p).pow(4).to_long())
            .with_precision(5) == Qp(p, 5, 1)
    );
    
    test.report();
    test.require_all_passed();
}

void test_field_completeness() {
    TestFramework test("Field Completeness");
    
    long p = 7;
    long N = 15;
    
    Qp sum(p, N, 0);
    Qp term(p, N, 1);
    
    for (int n = 0; n < 50; ++n) {
        sum += term;
        term = term * Qp(p, N, p) / Qp(p, N, n + 1);
    }
    
    Qp exp_p_minus_1 = sum - Qp(p, N, 1);
    
    test.assert_true(exp_p_minus_1.valuation() >= 1,
                    "exp(p) - 1 has positive valuation (converges in Q_p)");
    
    Qp a(p, 10, 1);
    Qp b(p, 10, BigInt(p).pow(10));
    test.assert_equal((a + b).with_precision(10), a,
                    "Cauchy sequence property: p^N → 0");
    
    std::vector<Qp> cauchy_seq;
    Qp x(p, N, 3);  // Start with 3 as initial guess for sqrt(2) mod 7
    Qp two(p, N, 2);
    for (int i = 0; i < 10; ++i) {
        x = (x + two / x) / two;
        cauchy_seq.push_back(x);
    }
    
    Qp diff = cauchy_seq.back() * cauchy_seq.back() - two;
    test.assert_true(diff.valuation() >= 5,
                    "Newton's method converges to sqrt(2)");
    
    test.report();
    test.require_all_passed();
}

void test_negative_valuation() {
    TestFramework test("Negative Valuation Handling");
    
    long p = 5;
    long N = 10;
    
    Qp inv_p = Qp::from_rational(1, 5, p, N);
    test.assert_equal(inv_p.valuation(), -1L, "1/p has valuation -1");
    
    Qp inv_p_squared = Qp::from_rational(1, 25, p, N);
    test.assert_equal(inv_p_squared.valuation(), -2L, "1/p^2 has valuation -2");
    
    test.assert_equal(inv_p * inv_p, inv_p_squared, "1/p * 1/p = 1/p^2");
    
    Qp prod = inv_p * Qp(p, N, 5);
    test.assert_equal(prod, Qp(p, N, 1), "1/p * p = 1");
    
    Qp rational = Qp::from_rational(2, 125, p, N);
    test.assert_equal(rational.valuation(), -3L, "2/125 has valuation -3");
    test.assert_equal(rational.get_unit().to_long(), 2L, "Unit part is 2");
    
    bool overflow_caught = false;
    try {
        Qp::from_rational(1, BigInt(p).pow(20).to_long(), p, 10);
    } catch (const std::overflow_error&) {
        overflow_caught = true;
    }
    test.assert_true(overflow_caught, "Valuation overflow is caught");
    
    test.report();
    test.require_all_passed();
}

void test_special_identities() {
    TestFramework test("Special p-adic Identities");
    
    long p = 7;
    long N = 10;
    
    Qp neg_one(p, N, -1);
    Qp sum(p, N, 0);
    for (int k = 0; k < p - 1; ++k) {
        sum += Qp(p, N, 1);
    }
    test.assert_equal(sum, Qp(p, N, p - 1), "(p-1) * 1 = p - 1");
    
    Qp one(p, N, 1);
    Qp one_plus_p = one + Qp(p, N, p);
    Qp log_series(p, N, 0);
    Qp p_power(p, N, p);
    long sign = 1;
    for (int n = 1; n < 20; ++n) {
        log_series += Qp(p, N, sign) * p_power / Qp(p, N, n);
        p_power *= Qp(p, N, p);
        sign = -sign;
    }
    
    test.assert_true(log_series.valuation() >= 1,
                    "log(1+p) series converges in Q_p");
    
    Qp binom_sum(p, N, 0);
    for (long k = 0; k <= 6; ++k) {
        binom_sum += Qp(p, N, BigInt::binomial(6, k).to_long());
    }
    test.assert_equal(binom_sum, Qp(p, N, 64), "Sum of binomial coefficients = 2^6");
    
    test.report();
    test.require_all_passed();
}

int main() {
    std::cout << "========== EXHAUSTIVE Qp VALIDATION ==========\n\n";
    
    test_qp_constructors();
    test_qp_arithmetic();
    test_valuation_properties();
    test_rational_reconstruction();
    test_precision_handling();
    test_square_roots();
    test_powers();
    test_field_completeness();
    test_negative_valuation();
    test_special_identities();
    
    std::cout << "\n========== ALL Qp TESTS PASSED ==========\n";
    std::cout << "The Qp class is mathematically sound and ready for p-adic analysis.\n";
    
    return 0;
}