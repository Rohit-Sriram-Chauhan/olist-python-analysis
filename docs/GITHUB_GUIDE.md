# Put the project on GitHub

Suggested repository name: `olist-python-analysis`  
Suggested description: `Python analysis of Olist sales, delivery performance and customer experience using pandas and Matplotlib.`

## Simple browser upload

1. Extract **Olist_Python_GitHub_Ready.zip**. This version contains the project,
   saved results and notebook, but no raw CSVs.
2. Create an empty GitHub repository with the name above. Do not add a second
   starter README or licence; the project already has them.
3. Use the repository's file-upload option. Upload the **contents** of the
   `olist-python-portfolio` folder, so `README.md` and `run_analysis.py` are at
   the repository's top level.
4. Preserve the folders `src`, `notebooks`, `reports`, `outputs`, `data`, `docs`
   and `tests`. Do not upload the ZIP as your only repository file: GitHub
   cannot display the project README/notebook from inside an archive.
5. Commit with a specific message such as `Add Olist sales and delivery analysis`.
6. Open the README and notebook in the repository. Confirm that chart images
   display and the notebook has saved results.
7. In the repository description, add topics such as `python`, `pandas`,
   `data-analysis`, `ecommerce`, `matplotlib`, and `portfolio` if desired.

GitHub interface labels may vary. The underlying requirement is to upload the
folder contents while keeping their relative paths.

## If uploading the complete download instead

Leave out `data/raw/*.csv`, virtual environments, cache folders and any ZIP
files. A browser upload does not automatically apply `.gitignore`. The
GitHub-ready ZIP already makes this selection for you.

Do not add a single outer folder around the whole project in the repository.
Otherwise the README will not be the main page when a reviewer opens it.

## Command-line option

After creating an empty repository and installing Git, run these commands
from your extracted project folder. Replace `YOUR_USERNAME` and the repository
name with the actual values; these are placeholders, not an existing URL.

```bash
git init
git add .
git status
git commit -m "Add Olist sales and delivery analysis"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/olist-python-analysis.git
git push -u origin main
```

Check `git status` before committing: it should not list the raw CSVs or your
virtual environment. With the command-line method, `.gitignore` excludes them.

## What a recruiter should see quickly

- A clear business question at the top of the README.
- Measured results and a chart, rather than only a list of libraries.
- An understandable notebook with outputs and stated data decisions.
- A short business summary with practical next steps.
- Reproducible instructions and meaningful validation.

GitHub displays Markdown, PNGs and notebooks. The HTML report is a downloadable
offline report; clicking its file in a repository does not create a live site.
The README and Markdown business summary provide the in-repository reading path.

## Add your own work before sharing

Complete at least one exercise from the learning guide, record the question and
your interpretation, rerun the notebook, and commit that change with a specific
message. This gives you a concrete decision to discuss in an interview.
