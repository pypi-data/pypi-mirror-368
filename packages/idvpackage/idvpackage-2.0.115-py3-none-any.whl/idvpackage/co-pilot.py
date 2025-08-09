import openai
import os

# Load your API key (ensure it's set in your environment or .env file)
openai.api_key = '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'


def refine_prompt(user_input: str) -> str:
    """Refines a vague user prompt and suggests enhancements."""
    system_msg = (
        "You are a helpful assistant that improves vague prompts. "
        "Rewrite the prompt clearly, ask if this matches the user's intent, "
        "and offer 2–3 suggestions to enhance it further."
    )
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Original prompt: {user_input}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

def generate_final_output(refined_prompt: str) -> str:
    """Uses the final, user-approved prompt to generate actual output."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": refined_prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

def run_prompt_refiner():
    print("🧠 Welcome to the Prompt Refinement Assistant")
    print("Type your vague prompt below. Type 'yes' when satisfied, or 'exit' to quit.\n")

    original_input = input("You: ")
    if original_input.lower() == "exit":
        return

    refined_prompt = original_input

    while True:
        print("\n🤖 Refining your prompt...")
        refinement = refine_prompt(refined_prompt)
        print(f"\n{refinement}")

        followup = input("\nYou (edit it, or type 'yes' to run it): ")
        if followup.strip().lower() == "yes":
            break
        elif followup.strip().lower() == "exit":
            print("Goodbye!")
            return
        else:
            refined_prompt += " " + followup.strip()

    print("\n🎯 Final prompt approved. Generating result...\n")
    result = generate_final_output(refined_prompt)
    print(f"✅ Output:\n{result}")

if __name__ == "__main__":
    run_prompt_refiner()
