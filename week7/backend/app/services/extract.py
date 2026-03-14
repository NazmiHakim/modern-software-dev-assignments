import re

def extract_action_items(text: str) -> list[str]:
    """
    Extracts action items from text using pattern recognition.
    Patterns include:
    - Checkboxes: [ ] or [x]
    - Keywords: TODO:, Action:, Task:, Fix:, Implement:
    - Phrases: "need to", "must", "should"
    - Lines ending with "!"
    """
    patterns = [
        r"(?i)\[[ xX]\]",  # Markdown checkboxes
        r"(?i)\b(todo|action|task|fix|implement|due)\b",  # Keywords
        r"(?i)\b(need to|must|should)\b",  # Imperative phrases
    ]
    
    results: list[str] = []
    # Strip bullet points and whitespace
    raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = [re.sub(r"^[ \t]*[-*+][ \t]*", "", line).strip() for line in raw_lines]
    
    for line in lines:
        # Check explicit patterns
        matched = False
        for pattern in patterns:
            if re.search(pattern, line):
                results.append(line)
                matched = True
                break
        
        # Fallback for exclamation marks (legacy logic)
        if not matched and line.endswith("!"):
            results.append(line)
            
    # Return as list, sorted to ensure deterministic output
    return sorted(list(set(results)))


