import streamlit as st
import pandas as pd

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
    "2nd Year": {
        "max_scores": [5.0, 10.0, 8.0, 7.0, 10.0, 5.0, 5.0, 10.0],
        "topics": [
            "Equations",
            "Ratios",
            "Fractions",
            "Percentages",
            "Geometry",
            "Graphs",
            "Averages",
            "Area & Volume",
        ]
    }
}

st.title("📘 Student Report Generator - Maths Exams")

exam_type = st.selectbox("Select Exam Type:", ["5th Year", "2nd Year", "Custom"])

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
st.header("🔢 Enter Student Scores")
student_name = st.text_input("Student Name")
scores = []

for i in range(num_questions):
    score = st.number_input(
        f"Score for Q{i+1} ({topics[i]})",
        min_value=0.0,
        max_value=float(max_scores[i]),
        step=0.5,
        key=f"scr{i}"
    )
    scores.append(score)

if st.button("Generate Report"):
    if not student_name.strip():
        st.warning("Please enter the student's name before generating the report.")
    else:
        percentages = [(s / max_scores[i]) * 100 if max_scores[i] > 0 else 0 for i, s in enumerate(scores)]
        df = pd.DataFrame({
            "Question": [f"Q{i+1}" for i in range(num_questions)],
            "Topic": topics,
            "Score": scores,
            "Max Score": max_scores,
            "Percentage": percentages
        })
        df_sorted = df.sort_values(by=["Percentage", "Topic"]).head(3)

        st.success(f"Report for {student_name}")
        st.write("### Topics to Focus On:")
        for i, row in df_sorted.iterrows():
            st.markdown(f"- **{row['Topic']}** (Q{row['Question'][-1]} - {row['Percentage']:.1f}%)")

        st.write("\n---\n### Full Breakdown")
        st.table(df)
