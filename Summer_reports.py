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

with st.form("student_form"):
    student_name = st.text_input("Student Name")
    scores = []
    for i in range(num_questions):
        score = st.number_input(
            f"Score for Q{i+1} ({topics[i]})",
            min_value=0.0,
            max_value=max_scores[i],
            step=0.5,
            key=f"score_input_{student_name}_{i}"
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
        for student in st.session_state.class_data
    ])
    st.dataframe(class_df)

# Download button
if st.session_state.class_data:
    if st.button("Download Results as CSV"):
        download_df = pd.DataFrame([
            {"Student": student["name"], **{f"Q{i+1}": student["scores"][i] for i in range(num_questions)}}
            for student in st.session_state.class_data
        ])
        csv = download_df.to_csv(index=False).encode("utf-8")
        st.download_button("Click to download", data=csv, file_name="class_results.csv", mime="text/csv")

# Generate reports
if st.session_state.class_data:
    if st.button("Generate Class Reports"):
        report_texts = []
        for student in st.session_state.class_data:
            scores = student["scores"]
            percentages = [(s / max_scores[i]) * 100 if max_scores[i] > 0 else 0 for i, s in enumerate(scores)]
            df = pd.DataFrame({
                "Question": [f"Q{i+1}" for i in range(num_questions)],
                "Topic": topics,
                "Score": scores,
                "Max Score": max_scores,
                "Percentage": percentages
            })
            df_sorted = df.sort_values(by=["Percentage", "Topic"])

            improvement_topics = []
            merged_area_flag = False

            for _, row in df_sorted.iterrows():
                topic = row['Topic']
                if topic in ["Area and Volume", "Area and perimeter"]:
                    if not merged_area_flag:
                        improvement_topics.append("Area, perimeter and volume")
                        merged_area_flag = True
                elif topic not in improvement_topics:
                    improvement_topics.append(topic)
                if len(improvement_topics) >= 3:
                    break

            report_text = f"{student['name']} should revise: {', '.join(improvement_topics)}."
            report_texts.append(report_text)

        st.markdown("### 📄 Class Report Summary")
        for r in report_texts:
            st.text(r)

        full_report = "\n".join(report_texts)
        st.download_button("Download Report Text", data=full_report, file_name="class_reports.txt", mime="text/plain")
