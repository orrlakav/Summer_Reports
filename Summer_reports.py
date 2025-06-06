import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import defaultdict
import uuid

# --- Session State Initialization ---
if "class_data" not in st.session_state:
    st.session_state.class_data = []
if "student_counter" not in st.session_state:
    st.session_state.student_counter = 0

# --- Predefined exams ---
predefined_exams = {
    "5th Year Higher": {
        "max_scores": [30.0] * 10,
        "topics": [
            "Patterns and Sequences", "Coordinate Geometry of the Circle", "Coordinate Geometry of the Line",
            "Logs and Indices", "Financial Maths", "Algebra", "Patterns and Sequences",
            "Complex Numbers", "Trigonometry", "Trigonometry"
        ]
    },
    "5th Year Ordinary": {
        "max_scores": [30.0, 30.0, 30.0, 30.0, 30.0, 50.0, 20.0, 30.0],
        "topics": [
            "Solving equations", "Coordinate Geometry of the Circle", "Coordinate Geometry of the Line",
            "Complex Numbers", "Patterns and Sequences", "Patterns and Sequences", "Algebra", "Fractions and Indices"
        ]
    },
    "2nd Year Higher": {
        "max_scores": [20.0, 25.0, 35.0, 35.0, 35.0, 20.0, 20.0, 25.0, 10.0, 15.0],
        "topics": [
            "Averages", "Factorising and inequalities", "Statistical charts", "Coordinate Geometry", "Area and Volume",
            "Financial Maths", "Factorising and solving equations", "Writing equations", "Area and perimeter", "Number"
        ]
    },
    "2nd Year Ordinary": {
        "max_scores": [25.0, 25.0, 20.0, 15.0, 10.0, 10.0, 25.0, 25.0, 10.0, 20.0, 15.0],
        "topics": [
            "Number", "Sets", "Algebra", "Financial Maths", "Worded problems", "Ratios and compound interest",
            "Financial Maths", "Financial Maths", "Coordinate Geometry of the line",
            "Statistics (measures of average)", "Statistical diagrams"
        ]
    },
    "1st Year": {
        "max_scores": [10.0, 10.0, 15.0, 15.0, 15.0, 30.0, 10.0, 20.0, 20.0, 10.0, 15.0, 20.0, 25.0, 10.0, 15.0],
        "topics": [
            "Number", "Number", "Angle Facts", "Simplifying algebraic expressions", "Probability", "Sets",
            "Worded problems", "Solving Equations", "Expanding Brackets", "Worded problems",
            "Coordinate Geometry of the Line", "Area, Perimeter and Volume", "Ratio and Proportion",
            "Coordinate Geometry", "Statistics"
        ]
    }
}

MERGE_TOPICS = {
    frozenset(["Area and Volume", "Area and perimeter"]): "Area, perimeter and volume",
    frozenset(["Statistics (measures of average)", "Statistical diagrams"]): "Statistics",
    frozenset(["Financial Maths"]): "Financial Maths",
    frozenset(["Trigonometry"]): "Trigonometry",
    frozenset(["Worded problems"]): "Worded problems"
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
    "OK": "While this is an OK result for {name}, there's definitely room to improve. Increased effort in class and at home will help them achieve a grade they can be truly proud of.",
    "Disappointing": "This is a disappointing outcome for {name}. They need to make a more sustained effort both in class and independently to see improvement.",
    "Awful": "{name} must make a much greater commitment to their studies if they want to earn a result they can be proud of next year."
}

drop_recommendations = {
    "Foundation": "{name} has found Maths particularly challenging this year. It is recommended they consider Foundation Level Maths next year, which may better match their current ability and help build key life and workplace skills.",
    "Ordinary": "{name} has struggled significantly with the demands of Higher Level Maths. It may now be appropriate for them to transition to Ordinary Level, where they can work at a more suitable pace and address learning gaps more effectively.",
    "No": ""
}

