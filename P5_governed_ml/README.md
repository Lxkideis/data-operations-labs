# Governed ML evaluation

NumPy logistic model with leakage exclusion and train-only preprocessing.

## Run and verify

From this directory:

```powershell
python run.py
python -m unittest -v test_case.py
```

Requires NumPy: install the repository requirements first.

## Saved result and limits

3,000 independent synthetic records; 60/20/20 ID-ordered split; held-out ROC-AUC 0.7612.

ID ordering does not establish real temporal generalization; no LLM or production deployment. All business inputs are fictional. Re-running writes generated evidence to `output/`. [Saved results and assumptions](结果报告.html).
