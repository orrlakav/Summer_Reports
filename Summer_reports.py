import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import defaultdict

# --- Predefined exams ---
predefined_exams = {
    "5th Year Higher": {
        "max_scores": [30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0],
        "topics": [
            "Patterns and Sequences",
            "Coordinate Geometry of the Circle",
            "Coordinate Geometry of the Line",
            "Logs and Indices",
            "Financial Maths",
            "Algebra",
            "Patterns and Sequences",
            "Complex Numbers",
            "Trigonometry",
            "Trigonomotery"
        ]
    },
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
    frozenset(["Financial Maths"]): "Financial Maths",
    frozenset(["Trigonometry"]): "Trigonometry"
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
    "OK": "While this is an OK result for {name}, there's definitely room to improve. Increased effort in class and at home will help them achieve a grade they can be truly proud of.",
    "Disappointing": "This is a disappointing outcome for {name}. They need to make a more sustained effort both in class and independently to see improvement.",
    "Awful": "{name} must make a much greater commitment to their studies if they want to earn a result they can be proud of next year."
}

drop_recommendations = {
    "Foundation": "{name} has found Maths particularly challenging this year. It is recommended they consider Foundation Level Maths next year, which may better match their current ability and help build key life and workplace skills.",
    "Ordinary": "{name} has struggled significantly with the demands of Higher Level Maths. It may now be appropriate for them to transition to Ordinary Level, where they can work at a more suitable pace and address learning gaps more effectively.",
    "No": ""
}

def get_topic_intro(judgement, name, topic_list):
    if judgement == "Perfect":
        return f"The only areas where marks were lost in this exam were: {topic_list}."
    elif judgement in ["Excellent", "Very good"]:
        return f"To further improve this grade, {name} should focus on the following topics: {topic_list}."
    else:
        return f"To improve this grade {name} needs to work on the following topics: {topic_list}."
       
if "class_data" not in st.session_state:
    st.session_state.class_data = []

st.title("📘 Student Report Generator")
exam_type = st.selectbox("Select Exam Type", list(predefined_exams.keys()) + ["Custom"], key="selected_exam")

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

with st.form("student_entry"):
    student_name = st.text_input("Student Name")
    scores = [
        st.number_input(f"Score for Q{i+1} ({topics[i]})", min_value=0.0, max_value=max_scores[i], step=0.5, key=f"score_input_{i}")
        for i in range(len(max_scores))
    ]
    submitted = st.form_submit_button("Add Student")
    if submitted and student_name.strip():
        st.session_state.class_data.append({"name": student_name.strip(), "scores": scores})

if st.session_state.class_data:
    st.markdown("### 📊 Current Class Data")
    df_display = pd.DataFrame([{
        "Name": s["name"],
        **{f"Q{i+1}": s["scores"][i] for i in range(len(s["scores"]))},
        "Total": sum(s["scores"]),
        "%": round((sum(s["scores"]) / sum(max_scores)) * 100, 2)
    } for s in st.session_state.class_data])
    st.dataframe(df_display)
    st.download_button("⬇️ Download Class Data as CSV", data=df_display.to_csv(index=False).encode("utf-8"), file_name="class_data.csv", mime="text/csv")

    st.markdown("### 📝 Basic Report Preview")
    basic_reports = []
    sorted_class_data = sorted(st.session_state.class_data, key=lambda x: x["name"].lower())
    for s in sorted_class_data:
        name = s["name"]
        scores = s["scores"]
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

    if st.checkbox("➕ Add More Detailed Reports"):
        st.markdown("### Judgement & Recommendations Table")
        judgements = ["", "Perfect", "Excellent", "Very good", "Good", "Solid", "OK", "Disappointing", "Awful"]
        drop_options = ["No", "Ordinary", "Foundation"]

        summary_data = []
        for s in st.session_state.class_data:
            name = s['name']
            percentage = round(sum(s['scores']) / sum(max_scores) * 100, 2)
            cols = st.columns(3)
            cols[0].markdown(f"**{name} ({percentage}%)**")
            cols[1].selectbox("Judgement", judgements, key=f"judge_{name}")
            cols[2].selectbox("Recommend Drop", drop_options, key=f"drop_{name}")

        st.markdown("### 📄 Detailed Report Preview")
        detailed_reports = []
        sorted_class_data = sorted(st.session_state.class_data, key=lambda x: x["name"].lower())
        detailed_reports = []
        for s in sorted_class_data:
            name = s['name']
            scores = s['scores']
            percentage = round(sum(scores) / sum(max_scores) * 100, 2)
            indiv_percentages = [(s / max_scores[i]) * 100 for i, s in enumerate(scores)]
            df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
            df["Topic"] = df["Topic"].apply(merge_topic)
            df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")
            top_topics = df_sorted["Topic"].head(3).tolist()
            topic_text = "; ".join(top_topics)

            judgement = st.session_state.get(f"judge_{name}", "")
            drop = st.session_state.get(f"drop_{name}", "")
            comment = judgement_texts.get(judgement, "").format(name=name)
            drop_comment = drop_recommendations.get(drop, "").format(name=name)
            improvement = f"To improve this grade {name} needs to work on the following topics: {topic_text}."

            full_text = f"Name: {name} | Percentage: {percentage}%\n{comment} {drop_comment} {get_topic_intro(judgement, name, topic_text)}"
            detailed_reports.append(full_text)

        st.text(detailed_reports[0])
        st.download_button("📥 Download Detailed Reports", data="\n\n".join(detailed_reports), file_name="detailed_reports.txt", mime="text/plain")
        
if st.checkbox("📊 Show Class Analytics"):
    st.markdown("### Class Metrics")
    all_percentages = [round(sum(s["scores"]) / sum(max_scores) * 100, 2) for s in st.session_state.class_data if len(s["scores"]) == len(max_scores)]
    st.write(f"**Average:** {np.mean(all_percentages):.2f}%")
    st.write(f"**Median:** {np.median(all_percentages):.2f}%")
    st.write(f"**Max:** {np.max(all_percentages):.2f}%")
    st.write(f"**Min:** {np.min(all_percentages):.2f}%")

    struggling = [s["name"] for s in st.session_state.class_data if (sum(s["scores"]) / sum(max_scores)) * 100 < 40]
    if struggling:
        st.write("### 🚨 Students Needing Extra Help (< 40%)")
        for name in struggling:
            st.write(f"- {name}")

    topic_rank_counts = defaultdict(lambda: {"First": 0, "Second": 0, "Third": 0, "Total": 0})
    for student in st.session_state.class_data:
        scores = student["scores"]
        indiv_percentages = [(s / max_scores[i]) * 100 for i, s in enumerate(scores)]
        df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
        df["Topic"] = df["Topic"].apply(merge_topic)
        df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")

        added = 0
        seen = set()
        for label, (_, row) in zip(["First", "Second", "Third"], df_sorted.iterrows()):
            topic = row["Topic"]
            if topic not in seen:
                topic_rank_counts[topic][label] += 1
                topic_rank_counts[topic]["Total"] += 1
                seen.add(topic)
                added += 1
            if added == 3:
                break

    topic_df = pd.DataFrame([{
        "Topic": topic,
        "First": count["First"],
        "Second": count["Second"],
        "Third": count["Third"],
        "Total": count["Total"]
    } for topic, count in topic_rank_counts.items()])

    melted = topic_df.melt(id_vars="Topic", var_name="Rank", value_name="Count")
    fig = px.bar(melted, x="Topic", y="Count", color="Rank", title="Topics That Need the Most Work by Rank")
    st.plotly_chart(fig)