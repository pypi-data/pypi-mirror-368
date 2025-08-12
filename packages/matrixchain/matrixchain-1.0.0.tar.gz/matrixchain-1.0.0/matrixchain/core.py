"""
Matrix Chain Multiplication Optimizer

A hacker-style interactive visualizer for the Matrix Chain Multiplication problem
using Dynamic Programming. This module implements the classic algorithm with
colorful terminal output and step-by-step visualization.

Author: Chauhan Pruthviraj
"""

import os
import time
import random
import sys
from colorama import Fore, Style, init

init(autoreset=True)

# ------------------ Banner ------------------
def banner():
    """Display the ASCII art banner for the application."""
    print(Fore.CYAN + r"""
 __  __       _        _   _       _ _   _             
|  \/  | __ _| |_ _ __| | | |_ __ (_) |_(_) ___  _ __  
| |\/| |/ _` | __| '__| | | | '_ \| | __| |/ _ \| '_ \ 
| |  | | (_| | |_| |  | |_| | | | | | |_| | (_) | | | |
|_|  |_|\__,_|\__|_|   \___/|_| |_|_|\__|_|\___/|_| |_|

        Matrix Chain Multiplication Optimizer
    """ + Style.RESET_ALL)
    print("=" * 60)

# ------------------ Fake scanning ------------------
def fake_scan():
    """Display fake scanning messages for enhanced user experience."""
    messages = [
        "[INFO] Initializing...",
        "[INFO] Checking multiplication paths...",
        "[SCAN] Enumerating chain lengths...",
        "[SCAN] Evaluating possible splits...",
        "[HIT] Possible optimization detected...",
        "[INFO] Calculating minimal cost path...",
    ]
    for msg in messages:
        print(Fore.YELLOW + msg + Style.RESET_ALL)
        time.sleep(random.uniform(0.2, 0.5))
    print()

# ------------------ Parenthesis reconstruction ------------------
def print_parenthesis(s, i, j):
    """
    Reconstruct the optimal parenthesization from the split table.

    Args:
        s: Split table from matrix_chain_order
        i: Start index
        j: End index

    Returns:
        String representation of optimal parenthesization
    """
    if i == j:
        return f"A{i+1}"
    else:
        return "(" + print_parenthesis(s, i, s[i][j]) + " x " + print_parenthesis(s, s[i][j]+1, j) + ")"

# ------------------ DP computation with live logs ------------------
def matrix_chain_order(P):
    """
    Solve the Matrix Chain Multiplication problem using Dynamic Programming.

    Args:
        P: List of matrix dimensions where matrix i has dimensions P[i-1] x P[i]

    Returns:
        Tuple (m, s) where:
        - m: Cost table where m[i][j] is minimum cost to multiply matrices i to j
        - s: Split table where s[i][j] is optimal split point for matrices i to j
    """
    n = len(P) - 1
    m = [[0 if i==j else float('inf') for j in range(n)] for i in range(n)]
    s = [[None for _ in range(n)] for _ in range(n)]

    for chain_len in range(2, n+1):
        for i in range(n-chain_len+1):
            j = i + chain_len - 1
            m[i][j] = float('inf')
            for k in range(i, j):
                cost = m[i][k] + m[k+1][j] + P[i] * P[k+1] * P[j+1]
                # compact scanning line
                sys.stdout.write(Fore.MAGENTA + f"[SCAN] DP[{i+1},{j+1}] via k={k+1} -> cost={cost}" + " " * 10 + "\r")
                sys.stdout.flush()
                time.sleep(random.uniform(0.03, 0.08))
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
                    print(Fore.GREEN + f"[HIT] DP[{i+1},{j+1}] = {cost} (k={k+1})" + Style.RESET_ALL)
                else:
                    # small NO message printed inline to keep scroll interesting
                    print(Fore.RED + f"[NO]  DP[{i+1},{j+1}] via k={k+1} -> {cost}" + Style.RESET_ALL)
    return m, s

# ------------------ Fancy Table Printing ------------------
# Replace your previous print_table_boxed with this one.
def _colorize_center(plain_text, width, color=None):
    text = str(plain_text)
    padded = text.center(width)                 # center plain text (no color codes)
    if color:
        return f"{color}{padded}{Style.RESET_ALL}"
    return padded

