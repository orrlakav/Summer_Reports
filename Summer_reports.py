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

# --- UI to add student ---
st.header("Add a Student")
selected_exam = st.selectbox("Select Exam Type", list(predefined_exams.keys()), key="exam_select")
exam_data = predefined_exams[selected_exam]
max_scores = exam_data["max_scores"]
topics = exam_data["topics"]

if "class_data" not in st.session_state:
    st.session_state.class_data = []

with st.form("student_form"):
    student_name = st.text_input("Student Name")
    scores = []
    for i in range(len(max_scores)):
        score = st.number_input(f"Score for {topics[i]}", min_value=0.0, max_value=max_scores[i], step=0.5, key=f"score_input_{i}")
        scores.append(score)
    submitted = st.form_submit_button("Add Student")

    if submitted and student_name.strip():
        existing_names = {s["name"] for s in st.session_state.class_data}
        unique_name = get_unique_name(student_name.strip(), existing_names)
        st.session_state.class_data.append({"name": unique_name, "scores": scores})
        st.success(f"Student {unique_name} added successfully!")

# --- Basic report generation ---
if st.session_state.class_data:
    exam_data = predefined_exams[selected_exam]
    max_scores = exam_data["max_scores"]
    topics = exam_data["topics"]
    basic_reports = []

    for student in st.session_state.class_data:
        name = student['name']
        scores = student['scores']
        percentage = round(sum(scores) / sum(max_scores) * 100, 2)
        basic_reports.append(f"Name: {name} | Percentage: {percentage}%")

    st.download_button("📥 Download Basic Reports", data="\n".join(basic_reports), file_name="basic_reports.txt", mime="text/plain")

    st.markdown("### 📝 Report Preview")
    st.text(basic_reports[0] if basic_reports else "No data available.")

    with st.expander("➕ Create More Detailed Report"):
        judgements = ["Perfect", "Excellent", "Very good", "Good", "Solid", "OK", "Disappointing", "Awful"]
        for idx, s in enumerate(st.session_state.class_data):
            sname = s['name']
            st.selectbox(f"Judgement for {sname}", judgements, key=f"judge_{sname}_{idx}")
            st.text_input(f"Recommend Drop for {sname} (Optional)", key=f"drop_{sname}_{idx}")

        detailed_reports = []
        for idx, student in enumerate(st.session_state.class_data):
            name = student['name']
            scores = student['scores']
            percentage = round(sum(scores) / sum(max_scores) * 100, 2)

            indiv_percentages = [(s / max_scores[i]) * 100 if max_scores[i] > 0 else 0 for i, s in enumerate(scores)]
            df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
            df["Topic"] = df["Topic"].apply(merge_topic)
            df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")

            topic_seen = set()
            topics_to_improve = []
            for _, row in df_sorted.iterrows():
                topic = row['Topic']
                if topic not in topic_seen:
                    topics_to_improve.append(topic)
                    topic_seen.add(topic)
                if len(topics_to_improve) == 3:
                    break

            topic_list = "; ".join(topics_to_improve)
            judgement = st.session_state.get(f"judge_{name}_{idx}", "")
            drop_level = st.session_state.get(f"drop_{name}_{idx}", "")

            comment = judgement_texts.get(judgement, "").format(name=name)
            if judgement == "Perfect":
                topic_intro = f"The only areas where marks were lost in this exam were: {topic_list}."
            elif judgement in ["Excellent", "Very good"]:
                topic_intro = f"To further improve this grade, {name} should focus on the following topics: {topic_list}."
            else:
                topic_intro = f"To improve this grade {name} needs to work on the following topics: {topic_list}."

            drop_comment = drop_recommendations.get(drop_level, "").format(name=name)

            full_text = (
                f"Name: {name} | Percentage: {percentage}%\n"
                f"{comment} {topic_intro} {drop_comment}"
            )
            detailed_reports.append(full_text)

        if detailed_reports:
            st.download_button("📥 Download Detailed Reports", data="\n\n".join(detailed_reports), file_name="detailed_reports.txt", mime="text/plain")


    if st.checkbox("Show Class Analytics"):
        st.markdown("### 📊 Class Metrics")
        topic_rank_counts = defaultdict(lambda: {"First": 0, "Second": 0, "Third": 0, "Total": 0})
        struggling_students = []
        all_percentages = []

        for student in st.session_state.class_data:
            scores = student["scores"]
            total = sum(scores)
            percentage = round((total / sum(max_scores)) * 100, 2)
            all_percentages.append(percentage)
            if percentage < 40:
                struggling_students.append(student["name"])

            indiv_percentages = [(s / max_scores[i]) * 100 if max_scores[i] > 0 else 0 for i, s in enumerate(scores)]
            df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
            df["Topic"] = df["Topic"].apply(merge_topic)
            df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")

            rank_label = ["First", "Second", "Third"]
            added = 0
            topic_seen = set()
            for _, row in df_sorted.iterrows():
                topic = row['Topic']
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

        if detailed_reports:
    	    st.download_button("Download All Reports as Text File", data="\n".join(detailed_reports), file_name="class_reports.txt", mime="text/plain") 
