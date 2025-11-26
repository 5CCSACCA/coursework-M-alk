import re
import logging

logger = logging.getLogger(__name__)


def is_low_quality_response(content: str) -> bool:
    if not content or len(content.strip()) < 3:
        return True
    
    content_lower = content.lower()
    lines = content.split('\n')
    
    question_lines = sum(1 for line in lines if line.strip().endswith('?') and len(line.strip()) < 100)
    if question_lines >= 3 and len(lines) < 20:
        logger.warning("Detected question-spamming pattern")
        return True
    
    numbered_lines = sum(1 for line in lines if line.strip().startswith('- ') or 
                        (line.strip() and line.strip()[0].isdigit() and 
                         (line.strip().startswith('1') or line.strip().startswith('2'))))
    if numbered_lines > 5 and len(lines) < 15:
        return True
    
    if '|' in content and ('comment' in content_lower or 
                           any(char.isdigit() for char in content if '-' in content)):
        if content.count('|') >= 2 and ('comment' in content_lower or 
                                        any(part.strip().count('-') == 2 for part in content.split('|'))):
            return True
    
    return False


def clean_response(content: str, prompt: str = "") -> str:
    content = content.strip()
    
    a_marker_match = re.search(r'(?:^|\n)(?:A:|Answer:)\s*', content, re.IGNORECASE)
    if a_marker_match:
        content = content[a_marker_match.end():].strip()
    
    if prompt and len(prompt) > 5:
        prompt_clean = prompt.strip()
        if content.startswith(prompt_clean):
            content = content[len(prompt_clean):].strip()
        
        first_line = content.split('\n')[0]
        if first_line in prompt_clean or prompt_clean in first_line:
             pass

    content = re.sub(r'^\s*\|\s*\d{1,2}-\d{1,2}-\d{4}\s*\|\s*\d+\s*[Cc]omments?\s*', '', content)
    
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and not (
            line_stripped.startswith('- ') and len(line_stripped) < 10 or
            (line_stripped.count('|') >= 2 and 'comment' in line_stripped.lower()) or
            (line_stripped.isdigit() and len(line_stripped) < 3) or
            (len(line_stripped) < 5 and '?' in line_stripped)
        ):
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines).strip()
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    
    return content.strip()

