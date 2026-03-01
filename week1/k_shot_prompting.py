import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are an AI assistant whose only task is to reverse the input word. 

CRITICAL INSTRUCTION:
You must ONLY output the reversed word. Do not include anyting, only the reversed word.

example for the word your input and output should look like this:
Input: 'hakim'
Output: 'mikah'
Input: 'status'
Output: 'sutats'
Input: 'https'
Output: 'sptth'
Input: 'read'
Output: 'dear'
Input: 'input'
Output: 'tupni'
Input: 'turu'
Output: 'urut'
Input: 'nazmi'
Output: 'imzan'
Input: 'backspace'
Output: 'esapskcab'
Input: 'raymond'
Output: 'dnomyar'
Input: 'king'
Output: 'gnik'
Input: 'calculator'
Output: 'rotaluclac'
Input: 'thingamajig'
Output: 'gijamagniht'
Input: 'sutatsptth'
Output: 'httpstatus'
Input: 'ptth'
Output: 'http'
Input: 'sptth'
Output: 'https'
input: 'sutats'
Output: 'status'

"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)