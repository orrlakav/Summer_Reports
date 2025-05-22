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

MERGE_TOPICS = {
    frozenset(["Area and Volume", "Area and perimeter"]): "Area, perimeter and volume",
    frozenset(["Statistics (measures of average)", "Statistical diagrams"]): "Statistics",
    frozenset(["Financial Maths"]): "Financial Maths"
}

def merge_topic(topic):
    for key_set, merged in MERGE_TOPICS.items():
        if topic in key_set:
            return merged
    return topic

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
    "Ordinary": "{name} has struggled significantly with the demands of Higher Level Maths. It may now be appropriate for them to transition to Ordinary Level, where they can work at a more suitable pace and address learning gaps more effectively.",
    "No": ""
}

# Ensure session state structure exists
if "class_data" not in st.session_state:
    st.session_state.class_data = []

st.title("📘 Student Report Generator")
exam_type = st.selectbox("Select Exam Type", list(predefined_exams.keys()) + ["Custom"], key="selected_exam")
if exam_type == "Custom":
    custom_q_count = st.number_input("Number of Questions", min_value=1, max_value=50, step=1, key="custom_q_count")
    max_scores = []
    topics = []
    for i in range(custom_q_count):
        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input(f"Max Score for Q{i+1}", min_value=1.0, step=1.0, key=f"custom_score_{i}")
        with col2:
            topic = st.text_input(f"Topic for Q{i+1}", key=f"custom_topic_{i}")
        max_scores.append(score)
        topics.append(topic)
else:
    exam_data = predefined_exams[exam_type]
    max_scores = exam_data["max_scores"]
    topics = exam_data["topics"]

with st.form("student_entry"):
    student_name = st.text_input("Student Name")
    scores = [st.number_input(f"Score for Q{i+1} ({topics[i]})", min_value=0.0, max_value=max_scores[i], step=0.5, key=f"score_input_{i}") for i in range(len(max_scores))]
    submitted = st.form_submit_button("Add Student")

    if submitted and student_name.strip():
        st.session_state.class_data.append({
            "name": student_name,
            "scores": scores
        })

if st.session_state.class_data:
    st.markdown("### Current Class Data")
    df_display = pd.DataFrame([{
        **{"Name": s["name"]},
        **{f"Q{i+1}": s["scores"][i] for i in range(len(s["scores"]))},
        "Total": sum(s["scores"]),
        "%": round((sum(s["scores"]) / sum(max_scores)) * 100, 2)
    } for s in st.session_state.class_data])
    df_display = df_display.sort_values("Name")
    st.dataframe(df_display)

    # Download button for class data
    csv_data = df_display.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Class Data as CSV", data=csv_data, file_name="class_data.csv", mime="text/csv")

    st.markdown("### Judgement & Recommendations")
    judgements = ["", "Perfect", "Excellent", "Very good", "Good", "Solid", "OK", "Disappointing", "Awful"]
    drop_options = ["No", "Ordinary", "Foundation"]

    summary_data = []
    for s in st.session_state.class_data:
        sname = s['name']
        percent = round((sum(s["scores"]) / sum(max_scores)) * 100, 2)
        judgement = st.selectbox("Judgement", judgements, key=f"judge_{sname}")
        drop = st.selectbox("Recommend Drop", drop_options, key=f"drop_{sname}")
        summary_data.append({"Student": sname, "Result": f"{percent}%", "Judgement": judgement, "Recommend Drop": drop})

    st.dataframe(pd.DataFrame(summary_data))
