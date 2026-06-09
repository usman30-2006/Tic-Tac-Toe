AI_Sign = 'X'
P1_Sign = 'O'
P2_Sign = 'X'  

CORNERS = [(0, 0), (0, 2), (2, 0), (2, 2)]
SIDES = [(0, 1), (1, 0), (1, 2), (2, 1)]
OPPOSITE_CORNERS = {
    (0, 0): (2, 2),
    (0, 2): (2, 0),
    (2, 0): (0, 2),
    (2, 2): (0, 0),
}

# Board Display

def make_board():
    """Create and return a fresh 3x3 board populated with integers 1-9."""
    return [[3 * row + col + 1 for col in range(3)] for row in range(3)]

def display_board(board):
    """Print the board to the console with ASCII grid lines."""
    print("+-------" * 3 + "+")
    for row in range(3):
        print("|       " * 3 + "|")
        for col in range(3):
            print("|   " + str(board[row][col]) + "   ", end="")
        print("|")
        print("|       " * 3 + "|")
        print("+-------" * 3 + "+")

# winning condititons

def is_winner(board, sign):
    # rows
    if board[0][0] == board[0][1] == board[0][2] == sign:
        return True
    if board[1][0] == board[1][1] == board[1][2] == sign:
        return True
    if board[2][0] == board[2][1] == board[2][2] == sign:
        return True

    # columns
    if board[0][0] == board[1][0] == board[2][0] == sign:
        return True
    if board[0][1] == board[1][1] == board[2][1] == sign:
        return True
    if board[0][2] == board[1][2] == board[2][2] == sign:
        return True

    # diagonals
    if board[0][0] == board[1][1] == board[2][2] == sign:
        return True
    if board[0][2] == board[1][1] == board[2][0] == sign:
        return True

    return False

def get_free_cells(board):
    """Return a list of (row, col) coordinates for cells that are still numbers."""
    return [(r, c) for r in range(3) for c in range(3) if isinstance(board[r][c], int)]

def is_board_full(board):
    """Check if there are no numeric cells remaining."""
    return len(get_free_cells(board)) == 0

def place_sign(board, row, col, sign):
    """Return a new board state with the sign placed at (row, col)."""
    new_board = [r[:] for r in board]
    new_board[row][col] = sign
    return new_board

# AI Agent Heuristics

def find_immediate_win(board, sign):
    #Find a move that results in an instant win for the specified sign.
    for r, c in get_free_cells(board):
        candidate = place_sign(board, r, c, sign)
        if is_winner(candidate, sign):
            return r, c
    return None

def search_for_fork(board, sign):
    #Find a move that creates two separate winning paths for the sign.
    for row, column in get_free_cells(board):
        candidate = place_sign(board, row, column, sign)
        win_paths = 0
        for row2, column2 in get_free_cells(candidate):
            if is_winner(place_sign(candidate, row2, column2, sign), sign):
                win_paths += 1
                if win_paths >= 2:
                    return row, column
    return None

def prevent_opponent_fork(board, opponent):
    #Find the opponent's forking position to block it.
    return search_for_fork(board, opponent)

def determine_optimal_move(board):
    #Calculate the best possible move based on a strict priority hierarchy.
    # 1. Win
    move = find_immediate_win(board, AI_Sign)
    if move: return move
    # 2. Block
    move = find_immediate_win(board, P1_Sign)
    if move: return move
    # 3. Fork
    move = search_for_fork(board, AI_Sign)
    if move: return move
    # 4. Block Fork
    move = prevent_opponent_fork(board, P1_Sign)
    if move: return move
    # 5. Center
    if isinstance(board[1][1], int):
        return 1, 1
    # 6. Opposite Corner
    for r, c in CORNERS:
        if board[r][c] == P1_Sign:
            opp_r, opp_c = OPPOSITE_CORNERS[(r, c)]
            if isinstance(board[opp_r][opp_c], int):
                return opp_r, opp_c
    # 7. Empty Corner
    for r, c in CORNERS:
        if isinstance(board[r][c], int):
            return r, c
    # 8. Empty Side
    for r, c in SIDES:
        if isinstance(board[r][c], int):
            return r, c
    return None


#utility function

def request_player_move(board, player_name, sign):
    #Prompt the current human player to choose an empty cell or quit.
    free_cells = {board[r][c]: (r, c) for r, c in get_free_cells(board)}
    while True:
        try:
            choice = input(f"{player_name} ({sign}), choose a cell {list(free_cells.keys())} (or 'q' to exit match): ").strip().lower()
            if choice == 'q':
                return 'quit'
            
            choice_int = int(choice)
            if choice_int in free_cells:
                return free_cells[choice_int]
            print("Invalid square. Try again.")
        except ValueError:
            print("Please enter a valid number or 'q'.")


