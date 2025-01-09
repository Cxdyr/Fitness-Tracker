import re

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'   # Format can be a-z  A-Z 0-9 combinations followed by @ a-zA A-Z 0-9 followed by .  a-z A-Z  also acounting for special chars in emails 
    return re.match(email_regex, email) is not None