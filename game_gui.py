import pygame
import chess
import chess.engine
import sys

# --- CẤU HÌNH ---
WIDTH = 512
HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 60  # Tăng FPS lên cho mượt
IMAGES = {}


# --- HÀM TẢI HÌNH ẢNH ---
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        try:
            IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        except pygame.error:
            # Nếu thiếu ảnh, tạo hình vuông màu tạm
            pass

        # --- VẼ BÀN CỜ ---


def draw_board(screen, player_color):
    """Vẽ ô vuông. Nếu chơi Đen, bàn cờ sẽ lật ngược."""
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board, player_color):
    """Vẽ quân cờ. Xử lý lật bàn cờ nếu chơi quân Đen."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Tính toán ô vuông dựa trên góc nhìn người chơi
            if player_color == chess.WHITE:
                # Góc nhìn Trắng: Hàng 0 ở trên cùng (Rank 8), Hàng 7 ở dưới (Rank 1)
                square_index = chess.square(c, 7 - r)
            else:
                # Góc nhìn Đen: Hàng 0 ở trên cùng (Rank 1), Hàng 7 ở dưới (Rank 8)
                square_index = chess.square(7 - c, r)

            piece = board.piece_at(square_index)
            if piece is not None:
                color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                piece_symbol = piece.symbol().upper()
                if piece_symbol == 'N': piece_symbol = 'N'
                filename = color_prefix + piece_symbol

                if filename in IMAGES:
                    screen.blit(IMAGES[filename], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# --- GIAO DIỆN CHỌN PHONG CẤP ---
def draw_promotion_menu(screen, move_to_col, move_to_row, piece_color):
    """Vẽ menu chọn 4 quân khi phong cấp"""
    # Vẽ nền mờ che bàn cờ
    s = pygame.Surface((WIDTH, HEIGHT))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 0))

    # Vẽ khung chọn
    font = pygame.font.SysFont('Arial', 32, bold=True)
    text = font.render("CHỌN QUÂN PHONG CẤP:", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    # Các lựa chọn: Hậu, Xe, Tượng, Mã
    color_prefix = 'w' if piece_color == chess.WHITE else 'b'
    options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    option_names = ['Q', 'R', 'B', 'N']

    # Tọa độ vẽ menu (Giữa màn hình)
    start_x = WIDTH // 2 - (2 * SQ_SIZE)
    start_y = HEIGHT // 2

    rects = []
    for i, opt in enumerate(options):
        # Vẽ ô nền
        rect = pygame.Rect(start_x + i * SQ_SIZE, start_y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, (200, 200, 200), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Viền đen

        # Vẽ quân cờ
        img_name = color_prefix + option_names[i]
        if img_name in IMAGES:
            screen.blit(IMAGES[img_name], rect)

        rects.append((rect, opt))  # Lưu lại để kiểm tra click

    pygame.display.flip()
    return rects


# --- CHƯƠNG TRÌNH CHÍNH ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cờ Vua - Python Project")
    clock = pygame.time.Clock()
    load_images()

    # --- KẾT NỐI STOCKFISH ---
    try:
        engine = chess.engine.SimpleEngine.popen_uci(r"stockfish.exe")
    except FileNotFoundError:
        print("Lỗi: Thiếu file stockfish.exe!")
        return

    # --- MÀN HÌNH CHỌN MÀU (MENU) ---
    choosing_color = True
    player_color = chess.WHITE  # Mặc định

    font = pygame.font.SysFont('Arial', 24)
    while choosing_color:
        screen.fill((50, 50, 50))
        txt1 = font.render("CHÀO MỪNG ĐẾN VỚI CỜ VUA!", True, (255, 255, 255))
        txt2 = font.render("Nhấn phím [W] để cầm quân TRẮNG (Đi trước)", True, (200, 200, 200))
        txt3 = font.render("Nhấn phím [B] để cầm quân ĐEN (Đi sau)", True, (200, 200, 200))

        screen.blit(txt1, (WIDTH // 2 - txt1.get_width() // 2, 150))
        screen.blit(txt2, (WIDTH // 2 - txt2.get_width() // 2, 250))
        screen.blit(txt3, (WIDTH // 2 - txt3.get_width() // 2, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player_color = chess.WHITE
                    choosing_color = False
                elif event.key == pygame.K_b:
                    player_color = chess.BLACK
                    choosing_color = False

    # --- VÀO GAME ---
    board = chess.Board()
    running = True
    game_over = False
    sq_selected = ()
    player_clicks = []

    # Biến để xử lý phong cấp
    promotion_pending = False
    pending_move_data = None  # Lưu tạm nước đi (from, to) chờ chọn quân

    while running:
        # Nếu đến lượt máy và game chưa kết thúc, chưa chờ phong cấp
        if not game_over and not promotion_pending and board.turn != player_color:
            # Vẽ lại để người chơi thấy nước mình vừa đi
            draw_board(screen, player_color)
            draw_pieces(screen, board, player_color)
            pygame.display.flip()

            # Máy suy nghĩ
            # Nếu máy cầm quân Đen (player cầm Trắng) -> Máy đi Đen và ngược lại
            print("Cá kho đang suy nghĩ nát óc...")
            result = engine.play(board, chess.engine.Limit(time=1.0))
            board.push(result.move)
            print(f"Cá kho quyết định đi: {result.move}")

        # Xử lý sự kiện (người chơi)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- XỬ LÝ CLICK KHI ĐANG CHỜ CHỌN QUÂN PHONG CẤP ---
            elif event.type == pygame.MOUSEBUTTONDOWN and promotion_pending:
                mouse_pos = pygame.mouse.get_pos()
                # Kiểm tra click vào ô nào trong menu phong cấp
                for rect, piece_type in promotion_rects:
                    if rect.collidepoint(mouse_pos):
                        # Thực hiện nước đi với quân đã chọn
                        move_from, move_to = pending_move_data
                        move = chess.Move(move_from, move_to, promotion=piece_type)
                        board.push(move)
                        print(f"Bạn vừa đi nước: {move}")

                        # Tắt menu, reset trạng thái
                        promotion_pending = False
                        pending_move_data = None
                        sq_selected = ()
                        player_clicks = []
                        break

            # --- XỬ LÝ CLICK ĐI QUÂN BÌNH THƯỜNG ---
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not promotion_pending and board.turn == player_color:
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                # Chuyển đổi tọa độ click theo góc nhìn người chơi
                if player_color == chess.WHITE:
                    click_sq = chess.square(col, 7 - row)
                else:
                    click_sq = chess.square(7 - col, row)

                if sq_selected == click_sq:  # Bỏ chọn
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = click_sq
                    player_clicks.append(sq_selected)

                if len(player_clicks) == 2:
                    move_from = player_clicks[0]
                    move_to = player_clicks[1]

                    # Tạo nước đi thử (chưa phong cấp)
                    move = chess.Move(move_from, move_to)

                    # Kiểm tra xem có phải nước phong cấp không?
                    # Điều kiện: Quân là Tốt + Đi đến hàng cuối cùng
                    is_pawn = board.piece_at(move_from) and board.piece_at(move_from).piece_type == chess.PAWN

                    is_promotion = False
                    if is_pawn:
                        rank_to = chess.square_rank(move_to)
                        if (board.turn == chess.WHITE and rank_to == 7) or \
                                (board.turn == chess.BLACK and rank_to == 0):
                            is_promotion = True

                    # NẾU LÀ PHONG CẤP -> DỪNG LẠI, HIỆN MENU
                    if is_promotion:
                        # Kiểm tra xem nước đi đến đó có hợp lệ không (ví dụ kiểm tra xem có bị ghim không)
                        # Ta thử tạo nước đi phong Hậu giả định để check luật
                        test_move = chess.Move(move_from, move_to, promotion=chess.QUEEN)
                        if test_move in board.legal_moves:
                            promotion_pending = True
                            pending_move_data = (move_from, move_to)
                            # Vẽ menu ngay lập tức
                            draw_board(screen, player_color)
                            draw_pieces(screen, board, player_color)
                            promotion_rects = draw_promotion_menu(screen, 0, 0, player_color)
                            continue  # Bỏ qua phần xử lý bên dưới, chờ vòng lặp sau

                    # NẾU KHÔNG PHẢI PHONG CẤP -> ĐI BÌNH THƯỜNG
                    if move in board.legal_moves:
                        board.push(move)
                        print(f"Bạn vừa đi nước: {move}")
                    else:
                        pass  # Nước đi lỗi

                    sq_selected = ()
                    player_clicks = []

        # --- CẬP NHẬT MÀN HÌNH ---
        if not promotion_pending:  # Nếu đang chọn phong cấp thì không vẽ lại bàn cờ đè lên menu
            draw_board(screen, player_color)
            draw_pieces(screen, board, player_color)

            if board.is_game_over() and not game_over:
                game_over = True
                outcome = board.outcome()
                result_text = "GAME OVER"
                if outcome.winner == chess.WHITE:
                    result_text = "WHITE WINS!"
                elif outcome.winner == chess.BLACK:
                    result_text = "BLACK WINS!"
                else:
                    result_text = "DRAW!"
                pygame.display.set_caption(result_text)
                print(result_text)

            pygame.display.flip()

        clock.tick(MAX_FPS)

    engine.quit()
    pygame.quit()


if __name__ == "__main__":
    main()