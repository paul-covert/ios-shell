def pre_mutation(context):
    line = context.current_source_line
    if any(name in context.filename for name in ["keys.py", "regex.py", "sections.py"]):
        context.skip = True
    elif any(text in line for text in ["logging", "raise"]):
        context.skip = True