first_year_recommendations = {
    "Ordinary": "{name} has found Maths difficult this year. Ordinary Level is recommended for next year, where the pace will be more manageable and suited to their current needs. This should help rebuild confidence and strengthen core understanding.",
    "Higher (borderline)": "Higher Level is recommended for {name} next year. The course will include more advanced Algebra and problem-solving, which can be challenging. With consistent effort and the right support, {name} can rise to meet these demands and make strong progress in their mathematical understanding.",
    "Higher (confident)": "Higher Level is recommended for {name} next year. Some topics will be challenging, but with consistent effort and focus, {name} will be well capable of handling them and continuing to make strong progress."
}

def get_topic_intro(judgement, name, topic_list):
    if judgement == "Perfect":
        return f"The only areas where marks were lost in this exam were: {topic_list}."
    elif judgement in ["Excellent", "Very good"]:
        return f"To further improve this grade, {name} should focus on the following topics: {topic_list}."
    else:
        return f"To improve this grade {name} needs to work on the following topics: {topic_list}."


# --- UI: Exam setup ---
st.title("Student Report Generator")
exam_type = st.selectbox("Select Exam Type", list(predefined_exams.keys()) + ["Custom"], key="selected_exam")

max_scores, topics = [], []

if exam_type == "Custom":
    num_questions = st.number_input("How many questions in the exam?", min_value=1, max_value=50, step=1)
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

    show_inputs = st.checkbox("✏️ Show/edit marks and topics", value=False)
    if show_inputs:
        for i in range(num_questions):
            col1, col2 = st.columns(2)
            with col1:
                score = st.number_input(f"Max score for Q{i+1}", value=float(default_max_scores[i]), min_value=1.0, step=1.0, key=f"edit_ms{i}")
            with col2:
                topic = st.text_input(f"Topic for Q{i+1}", value=default_topics[i], key=f"edit_tp{i}")
            max_scores.append(float(score))
            topics.append(topic)
    else:
        max_scores = default_max_scores
        topics = default_topics

# --- UI: Student form ---
with st.form("student_entry"):
    student_name = st.text_input("Student Name")
    scores = [
        st.number_input(
            f"Score for Q{i+1} ({topics[i]})",
            min_value=0.0,
            max_value=max_scores[i],
            step=0.5,
            key=f"score_input_{i}"
        ) for i in range(len(max_scores))
    ]
    submitted = st.form_submit_button("Add Student")
    if submitted and student_name.strip():
        st.session_state.class_data.append({
            "id": str(uuid.uuid4()),
            "name": student_name.strip(),
            "scores": scores
        })
        #st.experimental_rerun()

# --- UI: Edit/Delete Students ---
if st.session_state.class_data:
    st.markdown("### ✏️ Edit Student Entries")
    for i, student in enumerate(st.session_state.class_data):
        with st.expander(f"Edit: {student['name']} ({round(sum(student['scores']) / sum(max_scores) * 100, 2)}%)"):
            new_name = st.text_input("Student Name", value=student["name"], key=f"name_edit_{i}")
            new_scores = []
            for j in range(len(max_scores)):
                score = st.number_input(
                    f"Score for Q{j+1} ({topics[j]})",
                    min_value=0.0,
                    max_value=max_scores[j],
                    value=student["scores"][j],
                    step=0.5,
                    key=f"score_edit_{i}_{j}"
                )
                new_scores.append(score)
            if st.button("💾 Save Changes", key=f"save_edit_{i}"):
                student["name"] = new_name
                student["scores"] = new_scores
                #st.experimental_rerun()

    with st.expander("🗑️ Delete Students"):
        delete_ids = []
        for student in st.session_state.class_data:
            col1, col2 = st.columns([3, 1])
            col1.write(student["name"])
            if col2.checkbox("Delete", key=f"delete_{student['id']}"):
                delete_ids.append(student["id"])
        if delete_ids and st.button("❌ Confirm Deletion"):
            st.session_state.class_data = [s for s in st.session_state.class_data if s['id'] not in delete_ids]
            #st.experimental_rerun()

