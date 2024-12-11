import streamlit as st
import os
import openai
from dotenv import load_dotenv
from llama_index.core.llama_pack import download_llama_pack
from resume_screener_pack.llama_index.packs.resume_screener import ResumeScreenerPack

load_dotenv()
openai.api_key = 'sk-C6HMVglrw9iNK1bFO3xQrQaNrMzfFZ-BbySpFBckywT3BlbkFJl83p5Izy-e6y4nMdIthxQ2U67jEi8WJhyj62rAp4AA'



def rate_resume(criteria_decisions, overall_decision):
    rate_prompt = f"""
    Given the criteria decisions and overall decision, please rate the resume as percentage match based matched criteria elements:
    
    Criteria Decisions:
    {criteria_decisions}
    
    Overall Decision:
    {overall_decision}
    
    Please provide a percentage rating and a brief explanation for your rating:
    
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for rating resumes.",
            },
            {"role": "user", "content": rate_prompt},
        ],
    )

    return response.choices[0].message.content

#BackGround

css="""
<style>
    [data-testid="stForm"] {
        background: White;
    }
</style>
"""
st.write(css, unsafe_allow_html=True)

# Logo
col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image('IntervuLogo-Reduced.png')

with col3:
    st.write(' ')


st.markdown("<h2 style='text-align: center; color: grey;'>Resume Analysis System <br> (RAS)</h2>", unsafe_allow_html=True)


#JD and criteria Columns
col1, col2 = st.columns(2)
with col1:
    job_description = st.text_area("Job Description", "")
with col2:
    criteria = st.text_area("Selection Criteria (One per line)", "")

#CV input
uploaded_file = st.file_uploader("Upload the Resume File", type=["pdf"])


# Screen Resume Button
if (
    st.button("Screen Resume")
    and uploaded_file is not None
    and job_description
    and criteria
):
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    criteria_list = [c.strip() for c in criteria.split("\n") if c.strip()]

    resume_screener = ResumeScreenerPack(
        job_description=job_description,
        criteria=criteria_list,
    )

    response = resume_screener.run(resume_path="temp_resume.pdf")

    st.subheader("Screening Resume")

    decisions = [
        {
            "title": f"Criterion {i+1}",
            "reasoning": cd.reasoning,
            "decision": cd.decision,
        }
        for i, cd in enumerate(response.criteria_decisions)
    ]
    decisions.append(
        {
            "title": "Overall Decision",
            "reasoning": response.overall_reasoning,
            "decision": response.overall_decision,
        }
    )

    decision_summary = []
    for decision in decisions:
        st.markdown(f"#### {decision['title']}")
        st.write(decision["reasoning"])
        st.write(f"Decision: {decision['decision']}")

        decision_summary.extend(
            [
                decision["title"],
                decision["reasoning"],
                f"Decision: {decision['decision']}",
                "",
            ]
        )

    decision_summary = "\n".join(decision_summary).strip()


    st.subheader("Resume Rating")
    rating_results = rate_resume(response.criteria_decisions, response.overall_decision)
    st.markdown(rating_results)

    os.remove("temp_resume.pdf")
else:
    st.info(
        "Please upload a resume file, enter job description and criteria, then click 'Screen Resume'."
    )
