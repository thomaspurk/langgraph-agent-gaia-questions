verification_prompt = (
    f"Question: \n"
    f"Proposed Answer: \n\n"
    "Evaluate the answer against all the criteria in the question. If it's accurate and complete, return it as-is. "
    "If it's incorrect, update the answer."
)

print(type(verification_prompt))