# --- Display Class Data ---
if st.session_state.class_data:
    st.markdown("### 📊 Current Class Data")
    df_display = pd.DataFrame([{
        "Name": student["name"],
        **{f"Q{i+1}": student["scores"][i] for i in range(len(student["scores"]))},
        "Total": sum(student["scores"]),
        "%": round((sum(student["scores"]) / sum(max_scores)) * 100, 2)
    } for student in st.session_state.class_data])
    st.dataframe(df_display)
    st.download_button(
        "⬇️ Download Class Data",
        data=df_display.to_csv(index=False).encode("utf-8"),
        file_name="class_data.csv",
        mime="text/csv"
    )

    st.markdown("### 📝 Basic Report Preview")
    sorted_class_data = sorted(st.session_state.class_data, key=lambda x: x["name"].lower())
    basic_reports = []

    for student in sorted_class_data:
        name = student["name"]
        scores = student["scores"]
        percentage = round(sum(scores) / sum(max_scores) * 100, 2)
        indiv_percentages = [(score / max_scores[i]) * 100 for i, score in enumerate(scores)]
        df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
        df["Topic"] = df["Topic"].apply(merge_topic)
        df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")
        top_topics = df_sorted["Topic"].head(3).tolist()
        topic_text = "; ".join(top_topics)
        report = (
            f"Name: {name}\n"
            f"Percentage: {percentage}%\n"
            f"To improve this grade {name} needs to work on the following topics: {topic_text}."
        )
        basic_reports.append(report)

    if basic_reports:
        st.text(basic_reports[0])
        st.download_button(
            "📅 Download Basic Reports",
            data="\n\n".join(basic_reports),
            file_name="basic_reports.txt",
            mime="text/plain"
        )

    if st.checkbox("➕ Add More Detailed Reports"):
        st.markdown("### Judgement & Recommendations")
        judgements = ["", "Perfect", "Excellent", "Very good", "Good", "Solid", "OK", "Disappointing", "Awful"]
        drop_options = ["No", "Ordinary", "Foundation"]
        level_options = ["", "Higher (confident)", "Higher (borderline)", "Ordinary"]

        for student in st.session_state.class_data:
            student_id = id(student)
            name = student['name']
            percentage = round(sum(student['scores']) / sum(max_scores) * 100, 2)
            cols = st.columns(3)
            cols[0].markdown(f"**{name} ({percentage}%)**")
            cols[1].selectbox("Judgement", judgements, key=f"judge_{student_id}")
            if exam_type == "1st Year":
                cols[2].selectbox("Recommended Level", level_options, key=f"level_{student_id}")
            else:
                cols[2].selectbox("Recommend Drop", drop_options, key=f"drop_{student_id}")

        st.markdown("### 📄 Detailed Report Preview")
        detailed_reports = []
        for student in sorted_class_data:
            student_id = id(student)
            name = student['name']
            scores = student['scores']
            percentage = round(sum(scores) / sum(max_scores) * 100, 2)
            indiv_percentages = [(score / max_scores[i]) * 100 for i, score in enumerate(scores)]
            df = pd.DataFrame({"Topic": topics, "Percentage": indiv_percentages})
            df["Topic"] = df["Topic"].apply(merge_topic)
            df_sorted = df.groupby("Topic", as_index=False).mean().sort_values(by="Percentage")
            top_topics = df_sorted["Topic"].head(3).tolist()
            topic_text = "; ".join(top_topics)

            judgement = st.session_state.get(f"judge_{student_id}", "")
            comment = judgement_texts.get(judgement, "").format(name=name)
            if exam_type == "1st Year":
                level = st.session_state.get(f"level_{student_id}", "")
                level_comment = first_year_recommendations.get(level, "").format(name=name)
            else:
                drop = st.session_state.get(f"drop_{student_id}", "")
                level_comment = drop_recommendations.get(drop, "").format(name=name)

            full_text = (
                f"Name: {name}\n"
                f"Percentage: {percentage}%\n"
                f"{comment} {level_comment} {get_topic_intro(judgement, name, topic_text)}"
            )
            detailed_reports.append(full_text)

        if detailed_reports:
            st.text(detailed_reports[0])
            st.download_button(
                "📅 Download Detailed Reports",
                data="\n\n".join(detailed_reports),
                file_name="detailed_reports.txt",
                mime="text/plain"
            )

# --- Analytics ---
if st.checkbox("📊 Show Class Analytics"):
    st.markdown("### Class Metrics")
    all_percentages = [round(sum(s["scores"]) / sum(max_scores) * 100, 2) for s in st.session_state.class_data]
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
        indiv_percentages = [(score / max_scores[i]) * 100 for i, score in enumerate(scores)]
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