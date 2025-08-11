# LLM-for-SA
 A tool to generate software design document using LLM models

 # Steps to run locally the first time

 1. Clone the repository
 2. Open terminal and go to where repo was cloned.

        cd <repo name>

 4. Run this command there

        python -m venv venv

 5. Then run this command to activate the virtual environment

        For macOS/Linux:

            source venv/bin/activate

        For Windows (PowerShell)

            .\venv\Scripts\Activate.ps1

        (If you get the error saying running scripts is disabled on this system… -> Run this command in the root folder in PowerShell)

            Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

            (When prompted, type Y and press Enter.)

 7. To install dependencies run this command:

        pip install -r requirements.txt

 8. Then this command to run the tool

        python gui.py


# After setting up for the first time:
1.  Navigate to your project folder
2.  Activate the existing virtual venv (Step 4 from earlier)
3.  Install dependencies again only if any changes or additions made
4.  Run the tool with the same command as before

# Evaluation
1. Install dependencies via `pip install -r evaluation/requirements.txt`.
2. Download the [PlantUML JAR](https://github.com/plantuml/plantuml/releases).
3. Rename it to `plantuml.jar` and place it in `evaluation/`.
4. Run `python -m evaluation.main folder`, where `folder` contains either: I) LLM-generated PlantUML diagrams and the ground truth `Benchmark.puml`, or II) Folders each containing LLM-generated PlantUML diagrams and the ground truth `Benchmark.puml`. If the latter, iterative refinement is assumed; that is, each folder represents the second model, with the first model denoted by the files therein. For example, `o3/Gemini.puml` means Gemini was the first model and o3 the second.
In the case of the first option, a CSV table reporting the edit distance, true positives, false positives, false negatives, precision, recall, and F1 score of every model is saved. Otherwise, heatmaps displaying the edit distance, precision, recall, and F1 score of each model pair are saved, with the rows and columns denoting the first and second models used, respectively.
