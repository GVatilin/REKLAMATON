from llm_client import call_llm

def profile_bio_advisor_agent(profile_bio: str):
    system_instruction = ""
    prompt_text = ""

    return call_llm(prompt_text, system_instruction)

