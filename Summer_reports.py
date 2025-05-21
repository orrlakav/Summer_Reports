import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import defaultdict

# --- Predefined exams ---
predefined_exams = {
    "5th Year": {
        "max_scores": [10.0] * 10,
        "topics": [
            "Algebra",
            "Functions",
            "Trigonometry",
            "Statistics",
            "Calculus",
            "Geometry",
            "Probability",
            "Vectors",
            "Sequences",
            "Complex Numbers",
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
    }
}

st.title("📘 Class Report Generator - Maths Exams")

exam_type = st.selectbox("Select Exam Type:", ["5th Year", "2nd Year Higher", "Custom"])

if exam_type == "Custom":
    num_questions = st.number_input("How many questions in the exam?", min_value=1, max_value=50, step=1)
    max_scores = []
    topics = []

    st.markdown("#### Enter Max Score and Topic for Each Question")
    for i in range(num_questions):
        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input(f"Max score for Q{i+1}", min_value=1.0, step=1.0, key=f"ms{i}")
        with col2:
            topic = st.text_input(f"Topic for Q{i+1}", key=f"tp{i}")
        max_scores.append(float(score))
        topics.append(topic)
else:
    max_scores = [float(s) for s in predefined_exams[exam_type]["max_scores"]]
    topics = predefined_exams[exam_type]["topics"]
    num_questions = len(max_scores)

st.markdown("---")
st.header("🧑‍🏫 Enter Class Results")

if "class_data" not in st.session_state:
    st.session_state.class_data = []

with st.form("student_form", clear_on_submit=True):
    student_name = st.text_input("Student Name")
    scores = []
    for i in range(num_questions):
        score = st.number_input(
            f"Score for Q{i+1} ({topics[i]})",
            min_value=0.0,
            max_value=max_scores[i],
            step=0.5,
            key=f"score_input_{i}"
        )
        scores.append(score)
    submitted = st.form_submit_button("Add Student")
    if submitted and student_name.strip():
        st.session_state.class_data.append({
            "name": student_name.strip(),
            "scores": scores
        })

# Display class table
if st.session_state.class_data:
    st.markdown("### Current Class Data")
    class_df = pd.DataFrame([
        {"Student": student["name"], **{f"Q{i+1}": student["scores"][i] for i in range(num_questions)}}
        for student in sorted(st.session_state.class_data, key=lambda x: x["name"].lower())
    ])
    st.dataframe(class_df)

# Metrics and Topic Analysis
if st.session_state.class_data:
    st.markdown("### 📊 Class Metrics")
    percentages = []
    topic_rank_counts = defaultdict(lambda: {"First": 0, "Second": 0, "Third": 0, "Total": 0})
    struggling_students = []
    all_percentages = []

    for student in st.session_state.class_data:
        scores = student["scores"]
        total = sum(scores)
        max_total = sum(max_scores)
        percentage = round((total / max_total) * 100, 2)
        all_percentages.append(percentage)
        if percentage < 40:
            struggling_students.append(student["name"])

        indiv_percentages = [(s / max_scores[i]) * 100 if max_scores[i] > 0 else 0 for i, s in enumerate(scores)]
        df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
        df_sorted = df.sort_values(by="Percentage")

        merged_area_flag = False
        added = 0
        topic_seen = set()
        for idx, (_, row) in enumerate(df_sorted.iterrows()):
            topic = row['Topic']
            rank_label = ["First", "Second", "Third"]
            if topic in ["Area and Volume", "Area and perimeter"]:
                topic = "Area, perimeter and volume"
                if merged_area_flag:
                    continue
                merged_area_flag = True

            if topic not in topic_seen:
                topic_rank_counts[topic][rank_label[added]] += 1
                topic_rank_counts[topic]["Total"] += 1
                topic_seen.add(topic)
                added += 1
            if added == 3:
                break

    st.write(f"**Average:** {np.mean(all_percentages):.2f}%")
    st.write(f"**Median:** {np.median(all_percentages):.2f}%")
    st.write(f"**Max:** {np.max(all_percentages):.2f}%")
    st.write(f"**Min:** {np.min(all_percentages):.2f}%")
    if struggling_students:
        st.write("### 🚨 Students needing additional assistance (< 40%)")
        for name in struggling_students:
            st.write(f"- {name}")

    # Plotly bar chart with 4 colors for rank + total
    topic_df = pd.DataFrame([{
        "Topic": topic,
        "First": counts["First"],
        "Second": counts["Second"],
        "Third": counts["Third"],
        "Total": counts["Total"]
    } for topic, counts in topic_rank_counts.items()])

    topic_df_melted = topic_df.melt(id_vars=["Topic"], value_vars=["First", "Second", "Third", "Total"],
                                    var_name="Rank", value_name="Count")
    fig = px.bar(
        topic_df_melted,
        x="Topic",
        y="Count",
        color="Rank",
        title="Topics That Need the Most Work by Rank",
    )
    st.plotly_chart(fig)
