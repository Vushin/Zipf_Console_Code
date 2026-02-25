# Zipf Console UI Guide

This document explains how to use the interactive Zipf graph tool:

- Script: `RS_vs/zipf_console_ui.py`
- Core helpers: `RS_vs/zipf_utils.py`

The tool lets users type values in the console to generate PMF/CDF plots for
one or more Zipf exponents.

---

## 1) What the script does

1. Accepts user input for:
   - Zipf exponent values (`s`),
   - pool size / number of ranks (`n`),
   - plot type (`pmf`, `cdf`, or `both`),
   - output folder path.
2. Computes Zipf PMF values using `RS_vs/zipf_utils.py`.
3. Generates graph files and prints an entropy table in bits.
4. Saves images into the chosen output folder.

---

## 2) Interactive usage (recommended)

```bash
python RS_vs/zipf_console_ui.py
```

The script prompts for values and uses defaults if you press Enter.

---

## 3) Non-interactive usage (scripted)

```bash
python RS_vs/zipf_console_ui.py --s 1.0,1.4,2.0 --n 1000 --plot both --out-dir RS_vs/Reports/zipf_console --no-prompt
```

### Arguments

- `--s` comma-separated Zipf exponents, for example `1.0,1.2,1.6`
- `--n` number of ranks (pool size)
- `--plot` one of:
  - `pmf`
  - `cdf`
  - `both`
- `--out-dir` output directory
- `--title-suffix` optional title suffix for generated plots
- `--no-prompt` require all required args and disable interactive prompts

---

## 4) Dependencies and installation

To run `zipf_console_ui.py`, you need Python plus two packages:

- `numpy`
- `matplotlib`

### A) Quick check (optional)

```bash
python -c "import numpy, matplotlib; print('ok')"
```

If this prints `ok`, dependencies are already installed.

### B) Install with pip

```bash
python -m pip install --upgrade pip
python -m pip install numpy matplotlib
```

### C) Recommended: virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy matplotlib
```

### D) Conda option

```bash
conda create -n zipf-console python=3.10 -y
conda activate zipf-console
conda install numpy matplotlib -y
```

### E) If pip cannot write to system site-packages

Use user-local install:

```bash
python -m pip install --user numpy matplotlib
```

### F) Standalone-folder note

If you copy only the Zipf console files into a new folder, keep these files
side-by-side:

- `zipf_console_ui.py`
- `zipf_utils.py`

because `zipf_console_ui.py` imports `zipf_utils` directly.

---

## 5) Mathematical refresher for main Zipf functions

Let ranks be `i = 1..N`, where rank `1` is the most probable item.

### A) Zipf normalization constant

$$
Z(s,N) = \sum_{j=1}^{N} j^{-s}
$$

### B) PMF at rank `i`

$$
p_i = \frac{i^{-s}}{Z(s,N)}
$$

Where:

- `N` = number of ranks / support size.
- `s` = Zipf exponent (larger means more mass on top ranks).
- `p_i` = probability of rank `i`.

### C) CDF at rank `k`

$$
F(k) = \sum_{i=1}^{k} p_i
$$

`F(k)` is probability mass in top-`k` items.

### D) Shannon entropy (bits)

$$
H = -\sum_{i=1}^{N} p_i\log_2(p_i)
$$

Interpretation:

- `s \approx 0` behaves closer to uniform (`H` large).
- large `s` yields concentrated mass (`H` smaller).

---

## 6) Detailed pseudocode for main Zipf functions

Below is implementation-oriented pseudocode aligned with the utility functions
used by the console script.

### A) Build Zipf PMF (`zipf_pmf` style)

```text
function ZIPF_PMF(N, s):
    assert N >= 1
    assert s > 0

    # 1) Build unnormalized weights
    weights = array length N
    for i in 1..N:
        weights[i] = i^(-s)

    # 2) Normalize
    Z = sum(weights)
    pmf = array length N
    for i in 1..N:
        pmf[i] = weights[i] / Z

    return pmf
```

### B) Build Zipf CDF from PMF (`zipf_cdf` style)

```text
function ZIPF_CDF_FROM_PMF(pmf):
    cdf = array length len(pmf)
    running = 0
    for i in 1..len(pmf):
        running = running + pmf[i]
        cdf[i] = running
    return cdf
```

### C) Shannon entropy in bits (`shannon_entropy_bits` style)

```text
function SHANNON_BITS(pmf):
    H = 0
    for p in pmf:
        if p > 0:
            H = H - p * log2(p)
    return H
