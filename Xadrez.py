from stockfish import Stockfish
import chess
import re
import random
import time
from pyModbusTCP.server import ModbusServer, DataBank
import cv2 as cv
from FINAL_VISAO import jogada_realizada_adversario

stockfish_path = "C:\\Users\\ferna\\OneDrive\\Documentos\\Insper\\7Periodo\\RoboticaIndustrial\\Projeto Xadrez\\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(stockfish_path)

stockfish.set_depth(10)#How deep the AI looks
stockfish.set_skill_level(5)#Highest rank stockfish

board = chess.Board()

SERVER_ADDRESS = '10.103.16.103'
SERVER_PORT = 502
server = ModbusServer(SERVER_ADDRESS, SERVER_PORT, no_block=True)

jogada_anterior = ['a3', 'a4', 'a5', 'a6', 'b3', 'b4', 'b5', 'b6', 'c3', 'c4', 'c5', 'c6', 'd3', 'd4', 'd5', 'd6', 'e3', 'e4', 'e5', 'e6', 'f3', 'f4', 'f5', 'f6', 'g3', 'g4', 'g5', 'g6', 'h3', 'h4', 'h5', 'h6']

cor_anterior={'a1': 'white', 'a2': 'white', 'a7': 'black', 'a8': 'black', 'b1': 'white', 'b2': 'white', 'b7': 'black', 'b8': 'black', 'c1': 'white', 'c2':'white', 'c7': 'black', 'c8': 'black', 'd1': 'white', 'd2': 'white', 'd7': 'black', 'd8': 'black', 'e1': 'white', 'e2': 'white', 'e7': 'black', 'e8': 'black','f1': 'white', 'f2': 'white', 'f7': 'black', 'f8': 'black',  'g1': 'white', 'g2': 'white', 'g7': 'black', 'g8': 'black', 'h1': 'white', 'h2': 'white', 'h7': 'black', 'h8': 'black'}


def conversao_stockfish(mov_robot):
    mov_robot_convert = [int(char) if char.isdigit() else ord(char) - ord('a') for char in re.findall(r'[A-Ha-h]|[0-8]', mov_robot)]
    return mov_robot_convert


def manda_robo(manda_modbus, tabuleiro_inicio, tabuleiro_final):
    
    data_sent = [float((i * 45) + 20) for i in manda_modbus]  # mm
    server.data_bank.set_input_registers(180, data_sent)
    time.sleep(0.2)

    Tipo_mov = 0

    # Contagem de peças
    num_pieces_inicio = sum(1 for square in chess.SQUARES if tabuleiro_inicio.piece_at(square) is not None)
    num_pieces_final = sum(1 for square in chess.SQUARES if tabuleiro_final.piece_at(square) is not None)

    print(f"Número de peças no início: {num_pieces_inicio}")
    print(f"Número de peças no final: {num_pieces_final}")

    if num_pieces_inicio > num_pieces_final:
        Tipo_mov = 2  # Captura

        i_y=random.randint(50,400)
        i_x=random.randint(50,100)
        server.data_bank.set_input_registers(187,[i_y])
        server.data_bank.set_input_registers(188,[i_x])
        time.sleep(0.5)
        print('captura_x',i_x)
        print('captura_y',i_y)
    else:
        Tipo_mov = 1

    print(Tipo_mov)
    time.sleep(1)
    server.data_bank.set_input_registers(186, [Tipo_mov])
    time.sleep(1)

    while server.data_bank.get_holding_registers(331) == [0]:
        time.sleep(0.1)
    
    


'''def is_rook_move(move):
    move_obj = chess.Move.from_uci(move)
    piece = board.piece_at(move_obj.from_square)
    return piece.symbol().lower() == 'k' and abs(move_obj.from_square - move_obj.to_square) == 2'''

'''def is_rook_move(move):
    move_obj = chess.Move.from_uci(move)
    piece = board.piece_at(move_obj.from_square)
    
    # Verifica se há uma peça na casa de origem e se é um rei
    if piece and piece.symbol().lower() == 'k' and abs(move_obj.from_square - move_obj.to_square) == 2:
        return True
    else:
        return False'''


def roque(mov_robot):
    global houve_roque
    print(mov_robot)
    if mov_robot == "e8g8" and houve_roque==0:
        print("Roque curto (kingside)")
        houve_roque=1
        roque_curto = [7, 8, 5, 8]
        data_sent = [float((i * 45) + 20) for i in roque_curto]  # mm
        time.sleep(0.2)
        server.data_bank.set_input_registers(180, data_sent)
    
        Tipo_mov = 3
        print(Tipo_mov)
        
        time.sleep(1)
        server.data_bank.set_input_registers(186, [Tipo_mov])
        time.sleep(1)

        while server.data_bank.get_holding_registers(331) == [0]:
            time.sleep(0.1)
        
            

    elif mov_robot == "e8c8" and houve_roque==0:
        print("Roque longo (queenside)")
        houve_roque=1
        roque_longo = [0, 8, 3, 8]
        data_sent = [float((i * 45) + 20) for i in roque_longo]  # mm
        time.sleep(0.2)
        server.data_bank.set_input_registers(180, data_sent)

        Tipo_mov = 3
        print(Tipo_mov)
        time.sleep(1)
        server.data_bank.set_input_registers(186, [Tipo_mov])
        time.sleep(1)

        while server.data_bank.get_holding_registers(331) == [0]:
            time.sleep(0.1)

    else:
        print("Não é roque")


