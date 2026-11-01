
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from database import save_result, get_results


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="LearnMate",
    page_icon="📚",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

def find_question_bank_csv():
    """Find Question_Bank.csv beside app.py or inside its subfolders."""
    expected_name = "question_bank.csv"

    # Check the LearnMate folder first.
    direct_file = BASE_DIR / "Question_Bank.csv"
    if direct_file.is_file():
        return direct_file

    # Search inside LearnMate (including question_bank_files).
    try:
        for candidate in BASE_DIR.rglob("*"):
            if candidate.is_file() and candidate.name.lower() == expected_name:
                return candidate
    except OSError:
        pass

    # Also check the folder from which Streamlit was launched.
    current_folder = Path.cwd()
    direct_file = current_folder / "Question_Bank.csv"
    if direct_file.is_file():
        return direct_file

    return None


# ---------------- LOAD QUESTION BANK ----------------

@st.cache_data
def load_questions():

    csv_file = find_question_bank_csv()

    if csv_file is None:
        raise FileNotFoundError(
            "Question_Bank.csv was not found. Keep it in the same "
            "folder as app.py or inside the question_bank_files folder. "
            f"App folder checked: {BASE_DIR}"
        )

    df = pd.read_csv(csv_file).fillna("")

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    required_columns = [
        "question_id", "year", "subject", "topic",
        "exam", "difficulty", "question",
        "option_a", "option_b", "option_c",
        "option_d", "correct_option", "explanation"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(missing)
        )

    text_columns = [
        "question_id", "subject", "topic", "exam",
        "question", "option_a", "option_b",
        "option_c", "option_d", "correct_option",
        "explanation"
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["exam"] = df["exam"].str.upper()
    df["correct_option"] = df["correct_option"].str.upper()

    df = df[
        (df["question"] != "") &
        (df["option_a"] != "") &
        (df["option_b"] != "") &
        (df["option_c"] != "") &
        (df["option_d"] != "") &
        (df["correct_option"].isin(["A", "B", "C", "D"]))
    ].copy()

    return df.reset_index(drop=True)


# ---------------- QUESTION FILTER ----------------

def filter_questions(bank, selected_exam, selected_year):

    year_number = 1 if selected_year == "1st Year" else 2

    year_questions = bank[bank["year"] == year_number]

    shared = year_questions[
        year_questions["exam"] == "SHARED"
    ]

    exam_specific = year_questions[
        year_questions["exam"] == selected_exam.upper()
    ]

    combined = pd.concat(
        [shared, exam_specific],
        ignore_index=True
    )

    return combined.drop_duplicates(
        subset=["question_id"]
    ).reset_index(drop=True)


# ---------------- HELPER FUNCTIONS ----------------

def get_options(row):
    return [
        row["option_a"],
        row["option_b"],
        row["option_c"],
        row["option_d"]
    ]


def get_correct_answer(row):
    column = "option_" + row["correct_option"].lower()
    return row[column]


# ---------------- LOAD DATABASE ----------------

st.title("📚 LearnMate")
st.subheader("Your Personal Exam Preparation Assistant")
st.write("Learn. Practice. Improve.")

with st.sidebar:
    st.header("Student Details")

    name = st.text_input("Enter your name")

    year = st.selectbox(
        "Select your year",
        ["1st Year", "2nd Year"]
    )

    exam = st.selectbox(
        "Select your exam",
        ["IIT JEE", "TG EAPCET", "BITSAT"]
    )


try:
    bank = load_questions()
    exam_questions = filter_questions(bank, exam, year)

except Exception as error:
    st.error(f"Could not load questions: {error}")
    st.stop()


st.success(
    f"Question Bank Connected! {len(bank)} questions loaded."
)


# ---------------- DASHBOARD ----------------

st.divider()
st.header("📊 Student Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Available Questions", len(exam_questions))
col2.metric("Selected Exam", exam)
col3.metric("Selected Year", year)

practice_tab, test_tab, results_tab = st.tabs([
    "📘 Practice Questions",
    "📝 Mock Test",
    "📊 Results Dashboard"
])


# ---------------- PRACTICE QUESTIONS ----------------

with practice_tab:

    st.header("📘 Practice Questions")

    if exam_questions.empty:
        st.warning("No questions available for this exam and year.")

    else:
        subjects = sorted(exam_questions["subject"].unique())

        selected_subject = st.selectbox(
            "Select Subject",
            ["All Subjects"] + subjects,
            key="practice_subject"
        )

        if selected_subject == "All Subjects":
            practice_pool = exam_questions.copy()
        else:
            practice_pool = exam_questions[
                exam_questions["subject"] == selected_subject
            ].copy()

        count = st.slider(
            "Number of Questions",
            1,
            min(50, len(practice_pool)),
            min(10, len(practice_pool)),
            key="practice_count"
        )

        questions = practice_pool.head(count)

        with st.form("practice_test_form"):

            practice_answers = {}

            for index, (_, row) in enumerate(questions.iterrows(), 1):

                st.markdown(
                    f"**Q{index}. {row['question']}**"
                )

               

                options = [
                    f"{letter}. {option}"
                    for letter, option in zip(
                        "ABCD", get_options(row)
                    )
                ]

                practice_answers[index] = st.radio(
                    "Choose your answer",
                    options,
                    index=None,
                    key=f"practice_{row['question_id']}_{index}"
                )

                st.divider()

            submitted = st.form_submit_button(
                "Submit Test"
            )

        if submitted:

            correct = 0
            wrong = 0
            unanswered = 0

            for index, (_, row) in enumerate(
                questions.iterrows(), 1
            ):

                chosen = practice_answers[index]

                if chosen is None:
                    unanswered += 1

                elif chosen[0] == str(row["correct_option"]).strip():
                    correct += 1

                else:
                    wrong += 1

            st.subheader("📊 Practice Test Result")

            st.success(f"Correct Answers: {correct}")
            st.error(f"Wrong Answers: {wrong}")
            st.info(f"Unanswered: {unanswered}")

            st.metric(
                "Total Score",
                f"{correct} / {len(questions)}"
            )


# ---------------- MOCK TEST ----------------

def load_mock_test_csv(file_path):
    df = pd.read_csv(file_path).fillna("")

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    if "question_number" in df.columns:
        df["_sort_number"] = pd.to_numeric(
            df["question_number"],
            errors="coerce"
        )
        df = df.sort_values("_sort_number")
        df = df.drop(columns=["_sort_number"])

    return df.reset_index(drop=True)
with test_tab:

    st.header("📝 Mock Tests")

    exam_file_names = {
        "IIT JEE": "JEE_MAIN",
        "TG EAPCET": "TG_EAPCET",
        "BITSAT": "BITSAT"
    }

    year_number = st.selectbox(
        "Select Year",
        [1, 2],
        format_func=lambda x: f"{x}{'st' if x == 1 else 'nd'} Year",
        key="csv_mock_year"
    )

    paper_number = st.selectbox(
        "Select Mock Test",
        [1, 2, 3, 4, 5],
        format_func=lambda x: f"Mock Test {x}",
        key="csv_mock_paper"
    )
    file_prefix = exam_file_names[exam]

    mock_filename = (
        f"{file_prefix}_Mock_Test_{paper_number}_Year{year_number}.csv"
    )

    mock_file = (
        BASE_DIR
        / "Year_Assigned"
        / mock_filename
    )

    if not mock_file.is_file():
        mock_file = BASE_DIR / mock_filename

    if not mock_file.is_file():
        matches = list(BASE_DIR.rglob(mock_filename))
        if matches:
            mock_file = matches[0]

    if not mock_file.is_file():
        st.error(
            f"{exam} Mock Test {paper_number} CSV file not found."
        )
        st.stop()

    
    else:

        try:

            mock_questions = load_mock_test_csv(str(mock_file))

            required_columns = [
                "exam",
                "subject",
                "question",
                "question_type",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_option",
                "correct_answer",
                "explanation",
                "marks_correct",
                "marks_incorrect"
            ]

            missing_columns = [
                col for col in required_columns
                if col not in mock_questions.columns
            ]

            if missing_columns:

                st.error(
                    "CSV columns missing: "
                    + ", ".join(missing_columns)
                )

            elif mock_questions.empty:

                st.warning("Ee Mock Test lo questions levu.")

            else:

                # Check selected exam in CSV
                exam_aliases = {
                    "IIT JEE": [
                        "IIT JEE", "JEE MAIN",
                        "JEE_MAIN", "JEE"
                    ],
                    "TG EAPCET": [
                        "TG EAPCET", "TG_EAPCET",
                        "EAPCET"
                    ],
                    "BITSAT": ["BITSAT"]
                }

                csv_exams = set(
                    mock_questions["exam"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .unique()
                )

                allowed_exams = {
                    value.upper()
                    for value in exam_aliases[exam]
                }

                if not csv_exams.issubset(allowed_exams):

                    st.error(
                        f"{exam} select chesav, kani CSV lo "
                        f"vere exam questions unnayi: "
                        f"{', '.join(csv_exams)}"
                    )

                else:

                    # Check whether another exam's same paper
                    # contains exactly the same questions.
                    other_exams = {
                        "IIT JEE": ["TG_EAPCET", "BITSAT"],
                        "TG EAPCET": ["JEE_MAIN", "BITSAT"],
                        "BITSAT": ["JEE_MAIN", "TG_EAPCET"]
                    }

                    current_questions = set(
                        mock_questions["question"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                    )

                    identical_exam = None

                    for other_prefix in other_exams[exam]:
                        other_filename = (
                            f"{other_prefix}_Mock_Test_{paper_number}_Year{year_number}.csv"
                        )

                        other_file = (
                            BASE_DIR
                            / "Year_Assigned"
                            / other_filename
                        )

                        if not other_file.is_file():
                            other_file = BASE_DIR / other_filename

                        if not other_file.is_file():
                            other_matches = list(
                                BASE_DIR.rglob(other_filename)
                            )
                            if other_matches:
                                other_file = other_matches[0]

                        if other_file.is_file():

                            other_df = load_mock_test_csv(
                                str(other_file)
                            )

                            if "question" in other_df.columns:

                                other_questions = set(
                                    other_df["question"]
                                    .astype(str)
                                    .str.strip()
                                    .str.lower()
                                )

                                if (
                                    current_questions
                                    and current_questions == other_questions
                                ):
                                    identical_exam = other_prefix
                                    break

                    if identical_exam:

                        st.error(
                            f"Warning: {exam} Mock Test "
                            f"{paper_number} and {identical_exam} "
                            "Mock Test questions are identical. "
                            "Please check the CSV files."
                        )

                    else:

                        st.success(
                            f"{exam} | Mock Test {paper_number} | "
                            f"{len(mock_questions)} Questions"
                        )

                        answers = {}

                        with st.form(
                            f"mock_form_{exam}_{paper_number}"
                        ):

                            for index, row in mock_questions.iterrows():

                                st.markdown(
                                    f"### Question {index + 1}"
                                )

                                st.write(row["question"])

                                

                                question_type = str(
                                    row["question_type"]
                                ).strip().upper()

                                if question_type == "MCQ":

                                    options = [
                                        f"{letter}. {str(row[f'option_{letter.lower()}']).strip()}"
                                        for letter in "ABCD"
                                        if str(
                                            row[f"option_{letter.lower()}"]
                                        ).strip()
                                    ]

                                    answers[index] = st.radio(
                                        "Select your answer",
                                        options,
                                        index=None,
                                        key=(
                                            f"mock_{exam}_{paper_number}_{index}"
                                        )
                                    )

                                else:

                                    answers[index] = st.text_input(
                                        "Enter your numerical answer",
                                        key=(
                                            f"mock_{exam}_{paper_number}_{index}"
                                        )
                                    )

                                st.divider()

                            submitted = st.form_submit_button(
                                "Submit Mock Test",
                                type="primary",
                                use_container_width=True
                            )

                        if submitted:

                            unanswered = [
                                i for i, answer in answers.items()
                                if answer is None
                                or str(answer).strip() == ""
                            ]

                            if unanswered:

                                st.warning(
                                    f"{len(unanswered)} questions unanswered."
                                )

                            else:

                                total_score = 0
                                maximum_marks = 0
                                correct_count = 0
                                wrong_count = 0
                                subject_scores = {}
                                review = []

                                for index, row in mock_questions.iterrows():

                                    question_type = str(
                                        row["question_type"]
                                    ).strip().upper()

                                    chosen = str(
                                        answers[index]
                                    ).strip()

                                    correct_option = str(
                                        row["correct_option"]
                                    ).strip().upper()

                                    correct_answer = str(
                                        row["correct_answer"]
                                    ).strip()

                                    if question_type == "MCQ":

                                        chosen_letter = chosen[0].upper()

                                        is_correct = (
                                            chosen_letter == correct_option
                                        )

                                        correct_display = (
                                            correct_option + ". "
                                            + str(
                                                row[
                                                    "option_"
                                                    + correct_option.lower()
                                                ]
                                            )
                                        )

                                    else:

                                        try:

                                            chosen_number = float(
                                                chosen.replace(",", "")
                                            )

                                            correct_number = float(
                                                correct_answer.replace(",", "")
                                            )

                                            is_correct = (
                                                abs(
                                                    chosen_number
                                                    - correct_number
                                                ) < 0.000001
                                            )

                                        except (ValueError, TypeError):

                                            is_correct = (
                                                chosen.casefold()
                                                == correct_answer.casefold()
                                            )

                                        correct_display = correct_answer

                                    positive_marks = float(
                                        row["marks_correct"]
                                    )

                                    negative_marks = float(
                                        row["marks_incorrect"]
                                    )

                                    maximum_marks += positive_marks

                                    if is_correct:

                                        marks_obtained = positive_marks
                                        correct_count += 1

                                    else:

                                        marks_obtained = negative_marks
                                        wrong_count += 1

                                    total_score += marks_obtained

                                    subject = str(row["subject"]).strip()

                                    subject_scores[subject] = (
                                        subject_scores.get(subject, 0)
                                        + marks_obtained
                                    )

                                    review.append({
                                        "Question": index + 1,
                                        "Subject": subject,
                                        "Your Answer": chosen,
                                        "Correct Answer": correct_display,
                                        "Marks": marks_obtained,
                                        "Result": (
                                            "Correct"
                                            if is_correct
                                            else "Wrong"
                                        ),
                                        "Explanation": row["explanation"]
                                    })

                                accuracy = (
                                    correct_count / len(mock_questions)
                                ) * 100

                                st.session_state["mock_csv_result"] = {
                                    "exam": exam,
                                    "paper": paper_number,
                                    "score": total_score,
                                    "maximum_marks": maximum_marks,
                                    "correct": correct_count,
                                    "wrong": wrong_count,
                                    "accuracy": accuracy,
                                    "subject_scores": subject_scores,
                                    "review": review
                                }

                                st.rerun()

                        # DISPLAY RESULTS

                        if "mock_csv_result" in st.session_state:

                            result = st.session_state["mock_csv_result"]

                            if (
                                result["exam"] == exam
                                and result["paper"] == paper_number
                            ):

                                st.divider()
                                st.header("📊 Mock Test Results")

                                col1, col2, col3, col4 = st.columns(4)

                                col1.metric(
                                    "Score",
                                    f"{result['score']:g} / "
                                    f"{result['maximum_marks']:g}"
                                )

                                col2.metric(
                                    "Accuracy",
                                    f"{result['accuracy']:.1f}%"
                                )

                                col3.metric(
                                    "Correct",
                                    result["correct"]
                                )

                                col4.metric(
                                    "Wrong",
                                    result["wrong"]
                                )

                                st.subheader("Subject-wise Scores")

                                for subject, score in (
                                    result["subject_scores"].items()
                                ):

                                    st.write(
                                        f"{subject}: {score:g} marks"
                                    )

                                st.subheader("Answer Review")

                                st.dataframe(
                                    pd.DataFrame(result["review"]),
                                    use_container_width=True,
                                    hide_index=True
                                )

        except Exception as error:

            st.error(
                f"Mock Test load cheyyadam lo problem: {error}"
            )


# ---------------- RESULTS DASHBOARD ----------------

with results_tab:

    st.header("📊 Student Results Dashboard")

    try:
        results = get_results()

        if results:

            columns = [
                "ID",
                "Student Name",
                "Exam",
                "Mathematics",
                "Physics",
                "Chemistry",
                "Total Score",
                "Accuracy (%)"
            ]

            results_df = pd.DataFrame(
                results,
                columns=columns
            )

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No student results available yet.")

    except Exception as error:
        st.error(f"Could not load results: {error}")


st.caption("LearnMate | Practice today, succeed tomorrow.")
