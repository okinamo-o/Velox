import sys
import re

def validate_icon_content(content):
    lines = content.strip().split('\n')
    valid_commands = {
        'CANVAS_DIMENSIONS', 'FILL_RULE_NONZERO', 'NEW_PATH', 'PATH_COLOR_ALPHA',
        'PATH_COLOR_ARGB', 'PATH_MODE_CLEAR', 'STROKE', 'CAP_SQUARE',
        'MOVE_TO', 'R_MOVE_TO', 'ARC_TO', 'R_ARC_TO', 'LINE_TO', 'R_LINE_TO',
        'H_LINE_TO', 'R_H_LINE_TO', 'V_LINE_TO', 'R_V_LINE_TO',
        'CUBIC_TO', 'R_CUBIC_TO', 'CUBIC_TO_SHORTHAND',
        'QUADRATIC_TO', 'R_QUADRATIC_TO', 'QUADRATIC_TO_SHORTHAND', 'R_QUADRATIC_TO_SHORTHAND',
        'CIRCLE', 'OVAL', 'ROUND_RECT', 'CLOSE', 'CLIP', 'FLIPS_IN_RTL'
    }
    
    in_rep = False
    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.partition('//')[0].strip()
        if not line:
            continue
        parts = [p.strip().rstrip('f') for p in line.split(',') if p.strip()]
        if not parts:
            continue
        cmd = parts[0]
        if cmd not in valid_commands:
            return False, f"Line {line_num}: Unknown command '{cmd}' in '{raw_line}'"
        if cmd == 'CANVAS_DIMENSIONS':
            in_rep = True
    if not in_rep:
        return False, "Missing CANVAS_DIMENSIONS"
    return True, "Valid"

if __name__ == '__main__':
    print("Validator ready")