def play_human_vs_ai(stats):
    #Run a single match of Human vs AI where AI goes first.
    board = make_board()
    print("\n--- Human vs AI Mode ---")
    print(f"Current Stats -> Human: {stats['human']} | AI: {stats['computer']} | Draws: {stats['draws']}")
    print("AI is 'X', You are 'O'. AI plays first.")
    
    while True:
        # AI Turn
        print("\nAI is thinking...")
        move = determine_optimal_move(board)
        if move:
            board = place_sign(board, move[0], move[1], AI_Sign)
        
        display_board(board)
        
        if is_winner(board, AI_Sign):
            print("AI wins!")
            stats["computer"] += 1
            return
        if is_board_full(board):
            print("It's a draw!")
            stats["draws"] += 1
            return
            
        # Human Turn
        move = request_player_move(board, "Human", P1_Sign)
        if move == 'quit':
            print("Match cancelled.")
            return
            
        board = place_sign(board, move[0], move[1], P1_Sign)
        
        if is_winner(board, P1_Sign):
            display_board(board)
            print("You win!")
            stats["human"] += 1
            return
        if is_board_full(board):
            display_board(board)
            print("It's a draw!")
            stats["draws"] += 1
            return

def play_human_vs_human(stats):
    """Run a single match of Human vs Human where Player 1 goes first."""
    board = make_board()
    print("\n--- Human vs Human Mode ---")
    print(f"Current Stats -> Player 1: {stats['p1']} | Player 2: {stats['p2']} | Draws: {stats['draws']}")
    
    current_player = "Player 1"
    current_sign = P1_Sign
    
    while True:
        display_board(board)
        move = request_player_move(board, current_player, current_sign)
        if move == 'quit':
            print("Match cancelled.")
            return
            
        board = place_sign(board, move[0], move[1], current_sign)
        
        if is_winner(board, current_sign):
            display_board(board)
            print(f"{current_player} ({current_sign}) wins!")
            if current_player == "Player 1":
                stats["p1"] += 1
            else:
                stats["p2"] += 1
            return
            
        if is_board_full(board):
            display_board(board)
            print("It's a draw!")
            stats["draws"] += 1
            return
            
        # Swap players
        if current_player == "Player 1":
            current_player = "Player 2"
            current_sign = P2_Sign
        else:
            current_player = "Player 1"
            current_sign = P1_Sign
# main loop

def run_game_system():
    """Manage game system setup, tracking scorecards for both modes."""
    ai_mode_stats = {"human": 0, "computer": 0, "draws": 0}
    pvp_mode_stats = {"p1": 0, "p2": 0, "draws": 0}
    
    while True:
        print("\n" + "=" * 30)
        print("     TIC-TAC-TOE MENU     ")
        print("=" * 30)
        print("1. Play Human vs AI")
        print("2. Play Human vs Human")
        print("3. View Session Scoreboards")
        print("4. Quit Program")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            while True:
                play_human_vs_ai(ai_mode_stats)
                again = input("\nPlay Human vs AI again? (y/n): ").strip().lower()
                if again != 'y':
                    break
        elif choice == '2':
            while True:
                play_human_vs_human(pvp_mode_stats)
                again = input("\nPlay Human vs Human again? (y/n): ").strip().lower()
                if again != 'y':
                    break
        elif choice == '3':
            print("  CURRENT SESSION LIFETIME STATS")
            print("\n")
            print("-" * 30)
            print("[Mode 1: Human vs AI]")
            print(f"  Human Wins : {ai_mode_stats['human']}")
            print(f"  AI Wins    : {ai_mode_stats['computer']}")
            print(f"  Draws      : {ai_mode_stats['draws']}")
            print("-" * 30)
            print("[Mode 2: Human vs Human]")
            print(f"  Player 1 Wins: {pvp_mode_stats['p1']}")
            print(f"  Player 2 Wins: {pvp_mode_stats['p2']}")
            print(f"  Draws        : {pvp_mode_stats['draws']}")
            print("\n")
            input("\nPress Enter to return to menu...")
        elif choice == '4':
            print("\nFinalizing score logs...")
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select from 1, 2, 3, or 4.")

if __name__ == "__main__":
    run_game_system()