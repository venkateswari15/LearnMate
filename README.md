# 📚 LearnMate – Online Exam Preparation Platform

## 1. About the Project

LearnMate is an online exam preparation application developed using Python and Streamlit.

It helps students prepare for competitive entrance examinations through practice questions and mock tests.

## 2. Supported Exams

- IIT JEE (JEE Main)
- TG EAPCET
- BITSAT

## 3. Features

### 📘 Practice Questions
- Students can practice exam-related questions.
- Questions are loaded from CSV files.
- Students can select questions and check their answers.

### 📝 Mock Tests
- Separate mock tests for different entrance examinations.
- Year-wise question selection (1st Year and 2nd Year).
- Multiple mock test papers.
- Supports MCQ and Numerical questions.
- Automatic mark calculation based on the CSV marking scheme.

### 📊 Results Dashboard
- Displays student test results.
- Stores results using an SQLite database.
- Helps students review their performance.

## 4. Technologies Used

- Python
- Streamlit
- Pandas
- SQLite Database
- CSV Files

## 5. Project Structure

```text
LearnMate/
│
├── app - Copy.py
├── database.py
├── Question_Bank.csv
│
├── Mock_Tests/
│
├── Year_Assigned/
│
├── question_bank_files/
│
└── README.md
```

## 6. How to Run the Application

### Step 1
Install Python on your computer.

### Step 2
Install the required libraries.

```bash
pip install streamlit pandas
```

### Step 3
Open the LearnMate project folder in Command Prompt.

### Step 4
Run the application.

```bash
python -m streamlit run "app - Copy.py"
```

### Step 5
Open the local URL displayed in the terminal.

```text
http://localhost:8501
```

## 7. Project Objective

The main objective of LearnMate is to provide students with a simple platform to practice questions, attend mock tests, and track their examination performance.

## 8. Conclusion

LearnMate makes competitive exam preparation easier by bringing practice questions, mock tests, and results tracking together in one application.

**Project Name: LearnMate**  
**Developed Using: Python and Streamlit**

## 🌐 Live Website

[Open LearnMate](https://learnmate-exam-prep.streamlit.app/)
