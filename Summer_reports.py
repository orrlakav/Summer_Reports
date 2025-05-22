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

# --- Judgement and drop mappings ---
judgement_texts = {
    "Perfect": "This is an incredible result and a testament to the hard work and talent {name} has shown in the subject. They should be very proud of themselves.",
    "Excellent": "This is a fantastic result and a credit to the dedication {name} has shown throughout the year.",
    "Very good": "{name} should be pleased with this performance – their efforts are clearly paying off.",
    "Good": "This is a good result and reflects the consistent effort {name} has put in this year.",
    "Solid": "A solid performance. With continued focus both in and out of the classroom, {name} can build on this foundation.",
    "OK": "While this is an OK result for {name}, there's definitely room to grow. Increased effort in class and at home will help them achieve a grade they can be truly proud of.",
    "Disappointing": "This is a disappointing outcome for {name}. They need to make a more sustained effort both in class and independently to see improvement.",
    "Awful": "{name} must make a much greater commitment to their studies if they want to earn a result they can be proud of next year."
}

drop_recommendations = {
    "Foundation": "{name} has found Maths particularly challenging this year. It is recommended they consider Foundation Level Maths next year, which may better match their current ability and help build key life and workplace skills.",
    "Ordinary": "{name} has struggled significantly with the demands of Higher Level Maths. It may now be appropriate for them to transition to Ordinary Level, where they can work at a more suitable pace and address learning gaps more effectively."
}

# --- UI to select exam ---
st.title("\U0001F4D8 Class Report Generator - Maths Exams")
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

st.header("\U0001F9D1‍\U0001F3EB Enter Class Results")
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
    st.markdown("### \U0001F4DD Basic Report Preview")
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
    st.download_button("\U0001F4C5 Download Basic Reports", data="\n\n".join(basic_reports), file_name="basic_reports.txt", mime="text/plain")

    # --- Detailed Report Input ---
    with st.expander("➕ Create More Detailed Report"):
        judgements = list(judgement_texts.keys())
        for student in st.session_state.class_data:
            st.selectbox(f"Judgement for {student['name']}", judgements, key=f"judge_{student['name']}")
            st.text_input(f"Recommend Drop for {student['name']} (Optional)", key=f"drop_{student['name']}")

        detailed_reports = []
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

            judgement = st.session_state.get(f"judge_{name}", "")
            drop_level = st.session_state.get(f"drop_{name}", "")

            comment = judgement_texts.get(judgement, "").format(name=name)
            if judgement == "Perfect":
                topic_intro = f"The only areas where marks were lost in this exam were: {topic_text}."
            elif judgement in ["Excellent", "Very good"]:
                topic_intro = f"To further improve this grade, {name} should focus on the following topics: {topic_text}."
            else:
                topic_intro = f"To improve this grade {name} needs to work on the following topics: {topic_text}."

            drop_comment = drop_recommendations.get(drop_level, "").format(name=name)

            full_text = f"Name: {name} | Percentage: {percentage}%\n{comment} {topic_intro} {drop_comment}"
            detailed_reports.append(full_text)

        st.markdown("### 📄 Detailed Report Preview")
        st.text(detailed_reports[0] if detailed_reports else "No detailed report available yet.")

        if detailed_reports:
            st.download_button("📥 Download Detailed Reports", data="\n\n".join(detailed_reports), file_name="detailed_reports.txt", mime="text/plain")
