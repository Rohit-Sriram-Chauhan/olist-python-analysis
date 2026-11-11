# Start here, Rohit

This is a Python data analyst portfolio project built from your nine Olist CSV
files. The main analysis is deliberately small enough to study. The cohort,
seller-concentration and review-uncertainty sections add depth without requiring
machine learning.

## 1. Open the finished results

Extract the ZIP first. Open `reports/executive_report.html` in Chrome or Edge.
It works offline and contains the charts. Read `reports/executive_summary.md`
for the shorter business explanation.

## 2. Open the project in PyCharm

1. Choose **Open** and select the extracted `olist-python-portfolio` folder.
2. Use a Python 3.11+ interpreter. The project was checked with Python 3.12.
3. Open PyCharm's terminal. Make sure it is inside the project folder, where
   `run_analysis.py` is located.
4. Install the analysis packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Run the project:

   ```bash
   python run_analysis.py
   ```

6. The run rebuilds the summary CSVs, six charts and HTML report. It does not
   rewrite your raw CSV files or refresh the saved notebook outputs.

The **complete download** already includes `data/raw/`. The **GitHub-ready
download** omits the raw CSVs; copy your nine original CSVs into `data/raw/`
before running it.

## 3. Work through the notebook

You can read the saved notebook on GitHub without running anything. To work
interactively on your computer:

```bash
python -m pip install -r requirements-notebook.txt
python -m notebook
```

Open `notebooks/01_olist_analysis.ipynb`. Choose **Restart Kernel and Run All**
to refresh its outputs, then save. Start with the sections through delivery and
reviews; study cohorts after you understand `groupby`, `merge` and date columns.

## 4. Check your installation

```bash
python -m unittest discover -s tests -v
```

Expected: eight tests pass. A successful analysis run also writes ten source
reconciliation checks to `outputs/tables/validation_checks.csv`.

## 5. Prepare your GitHub portfolio

Follow `docs/GITHUB_GUIDE.md`. Use the GitHub-ready ZIP for the simplest upload.
The project README is already written for a visitor who has not seen this chat.
The raw data stay on Kaggle; the repository includes results and instructions
to reproduce them.

## 6. Make the project your own through practice

Read `docs/LEARNING_AND_INTERVIEW_GUIDE.md`. Before adding it to your resume,
run it yourself, recreate one chart, change one analysis question and practise
explaining why the tables are joined this way. Keep your own observations in
the final notebook section. The project demonstrates an analysis; it does not
claim employment at Olist or an implemented business improvement.

## Common errors

| Message / problem | What to do |
|---|---|
| `ModuleNotFoundError: pandas` | Install the requirements using the same Python interpreter that runs the project. |
| `Missing files in ...data/raw` | Extract/copy all nine CSVs into `data/raw/`; keep their original filenames. |
| Python cannot find `run_analysis.py` | Open a terminal in the extracted project folder. |
| `No module named src` in the notebook | Start the notebook from the project folder, or open its `notebooks/` subfolder. Do not move only the notebook elsewhere. |
| You downloaded the report but cannot run Python | Use the complete project ZIP; the report alone is a read-only result. |
| You reran the script but notebook values are old | Restart and run all notebook cells, then save. The script regenerates reports, not saved notebook cells. |
