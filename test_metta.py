import os

def check_balanced_parentheses(filepath):
    """Checks if parentheses are balanced in a MeTTa file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    for i, char in enumerate(content):
        if char == '(':
            stack.append((char, i))
        elif char == ')':
            if not stack:
                return False, f"Unmatched closing parenthesis at index {i}"
            stack.pop()
            
    if stack:
        char, i = stack[-1]
        return False, f"Unmatched opening parenthesis at index {i}"
    
    return True, "Parentheses balanced successfully."

def run_metta_syntax_check():
    files_to_check = [
        "src/logic/scene1_archetypes.metta",
        "src/logic/biocentric_rules.metta"
    ]
    
    print("🦉 Running TQFAI MeTTa Syntax & Structure Check...\n")
    
    all_passed = True
    for filepath in files_to_check:
        print(f"Checking: {filepath}")
        if not os.path.exists(filepath):
            print(f"  ❌ ERROR: File not found at {filepath}\n")
            all_passed = False
            continue
            
        is_balanced, message = check_balanced_parentheses(filepath)
        if is_balanced:
            print(f"  ✅ SYNTAX OK: {message}")
        else:
            print(f"  ❌ SYNTAX ERROR: {message}")
            all_passed = False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"  📊 Total lines: {line_count}\n")
        
    if all_passed:
        print("🎉 All MeTTa files passed basic structural checks!")
    else:
        print("⚠️ Some files require fixes before running in the AtomSpace.")

if __name__ == "__main__":
    run_metta_syntax_check()