print('Starting server...')
server.start()
print('Server is online')

# Variaveis
variavel = 0
houve_roque=0
contador=0
i_y=0

mov_robot_obj = None

executou_bloco_do_jogador = False
executou_bloco_do_robo = True
while True:
    if not board.is_checkmate() and not board.is_stalemate():
        server.data_bank.set_input_registers(184, [0])

        
        if server.data_bank.get_holding_registers(330) == [1]:
            variavel = 1 - variavel  # Toggle between 0 and 1
            print('Entrou no botao')
            try:
                contador=0
                mov_user = jogada_realizada_adversario(jogada_anterior,cor_anterior)
                print(mov_user[0])
                board.push_san(mov_user[0])

                executou_bloco_do_jogador = True
                executou_bloco_do_robo = False
            
            except chess.IllegalMoveError as e:
                print(f"Erro ao fazer o movimento: {e}")
                
                while(contador<3):
                    server.data_bank.set_input_registers(184, [0])
                    time.sleep(1)
                    server.data_bank.set_input_registers(184, [2])
                    time.sleep(1)
                    contador+=1

                #cv.namedWindow("Imagem com Grid e Rótulos e circulos", cv.WINDOW_NORMAL) 
    
                # Using resizeWindow() 
                #cv.resizeWindow("Imagem com Grid e Rótulos e circulos", 800, 800) 
    
                # Displaying the image 
                #cv.imshow("Imagem com Grid e Rótulos e circulos", mov_user[3]) 
                #cv.waitKey(0)

                variavel=0
                executou_bloco_do_jogador = False
                executou_bloco_do_robo = True

        if variavel == 0 and not executou_bloco_do_jogador:
            server.data_bank.set_input_registers(184, [1])
            time.sleep(0.2)

        
        if variavel == 1 and not executou_bloco_do_robo:
            jogada_anterior = mov_user[1]
            cor_anterior=mov_user[2]
            server.data_bank.set_input_registers(184, [0])
            server.data_bank.set_input_registers(184, [2])

            stockfish.set_fen_position(board.fen())
            mov_robot = stockfish.get_best_move()


            tabuleiro_inicio = board.copy()
            board.push_san(mov_robot)
            tabuleiro_final = board.copy()
            
                           
            verifica_roque=roque(mov_robot)
            
            
            manda_modbus = conversao_stockfish(mov_robot)

            
            cor_anterior = {square: 'white' if tabuleiro_final.piece_at(chess.parse_square(square)).color == chess.WHITE else 'black' for square in chess.SQUARE_NAMES if tabuleiro_final.piece_at(chess.parse_square(square)) is not None}
            time.sleep(1)

            stockfish.set_fen_position(board.fen())
            print("Vez peça preta")
            print(stockfish.get_board_visual())
            print(manda_modbus)
            print("")
            time.sleep(1)


            empty_squares = [chess.square_name(square) for square in chess.SQUARES if board.piece_at(square) is None]
            jogada_anterior=empty_squares
            
    
            manda_robo(manda_modbus,tabuleiro_inicio, tabuleiro_final)
            time.sleep(0.2)

            server.data_bank.set_input_registers(188, [0])
            time.sleep(0.2)
            server.data_bank.set_input_registers(186, [0])

            executou_bloco_do_jogador = False
            executou_bloco_do_robo = True
            variavel = 0

        if board.is_check():
            
            server.data_bank.set_input_registers(184, [0])
            time.sleep(0.2)
            server.data_bank.set_input_registers(184, [1])
            time.sleep(0.2)
            server.data_bank.set_input_registers(184, [0])
            time.sleep(0.2)
            server.data_bank.set_input_registers(184, [2])
            time.sleep(0.2)
            print("O jogo está em xeque!")        

        if board.is_checkmate():
            print("Cheque mate")
            server.data_bank.set_input_registers(184, [1])
            time.sleep(0.2)
            server.data_bank.set_input_registers(184, [2])

            if board.turn:
                print("O vencedor é o jogador das peças pretas!")
                king_square = board.king(chess.WHITE)
                king_position = chess.square_name(king_square)
                print(king_position)
                manda_modbus = conversao_stockfish(king_position)
                print(manda_modbus)
                data_sent = [float((i * 45) + 20) for i in manda_modbus]  # mm
                server.data_bank.set_input_registers(180, data_sent)
                time.sleep(0.2)
                
                Tipo_mov = 2  # Captura

                i_y=random.randint(50,400)
                i_x=random.randint(0,100)
                server.data_bank.set_input_registers(187,[i_y])
                server.data_bank.set_input_registers(188,[i_x])

                time.sleep(1)
                server.data_bank.set_input_registers(186, [Tipo_mov])
                time.sleep(1)
                while server.data_bank.get_holding_registers(331) == [0]:
                    time.sleep(0.2)
            
            else:
                print("O vencedor é o jogador das peças brancas!")

            break

        if board.is_stalemate():
            print("Empate por falta de movimentos possíveis.")
            break


        


    
    











