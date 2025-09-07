📘 Student Study Tracker – Description & User Manual
🌟 App Description

The Student Study Tracker is a simple, interactive web app (built with Streamlit) that helps students manage their Physics and Additional Mathematics revision.

It focuses on:

Daily planning: Add subject-specific tasks by date.

Accountability: Mark tasks as Done, Pending, or Skipped.

Carry-forward system: Incomplete tasks automatically roll over to the next day.

Progress tracking: See completion rates, study hours, and trends over time.

Student profile: Store current exam results and targets for upcoming exams.

Data export: Download study records as CSV for backup or sharing.

The app combines time management, task accountability, and progress monitoring — all in one place.

📝 User Manual
1. Getting Started

Launch the app with:

streamlit run app.py

The app will open in your browser.

2. Onboarding

Fill in your Name, Current Results, and Target Results for Physics and Add Maths.

Save your profile (details are stored for future use).

3. Choosing a Date

Use the sidebar on the left to pick the date you want to plan or review.

All tasks you add, view, or mark as completed are tied to this date.

⚡ Tip: If you select tomorrow, unfinished tasks from today will auto-carry forward.

4. Tabs Overview
🗓️ Daily Plan

Add new tasks for the chosen date:

Enter task name

Select subject (Physics / Add Maths)

Add planned study hours

(Optional) Write notes

Saved tasks appear in a table below.

✅ Mark Completion

View the task list for the selected date.

For each task, choose:

Pending (default)

Done (completed)

Skipped (did not attempt)

Optionally, enter actual study hours and a reflection note.

Save updates individually.

📈 Progress

View a progress bar for the selected date (percentage of tasks completed).

Charts show:

Daily completion % over time

Study hours per subject (planned vs actual)

A table of recent tasks is also shown.

⚙️ Settings

Export data as tasks.csv (can be opened in Excel/Google Sheets).

Option to clear your tasks (permanently deletes tasks for your profile).

5. Carry-Forward Logic

At the start of each new day (or when you switch the sidebar to a new date):

All tasks from the previous day that are Pending or Skipped are copied to the new date.

The carried tasks keep a record of which day they came from.

6. Example Workflow

Morning: Pick today’s date → Add Physics & Add Maths tasks in Daily Plan.

Evening: Go to Mark Completion → Mark tasks Done or Skipped.

Tomorrow: Switch sidebar to next day → Yesterday’s skipped tasks appear automatically.

End of week: Check Progress tab to see completion % and study hours.

Before exams: Download tasks.csv from Settings for review.

✨ In short:
This app ensures students plan daily, stay accountable, and track progress towards exam targets — helping them stay consistent until SPM.
