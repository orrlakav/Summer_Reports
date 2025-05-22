import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import defaultdict

# --- Predefined exams ---
predefined_exams = {
    "5th Year Ordinary": {
        "max_scores": [30.0, 30.0, 30.0, 30.0, 30.0, 50.0, 30.0, 30.0],
        "topics": [
            "Solving equations",
            "Coordinate Geometry of the Circle",
            "Coordinate Geometry of the Line",
            "Complex Numbers",
            "Patterns and Sequences",
            "Patterns and Sequences",
            "Algebra",
            "Fractions and Indices"
        ]
    },
    "2nd Year Higher": {
        "max_scores": [20.0, 25.0, 35.0, 35.0, 35.0, 20.0, 20.0, 25.0, 10.0, 15.0],
        "topics": [
            "Averages",
            "Factorising and inequalities",
            "Statistical charts",
            "Coordinate Geometry",
            "Area and Volume",
            "Financial Maths",
            "Factorising and solving equations",
            "Writing equations",
            "Area and perimeter",
            "Number",
        ]
    },
    "2nd Year Ordinary": {
        "max_scores": [25.0, 25.0, 20.0, 15.0, 10.0, 10.0, 25.0, 25.0, 10.0, 20.0, 15.0],
        "topics": [
            "Number",
            "Sets",
            "Algebra",
            "Financial Maths",
            "Worded problems",
            "Ratios and compound interest",
            "Financial Maths",
            "Financial Maths",
            "Coordinate Geometry of the line",
            "Statistics (measures of average)",
            "Statistical diagrams"
        ]
    }
}

# Topic merging rules
MERGE_TOPICS = {
    frozenset(["Area and Volume", "Area and perimeter"]): "Area, perimeter and volume",
    frozenset(["Statistics (measures of average)", "Statistical diagrams"]): "Statistics",
    frozenset(["Financial Maths"]): "Financial Maths",
    frozenset(["Factorising and solving equations", "Factorising and inequalities"]): "Factorising and Inequalities"
}

def merge_topic(topic):
    for key_set, merged in MERGE_TOPICS.items():
        if topic in key_set:
            return merged
    return topic

def get_unique_name(name, existing_names):
    if name not in existing_names:
        return name
    i = 1
    new_name = f"{name}{i}"
    while new_name in existing_names:
        i += 1
        new_name = f"{name}{i}"
    return new_name

# --- UI to select exam ---
st.title("📘 Class Report Generator - Maths Exams")
exam_type = st.selectbox("Select Exam Type:", list(predefined_exams.keys()) + ["Custom"])

if exam_type == "Custom":
    num_questions = st.number_input("How many questions in the exam?", min_value=1, max_value=50, step=1)
    max_scores, topics = [], []
    for i in range(num_questions):
        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input(f"Max score for Q{i+1}", min_value=1.0, step=1.0, key=f"custom_ms{i}")
        with col2:
            topic = st.text_input(f"Topic for Q{i+1}", key=f"custom_tp{i}")
        max_scores.append(float(score))
        topics.append(topic)
else:
    default_max_scores = predefined_exams[exam_type]["max_scores"]
    default_topics = predefined_exams[exam_type]["topics"]
    num_questions = len(default_max_scores)
    max_scores, topics = [], []
    for i in range(num_questions):
        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input(f"Max score for Q{i+1}", value=float(default_max_scores[i]), min_value=1.0, step=1.0, key=f"edit_ms{i}")
        with col2:
            topic = st.text_input(f"Topic for Q{i+1}", value=default_topics[i], key=f"edit_tp{i}")
        max_scores.append(float(score))
        topics.append(topic)

# --- Student Input Form ---
if "class_data" not in st.session_state:
    st.session_state.class_data = []

st.header("🧑‍🏫 Enter Class Results")
with st.form("student_form", clear_on_submit=True):
    student_name = st.text_input("Student Name")
    scores = [st.number_input(f"Score for Q{i+1} ({topics[i]})", min_value=0.0, max_value=max_scores[i], step=0.5, key=f"score_input_{i}") for i in range(num_questions)]
    submitted = st.form_submit_button("Add Student")
    if submitted and student_name.strip():
        existing_names = {s["name"] for s in st.session_state.class_data}
        unique_name = get_unique_name(student_name.strip(), existing_names)
        st.session_state.class_data.append({"name": unique_name, "scores": scores})
        st.success(f"Student {unique_name} added successfully!")

# --- Basic Report Generation ---
if st.session_state.class_data:
    st.markdown("### 📝 Basic Report Preview")
    basic_reports = []
    for student in st.session_state.class_data:
        name = student["name"]
        scores = student["scores"]
        percentage = round(sum(scores) / sum(max_scores) * 100, 2)
        indiv_percentages = [(s / max_scores[i]) * 100 for i, s in enumerate(scores)]
        df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
        df["Topic"] = df["Topic"].apply(merge_topic)
        df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")
        top_topics = df_sorted["Topic"].head(3).tolist()
        topic_text = "; ".join(top_topics)
        report = f"Name: {name} | Percentage: {percentage}%\nTo improve this grade {name} needs to work on the following topics: {topic_text}."
        basic_reports.append(report)

    st.text(basic_reports[0])
    st.download_button("📥 Download Basic Reports", data="\n\n".join(basic_reports), file_name="basic_reports.txt", mime="text/plain")