def print_table_boxed(table, title, cell_width=14, inf_symbol="--", is_split=False):
    """
    Nicely aligned boxed table.
    - is_split=True: display split table values as (k+1), show '--' for None.
    - For cost table (is_split=False) diagonal shows '0', inf shows '--'.
    """
    n = len(table)
    print(Fore.CYAN + f"\n[LOOT] {title}" + Style.RESET_ALL)

    # horizontal border and header
    horizontal_line = "+" + "+".join(["-" * cell_width for _ in range(n + 1)]) + "+"
    header_cells = [" "] + [f"A{j+1}" for j in range(n)]
    print(horizontal_line)
    print("|" + "|".join(_colorize_center(h, cell_width) for h in header_cells) + "|")
    print(horizontal_line)

    # rows
    for i in range(n):
        row_label = _colorize_center(f"A{i+1}", cell_width, Fore.CYAN)
        row_cells = []
        for j in range(n):
            val = table[i][j]
            if is_split:
                # split table display: show k+1 (human readable), '--' for None or diag
                if val is None:
                    plain = inf_symbol
                    col = Fore.RED
                else:
                    plain = str(val + 1)
                    col = Fore.YELLOW
            else:
                # cost table display
                if isinstance(val, float) and val == float('inf'):
                    plain = inf_symbol
                    col = Fore.RED
                elif i == j:
                    plain = "0"
                    col = Fore.GREEN
                else:
                    plain = str(val)
                    col = Fore.YELLOW
            row_cells.append(_colorize_center(plain, cell_width, col))
        print("|" + row_label + "|" + "|".join(row_cells) + "|")
    print(horizontal_line)

# ------------------ Input helper ------------------
def read_dimensions():
    print(Fore.CYAN + "Enter matrix dimensions P as space-separated integers.")
    print("Example for matrices A1 (5x4), A2 (4x6), A3 (6x2), A4 (2x7):")
    print("    5 4 6 2 7  (this is P0 P1 P2 P3 P4)\n" + Style.RESET_ALL)
    line = input(Fore.YELLOW + "[#] Paste dims (or press Enter to input step-by-step): " + Style.RESET_ALL).strip()
    if line:
        parts = line.split()
        try:
            P = [int(x) for x in parts]
            if len(P) < 2:
                raise ValueError
            return P
        except ValueError:
            print(Fore.RED + "Invalid dimensions. Falling back to interactive mode." + Style.RESET_ALL)

    # interactive fallback
    while True:
        try:
            num_m = int(input(Fore.YELLOW + "[#] Number of matrices (n): " + Style.RESET_ALL))
            if num_m < 1:
                raise ValueError
            break
        except ValueError:
            print(Fore.RED + "Please enter a positive integer." + Style.RESET_ALL)

    P = []
    for i in range(num_m):
        while True:
            try:
                a = int(input(Fore.CYAN + f"  Enter rows of A{i+1} (or P{i}): " + Style.RESET_ALL))
                b = int(input(Fore.CYAN + f"  Enter cols of A{i+1} (or P{i+1}): " + Style.RESET_ALL))
                # For chain dims we only need to append first matrix rows then each following cols,
                # but to keep it simple, we'll construct P by reading A1 rows and all Ai cols:
                if i == 0:
                    P.append(a)  # P0
                P.append(b)      # P1, P2, ...
                break
            except ValueError:
                print(Fore.RED + "Please enter integer dimensions." + Style.RESET_ALL)
    return P

# ------------------ Main ------------------
def main():
    # clear a bit and banner
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    # read P array
    P = read_dimensions()
    # confirm
    print(Fore.GREEN + f"\nDimensions P = {P}  (matrices = {len(P)-1})\n" + Style.RESET_ALL)

    fake_scan()
    print(Fore.YELLOW + "[+] Starting DP computation...\n" + Style.RESET_ALL)
    time.sleep(0.3)
    m, s = matrix_chain_order(P)

    # results
    print_table_boxed(m, "Minimal Multiplication Cost Table (mTable)")
    print_table_boxed(s, "Split Table (sTable) — k indices", is_split=True)
    order = print_parenthesis(s, 0, len(P)-2)
    print(Fore.CYAN + "\n[LOOT] Optimal Parenthesization" + Style.RESET_ALL)
    print(Fore.GREEN + order + Style.RESET_ALL)
    print(Fore.YELLOW + f"\n[+] Minimum multiplication cost: {m[0][len(P)-2]}" + Style.RESET_ALL)
    print(Fore.MAGENTA + "\n[+] Mission Complete\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
