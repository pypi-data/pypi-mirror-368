from cxglearner.utils.utils_config import DefaultConfigs
from cxglearner.config.config import Config
from cxglearner.utils.utils_log import init_logger
from cxglearner.parser.parser import Parser
from cxglearner.utils.utils_cxs import convert_slots_to_str

import argparse
import sys
import os
import curses
import textwrap


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_results_fullscreen(input_text, tokens, upos, xpos, cxs_table_data, parser, logger):
    """Display parsing results in a full-screen htop-like interface"""
    def draw_interface(stdscr):
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Header
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Input text
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Section titles
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal text
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Highlights
        
        # Configure curses
        curses.curs_set(0)  # Hide cursor
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)  # Enable mouse events
        
        # Get screen dimensions
        height, width = stdscr.getmaxyx()
        
        # Scrolling state
        scroll_pos = 0
        max_scroll = 0
        
        while True:
            stdscr.clear()
            
            # Calculate content height for scrolling
            content_lines = []
            
            # Header content (will be displayed separately as fixed header)
            header_lines = [
                ("header", "CxG Parser v1.3.3 - Full Screen Results", curses.A_BOLD | curses.color_pair(1)),
                ("separator", "=" * width, curses.color_pair(1)),
                ("empty", "", 0)
            ]
            header_height = len(header_lines)
            
            # Input text section
            input_title = "RAW Sentence"
            centered_input_title = input_title.center(width)
            content_lines.append(("section", centered_input_title, curses.A_BOLD | curses.color_pair(3)))
            
            # Create table for input text (centered and aligned with other tables)
            max_table_width = width - 10  # Reserve space for centering, same as other tables
            content_width = max_table_width - 4  # Subtract 4 for borders
            
            # Wrap input text to fit within content width
            wrapped_input = textwrap.fill(f'"{input_text}"', content_width)
            input_lines = wrapped_input.split('\n')
            
            # Calculate actual table width based on longest line
            actual_content_width = max(len(line) for line in input_lines)
            actual_content_width = min(actual_content_width, content_width)
            table_width = actual_content_width + 4  # Add 4 for borders
            
            # Top border (centered)
            input_top_border = "+" + "-" * (table_width - 2) + "+"
            centered_input_top_border = input_top_border.center(width)
            content_lines.append(("text", centered_input_top_border, curses.color_pair(4)))
            
            # Content rows (centered)
            for line in input_lines:
                padded_line = f"| {line:<{table_width - 4}} |"
                centered_input_line = padded_line.center(width)
                content_lines.append(("text", centered_input_line, curses.color_pair(2)))
            
            # Bottom border (centered)
            input_bottom_border = "+" + "-" * (table_width - 2) + "+"
            centered_input_bottom_border = input_bottom_border.center(width)
            content_lines.append(("text", centered_input_bottom_border, curses.color_pair(4)))
            
            content_lines.append(("empty", "", 0))
            
            # Encoding results section
            encoding_title = f"Encoding Results ({len(tokens)} tokens)"
            centered_encoding_title = encoding_title.center(width)
            content_lines.append(("section", centered_encoding_title, curses.A_BOLD | curses.color_pair(3)))
            
            # Token table with individual cell borders (centered)
            if tokens:
                # Calculate optimal column width based on terminal width
                max_table_width = width - 10  # Reserve space for centering
                min_col_width = 8  # Minimum column width
                max_tokens_per_line = min(len(tokens), max(1, max_table_width // (min_col_width + 3)))  # +3 for borders
                
                # Split tokens into chunks if they don't fit on one line
                token_chunks = [tokens[i:i+max_tokens_per_line] for i in range(0, len(tokens), max_tokens_per_line)]
                upos_chunks = [upos[i:i+max_tokens_per_line] for i in range(0, len(upos), max_tokens_per_line)] if upos else []
                xpos_chunks = [xpos[i:i+max_tokens_per_line] for i in range(0, len(xpos), max_tokens_per_line)] if xpos else []
                
                for chunk_idx, token_chunk in enumerate(token_chunks):
                    start_idx = chunk_idx * max_tokens_per_line
                    num_cols = len(token_chunk)
                    
                    # Calculate column width for this chunk
                    col_width = max(min_col_width, (max_table_width - (num_cols + 1)) // num_cols)
                    
                    # Calculate actual table width
                    actual_table_width = num_cols * col_width + (num_cols + 1)
                    
                    # Top border (centered)
                    top_border = "+" + "+".join("-" * col_width for _ in range(num_cols)) + "+"
                    centered_top_border = top_border.center(width)
                    content_lines.append(("text", centered_top_border, curses.color_pair(4)))
                    
                    # ID row (centered)
                    ids = [str(start_idx + i + 1) for i in range(num_cols)]
                    id_cells = [f"{id:^{col_width}}" for id in ids]
                    id_row = "|" + "|".join(id_cells) + "|"
                    centered_id_row = id_row.center(width)
                    content_lines.append(("text", centered_id_row, curses.A_BOLD | curses.color_pair(4)))
                    
                    # Separator line between ID and Token (centered)
                    separator = "+" + "+".join("-" * col_width for _ in range(num_cols)) + "+"
                    centered_separator = separator.center(width)
                    content_lines.append(("text", centered_separator, curses.color_pair(4)))
                    
                    # Token row (centered)
                    token_cells = [f"{token[:col_width]:^{col_width}}" for token in token_chunk]
                    token_row = "|" + "|".join(token_cells) + "|"
                    centered_token_row = token_row.center(width)
                    content_lines.append(("text", centered_token_row, curses.color_pair(4)))
                    
                    # UPOS row (centered)
                    if upos_chunks and chunk_idx < len(upos_chunks):
                        # Separator line between Token and UPOS
                        content_lines.append(("text", centered_separator, curses.color_pair(4)))
                        
                        upos_chunk = upos_chunks[chunk_idx]
                        upos_cells = [f"{pos:^{col_width}}" for pos in upos_chunk]
                        upos_row = "|" + "|".join(upos_cells) + "|"
                        centered_upos_row = upos_row.center(width)
                        content_lines.append(("text", centered_upos_row, curses.color_pair(4)))
                    
                    # XPOS row (centered)
                    if xpos_chunks and chunk_idx < len(xpos_chunks):
                        # Separator line between UPOS and XPOS
                        content_lines.append(("text", centered_separator, curses.color_pair(4)))
                        
                        xpos_chunk = xpos_chunks[chunk_idx]
                        xpos_cells = [f"{pos:^{col_width}}" for pos in xpos_chunk]
                        xpos_row = "|" + "|".join(xpos_cells) + "|"
                        centered_xpos_row = xpos_row.center(width)
                        content_lines.append(("text", centered_xpos_row, curses.color_pair(4)))
                    
                    # Bottom border (centered)
                    bottom_border = "+" + "+".join("-" * col_width for _ in range(num_cols)) + "+"
                    centered_bottom_border = bottom_border.center(width)
                    content_lines.append(("text", centered_bottom_border, curses.color_pair(4)))
                    
                    # Add separator between chunks if there are multiple
                    if chunk_idx < len(token_chunks) - 1:
                        content_lines.append(("empty", "", 0))
            
            content_lines.append(("empty", "", 0))
            
            # CxS results section with complete table display (centered)
            if cxs_table_data and len(cxs_table_data) > 1:
                data_count = len(cxs_table_data) - 1
                cxs_title = f"CxS Parsing Results ({data_count} structures)"
                centered_cxs_title = cxs_title.center(width)
                content_lines.append(("section", centered_cxs_title, curses.A_BOLD | curses.color_pair(3)))
                
                # Calculate column widths for CxS table
                headers = cxs_table_data[0]
                data_rows = cxs_table_data[1:]
                
                # Calculate optimal widths with more balanced proportions
                max_table_width = width - 10  # Reserve space for centering
                
                # Set proportional widths
                id_width = max(len(str(headers[0])), max(len(str(row[0])) for row in data_rows), 8)
                pos_width = max(len(str(headers[2])), max(len(str(row[2])) for row in data_rows), 15)
                
                # Slot info gets remaining width (with reasonable minimum)
                remaining_width = max_table_width - id_width - pos_width - 4  # 4 for borders
                slot_width = max(35, remaining_width)
                
                # Ensure total width doesn't exceed max
                total_table_width = id_width + slot_width + pos_width + 4
                if total_table_width > max_table_width:
                    # Reduce slot width to fit
                    slot_width = max_table_width - id_width - pos_width - 4
                    slot_width = max(30, slot_width)  # Minimum slot width
                
                # Top border for CxS table (centered)
                cxs_top_border = f"+{'-' * id_width}+{'-' * slot_width}+{'-' * pos_width}+"
                centered_cxs_top_border = cxs_top_border.center(width)
                content_lines.append(("text", centered_cxs_top_border, curses.color_pair(4)))
                
                # Header row (centered)
                header_row = f"|{headers[0]:^{id_width}}|{headers[1]:^{slot_width}}|{headers[2]:^{pos_width}}|"
                centered_header_row = header_row.center(width)
                content_lines.append(("text", centered_header_row, curses.A_BOLD | curses.color_pair(4)))
                
                # Separator after header (centered)
                cxs_separator = f"+{'-' * id_width}+{'-' * slot_width}+{'-' * pos_width}+"
                centered_cxs_separator = cxs_separator.center(width)
                content_lines.append(("text", centered_cxs_separator, curses.color_pair(4)))
                
                # Data rows
                for row in data_rows:
                    cxs_id = str(row[0])
                    slot_info = str(row[1])
                    position = str(row[2])
                    
                    # Handle long slot info by wrapping
                    if len(slot_info) > slot_width:
                        # Split long slot info into multiple lines
                        slot_lines = []
                        for i in range(0, len(slot_info), slot_width):
                            slot_lines.append(slot_info[i:i+slot_width])
                        
                        # First line with all columns (centered)
                        first_line = f"|{cxs_id:^{id_width}}|{slot_lines[0]:<{slot_width}}|{position:^{pos_width}}|"
                        centered_first_line = first_line.center(width)
                        content_lines.append(("text", centered_first_line, curses.color_pair(5)))
                        
                        # Additional lines for slot info only (centered)
                        for slot_line in slot_lines[1:]:
                            additional_line = f"|{' ' * id_width}|{slot_line:<{slot_width}}|{' ' * pos_width}|"
                            centered_additional_line = additional_line.center(width)
                            content_lines.append(("text", centered_additional_line, curses.color_pair(5)))
                    else:
                        # Single line (centered)
                        data_row = f"|{cxs_id:^{id_width}}|{slot_info:^{slot_width}}|{position:^{pos_width}}|"
                        centered_data_row = data_row.center(width)
                        content_lines.append(("text", centered_data_row, curses.color_pair(5)))
                    
                    # Row separator (except for last row) (centered)
                    if row != data_rows[-1]:
                        content_lines.append(("text", centered_cxs_separator, curses.color_pair(4)))
                
                # Bottom border for CxS table (centered)
                cxs_bottom_border = f"+{'-' * id_width}+{'-' * slot_width}+{'-' * pos_width}+"
                centered_cxs_bottom_border = cxs_bottom_border.center(width)
                content_lines.append(("text", centered_cxs_bottom_border, curses.color_pair(4)))
                
            else:
                no_cxs_title = "CxS Parsing Results:"
                centered_no_cxs_title = no_cxs_title.center(width)
                content_lines.append(("section", centered_no_cxs_title, curses.A_BOLD | curses.color_pair(3)))
                # No results table (centered)
                no_results_border = "+" + "-" * 30 + "+"
                centered_no_results_border = no_results_border.center(width)
                content_lines.append(("text", centered_no_results_border, curses.color_pair(4)))
                
                no_results_content = f"|{'No CxS structures found':^30}|"
                centered_no_results_content = no_results_content.center(width)
                content_lines.append(("text", centered_no_results_content, curses.color_pair(4)))
                content_lines.append(("text", centered_no_results_border, curses.color_pair(4)))
            
            content_lines.append(("empty", "", 0))
            content_lines.append(("empty", "", 0))
            
            # Calculate max scroll (accounting for fixed header and footer)
            available_content_height = height - header_height - 1  # -1 for footer
            max_scroll = max(0, len(content_lines) - available_content_height)
            
            # Display fixed header first
            displayed_lines = 0
            for line_type, content, attr in header_lines:
                try:
                    if line_type == "header":
                        # Center the header
                        x_pos = (width - len(content)) // 2
                        stdscr.addstr(displayed_lines, x_pos, content, attr)
                    else:
                        # Truncate if too long
                        display_content = content[:width-1] if len(content) >= width else content
                        stdscr.addstr(displayed_lines, 0, display_content, attr)
                except curses.error:
                    pass  # Ignore if we can't write to that position
                displayed_lines += 1
            
            # Display scrollable content
            for i, (line_type, content, attr) in enumerate(content_lines[scroll_pos:]):
                if displayed_lines >= height - 1:  # Leave space for footer
                    break
                    
                try:
                    # Truncate if too long
                    display_content = content[:width-1] if len(content) >= width else content
                    stdscr.addstr(displayed_lines, 0, display_content, attr)
                except curses.error:
                    pass  # Ignore if we can't write to that position
                    
                displayed_lines += 1
            
            # Footer with instructions
            footer_y = height - 1
            footer_text = "Press 'q' to quit, '↑'/'↓' or 'j'/'k' or mouse wheel to scroll"
            if max_scroll > 0:
                scroll_info = f" | Scroll: {scroll_pos}/{max_scroll}"
                footer_text += scroll_info
            
            try:
                stdscr.addstr(footer_y, 0, footer_text[:width-1], curses.A_BOLD | curses.color_pair(3))
            except curses.error:
                pass
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_MOUSE:
                # Handle mouse events
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    # Mouse wheel up (scroll up)
                    if bstate & curses.BUTTON4_PRESSED:
                        scroll_pos = max(0, scroll_pos - 3)  # Scroll up 3 lines
                    # Mouse wheel down (scroll down)
                    elif bstate & curses.BUTTON5_PRESSED:
                        scroll_pos = min(max_scroll, scroll_pos + 3)  # Scroll down 3 lines
                except curses.error:
                    pass  # Ignore mouse errors
            elif key == curses.KEY_UP or key == ord('k'):
                scroll_pos = max(0, scroll_pos - 1)
            elif key == curses.KEY_DOWN or key == ord('j'):
                scroll_pos = min(max_scroll, scroll_pos + 1)
            elif key == curses.KEY_PPAGE:  # Page Up
                scroll_pos = max(0, scroll_pos - (height - 3))
            elif key == curses.KEY_NPAGE:  # Page Down
                scroll_pos = min(max_scroll, scroll_pos + (height - 3))
            elif key == curses.KEY_HOME:
                scroll_pos = 0
            elif key == curses.KEY_END:
                scroll_pos = max_scroll
    
    # Run the curses interface
    try:
        curses.wrapper(draw_interface)
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully


def print_text_with_border(text, title=""):
    display_text = f"  {text}  "
    border = "+" + "-" * len(display_text) + "+"
    
    if title:
        print(f"{title}:")
    print(border)
    print(f"|{display_text}|")
    print(border)
    print()


def print_table(data, title="", header_separator="="):
    if not data:
        return
    
    widths = [max(len(str(row[i])) for row in data) + 2 for i in range(len(data[0]))]
    
    if title:
        print(f"{title}:")
    
    for i, row in enumerate(data):
        if i == 0:
            print("+" + "+".join("-" * w for w in widths) + "+")
        
        print("|" + "|".join(f"{cell:^{widths[j]}}" for j, cell in enumerate(row)) + "|")
        
        if i == 0 and header_separator == "=":
            print("+" + "+".join("=" * w for w in widths) + "+")
        else:
            print("+" + "+".join("-" * w for w in widths) + "+")


def format_encoding_data(tokens, upos, xpos):
    return [["ID"] + [str(i+1) for i in range(len(tokens))],
            ["Token"] + tokens,
            ["UPOS"] + upos,
            ["XPOS"] + xpos]


def format_cxs_data(cxs_s, parser, logger):
    if not cxs_s or not cxs_s[0]:
        return []
    
    cxs_data = [[cxs[0], convert_slots_to_str(parser.cxs_decoder[cxs[0]], parser.encoder, logger), 
                 f"{cxs[1] + 1}-{cxs[2]}"] for cxs in cxs_s[0]]
    
    return [["CxS ID", "Slot Info", "Position Range"]] + cxs_data

raw_sentences = [
    'She should be more polite with the customers.',
    "She said, \"I am tired.\" She said that she was tired.",
    "She said, \"I am tired. \" She said that she was tired.",
    "The advantage of a bad memory is that one enjoys several times the same good things for the first time.",
]


def parse_arguments():
    # Save original argv
    original_argv = sys.argv.copy()
    
    # Parse custom arguments
    argparser = argparse.ArgumentParser(description='CxG Parser - Parse construction grammar structures')
    argparser.add_argument('text', nargs='?', help='Input text to parse')
    argparser.add_argument('-i', '--interactive', action='store_true', help='Interactive input mode')
    args = argparser.parse_args()
    
    # Temporarily set sys.argv to avoid Config argparse conflicts
    sys.argv = [sys.argv[0]]
    
    return args, original_argv


def get_input_text(args):
    if args.text:
        return args.text
    elif args.interactive:
        user_input = input("Enter text to parse (or 'q' to quit): ")
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("\nExiting CxG Parser. Goodbye!")
            sys.exit(0)
        return user_input
    else:
        print("Usage:")
        print("  python cxgparser.py \"your text here\"")
        print("  python cxgparser.py -i")
        print("\nExample sentences:")
        for i, sentence in enumerate(raw_sentences):
            print(f"  {i}: {sentence}")
        
        try:
            choice = input("\nSelect example (0-{}) or 'q' to quit: ".format(len(raw_sentences)-1))
            
            # Check if user wants to quit
            if choice.lower() in ['q', 'quit', 'exit']:
                print("\nExiting CxG Parser. Goodbye!")
                sys.exit(0)
            
            # Try to convert to integer
            choice = int(choice)
            if 0 <= choice < len(raw_sentences):
                return raw_sentences[choice]
            else:
                print(f"\nInvalid Choice {choice}, Goodbye!")
                sys.exit(-1)
        except (ValueError, KeyboardInterrupt):
            print("\nExiting CxG Parser. Goodbye!")
            sys.exit(0)


def run_parser(input_text, parser, logger):
    # Encoding and parsing
    encoded_elements = parser.encoder.encode(input_text, raw=True)
    tokens, upos, xpos = encoded_elements["lexical"], encoded_elements["upos"]["spaCy"], encoded_elements["xpos"]["spaCy"]
    
    # CxS parsing
    cxs_s = parser.parse(input_text)
    cxs_table_data = format_cxs_data(cxs_s, parser, logger)
    
    # Display results in full-screen interface
    display_results_fullscreen(input_text, tokens, upos, xpos, cxs_table_data, parser, logger)


def main():
    args, original_argv = parse_arguments()
    
    # Initialize config and parser
    config = Config(DefaultConfigs.eng)
    logger = init_logger(config)

    # Use relative path from the project root or let Parser handle the default path
    file_path = os.path.dirname(os.path.abspath(__file__))
    parser = Parser(name_or_path=os.path.join(file_path, "../resources/data/eng/1.1"), config=config, logger=logger)
    
    # Restore original argv
    sys.argv = original_argv
    
    # Get input text and run parser
    input_text = get_input_text(args)
    run_parser(input_text, parser, logger)


if __name__ == '__main__':
    main()
