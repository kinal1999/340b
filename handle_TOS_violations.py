from openai import OpenAI
import streamlit as st
def TOS_violations_in_text(input, client):
    categories_set = moderation_response_categories(input, client)
    violations = interpret_response(categories_set)
    return violations
def moderation_response_categories(input, client):
    response = client.moderations.create(
        input=input
    )
    results = response.results[0].categories.model_dump()
    categories_set = set()
    for category in results:
        if results[category]:
            categories_set.add(category)
    return categories_set
def interpret_response(categories_set):
    serious_violation_categories = set(["harassment_threatening", "harassment-threatening", "hate-threatening", "hate_threatening", "sexual_minors", "sexual/minors"])
    violation_categories = set(["harassment", "sexual", "hate"])
    critical_self_harm = set(["self_harm_instructions", "self-harm/instructions"])
    self_harm = set(["self_harm", "self-harm", "self-harm/intent", "self_harm_intent"])

    violations = set()
    if len(categories_set.intersection(critical_self_harm)) > 0:
        violations.add("critical_self_harm")
    elif len(categories_set.intersection(self_harm)) > 0:
        violations.add("self_harm")
   
    if len(categories_set.intersection(serious_violation_categories)) > 0:
        violations.add("serious_violation")
    elif len(categories_set.intersection(violation_categories)) > 0:
        violations.add("violation")
    return violations

def handle_TOS_violations(violations):
    CRITICAL_SELF_HARM_ERROR_MESSAGE = "I'm really concerned about what you're going through. It's brave to \
            express these feelings, but it's also important to talk to someone who \
            can offer real help right now. Whether it's a mental health professional \
            or a crisis line, reaching out is a strong and positive step. You're \
            not alone in this."
    SELF_HARM_WARNING_MESSAGE = "I hear that you're in a lot of pain, and that's okay to feel. But let's try \
            to find a healthier way to deal with these tough emotions. Talking to a mental \
            health professional can be incredibly helpful. It's a sign of strength, not \
            weakness, to seek support. Remember, it's okay to ask for help."
    SERIOUS_VIOLATION_ERROR_MESSAGE = "This message seems to contain harmful content that does not \
            align with our content policy. It's important to communicate \
            respectfully, even when discussing difficult topics. Please revise \
            and retype your message to adhere to our standards."
    VIOLATION_WARNING_MESSAGE = "Your message might not align with our community guidelines. \
            We encourage constructive and respectful dialogue. Please \
            revise and retype your message to ensure it's in line with our standards."    
    stop_flag = False
    if "critical_self_harm" in violations:
        st.error(CRITICAL_SELF_HARM_ERROR_MESSAGE)
        stop_flag = True
        st.stop()
    elif "self_harm" in violations:
        st.warning(SELF_HARM_WARNING_MESSAGE)
        
    if "serious_violation" in violations:
        st.error(SERIOUS_VIOLATION_ERROR_MESSAGE)
        stop_flag = True
    elif "violation" in violations:
        st.warning(VIOLATION_WARNING_MESSAGE)
        stop_flag = True
    if stop_flag:
        st.stop()
