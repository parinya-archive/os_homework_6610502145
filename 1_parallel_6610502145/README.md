# Integer Factorization Project

This project finds prime factors of large numbers using parallel processing.

## How to Run

### Step 1: Set up environment file

Copy the example environment file and add your path:

```bash
cp .env.example .env
```

Edit `.env` and add your project directory path:
```
PATH_CODE_DIR=/path/to/your/1_parallel_6610502145
```

### Step 2: Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the factorization

```bash
python3 parallel.py <large_number>
```

Example:
```bash
python3 parallel.py 123456789
```

## Output

The program will:
- Test factorization using 1-8 CPU cores
- Display timing results for each core count
- Save results to `factor_timing.csv`
- Generate a performance graph `factor_timing.png`