```

### D) Parse exponent list (`parse_s_values` style)

```text
function PARSE_S_VALUES(raw_text):
    # raw example: "1.0, 1.3, 2.0"
    tokens = split(raw_text, ',')
    s_values = []
    for t in tokens:
        x = trim(t)
        if x not empty:
            s_values.append(float(x))
    assert len(s_values) > 0
    return s_values
```

### E) End-to-end console workflow

```text
function RUN_ZIPF_CONSOLE(args):
    if args.no_prompt:
        read params from CLI only
    else:
        prompt for missing params

    s_values = parse list of exponents
    N = number of ranks

    table = []
    for s in s_values:
        pmf = ZIPF_PMF(N, s)
        cdf = ZIPF_CDF_FROM_PMF(pmf)
        H = SHANNON_BITS(pmf)

        table.append({s, H, p1=pmf[1], p10=cdf[min(10,N)]})

        if plot needs PMF:
            draw rank-vs-pmf curve for this s
        if plot needs CDF:
            draw rank-vs-cdf curve for this s

    print entropy/summary table
    save PNG files with timestamp in output folder
```

---

## 7) MATLAB versions of the main Zipf functions

These MATLAB snippets mirror the Python logic and are useful for quick
cross-checks.

### A) `zipf_pmf.m`

```matlab
function p = zipf_pmf(N, s)
%ZIPF_PMF Compute Zipf PMF over ranks 1..N.
%   N: number of ranks (positive integer)
%   s: Zipf exponent (> 0)

    if N < 1 || floor(N) ~= N
        error('N must be a positive integer.');
    end
    if s <= 0
        error('s must be > 0.');
    end

    r = 1:N;
    w = r .^ (-s);
    Z = sum(w);
    p = w / Z;
end
```

### B) `zipf_cdf.m`

```matlab
function F = zipf_cdf(N, s)
%ZIPF_CDF Compute Zipf CDF over ranks 1..N.

    p = zipf_pmf(N, s);
    F = cumsum(p);
end
```

### C) `zipf_entropy_bits.m`

```matlab
function H = zipf_entropy_bits(N, s)
%ZIPF_ENTROPY_BITS Shannon entropy of Zipf PMF in bits.

    p = zipf_pmf(N, s);
    p = p(p > 0); % numerical safety
    H = -sum(p .* log2(p));
end
```

### D) `zipf_topk_mass.m`

```matlab
function m = zipf_topk_mass(N, s, k)
%ZIPF_TOPK_MASS Mass in top-k ranks.

    if k < 1
        m = 0;
        return;
    end
    k = min(k, N);
    p = zipf_pmf(N, s);
    m = sum(p(1:k));
end
```

---

## 8) MATLAB usage examples

### Example 1: PMF, CDF, and entropy for one `(N, s)`

```matlab
N = 1000;
s = 1.3;

p = zipf_pmf(N, s);
F = zipf_cdf(N, s);
H = zipf_entropy_bits(N, s);

fprintf('Entropy (bits): %.4f\n', H);
fprintf('Top-1 mass: %.4f\n', p(1));
fprintf('Top-10 mass: %.4f\n', F(10));
```

### Example 2: Compare multiple exponents

```matlab
N = 1000;
s_values = [1.0, 1.2, 1.5, 2.0];

for s = s_values
    H = zipf_entropy_bits(N, s);
    top10 = zipf_topk_mass(N, s, 10);
    fprintf('s=%.2f  H=%.4f bits  top10=%.4f\n', s, H, top10);
end
```

### Example 3: Plot PMF curves (log-log)

```matlab
N = 1000;
s_values = [1.0, 1.3, 1.8];
r = 1:N;

figure; hold on;
for s = s_values
    p = zipf_pmf(N, s);
    loglog(r, p, 'DisplayName', sprintf('s=%.1f', s));
end
xlabel('Rank'); ylabel('PMF');
title('Zipf PMF (log-log)');
legend('Location','southwest'); grid on;
```

---

## 9) Output files

The Python console script saves PNG files like:

- `zipf_pmf_<timestamp>.png`
- `zipf_cdf_<timestamp>.png`

It also prints Shannon entropy values for each selected `s`.

---

## 10) Notes

- PMF plot uses log-log axes to make rank behavior easier to inspect.
- CDF plot uses log-scale x-axis and linear y-axis.
- Larger `s` values produce stronger concentration toward top ranks.
- For very large `N`, vectorized code paths are much faster than Python/MATLAB
  loops.
