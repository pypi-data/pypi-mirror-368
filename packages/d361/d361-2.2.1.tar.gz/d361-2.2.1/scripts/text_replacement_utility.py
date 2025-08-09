#!/usr/bin/env python3
# this_file: fix_function.py

import re

# Read the file
with open("d361/docs/summarize.py", "r") as f:
    content = f.read()

# Define the new function
new_function = '''def clean_llm_output(text: str) -> str:
    """
    Clean LLM output by extracting content between <output> and </output> tags.
    Also handles <o> and </o> tags for backward compatibility.
    If tags are not found, returns the original text.

    Args:
        text: The text to clean

    Returns:
        Cleaned text with only the content between output tags, or original text if tags not found
    """
    # Check for <output> tags
    output_tag_start = "<output>"
    output_tag_end = "</output>"
    start_idx = text.find(output_tag_start)
    
    if start_idx >= 0:
        content_start = start_idx + len(output_tag_start)
        end_idx = text.find(output_tag_end, content_start)
        if end_idx >= 0:
            return text[content_start:end_idx].strip()
    
    # Check for <o> tags as fallback
    o_tag_start = "<o>"
    o_tag_end = "</o>"
    start_idx = text.find(o_tag_start)
    
    if start_idx >= 0:
        content_start = start_idx + len(o_tag_start)
        end_idx = text.find(o_tag_end, content_start)
        if end_idx >= 0:
            return text[content_start:end_idx].strip()
    
    # If no tags found, return the original text
    return text.strip()'''

# Replace the function
pattern = r"def clean_llm_output.*?return text\.strip\(\)"
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

# Write the file
with open("d361/docs/summarize.py", "w") as f:
    f.write(content)

print("Function updated successfully")
