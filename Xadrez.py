from stockfish import Stockfish
import chess
import re
import time
from pyModbusTCP.server import ModbusServer, DataBank
import cv2 as cv
from FINAL_VISAO import jogada_realizada_adversario

stockfish_path = "C:\\Users\\ferna\\OneDrive\\Documentos\\Insper\\7Periodo\\RoboticaIndustrial\\Projeto Xadrez\\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(stockfish_path)

stockfish.set_depth(20)#How deep the AI looks
stockfish.set_skill_level(20)#Highest rank stockfish

board = chess.Board()

SERVER_ADDRESS = '10.103.16.103'
SERVER_PORT = 502
server = ModbusServer(SERVER_ADDRESS, SERVER_PORT, no_block=True)

jogada_anterior = ['a3', 'a4', 'a5', 'a6', 'b3', 'b4', 'b5', 'b6', 'c3', 'c4', 'c5', 'c6', 'd3', 'd4', 'd5', 'd6', 'e3', 'e4', 'e5', 'e6', 'f3', 'f4', 'f5', 'f6', 'g3', 'g4', 'g5', 'g6', 'h3', 'h4', 'h5', 'h6']
cor_anterior={'a1': 'white', 'a2': 'white', 'a7': 'black', 'a8': 'black', 'b1': 'white', 'b2': 'white', 'b7': 'black', 'b8': 'black', 'c1': 'white', 'c2':'white', 'c7': 'black', 'c8': 'black', 'd1': 'white', 'd2': 'white', 'd7': 'black', 'd8': 'black', 'e1': 'white', 'e2': 'white', 'e7': 'black', 'e8': 'black','f1': 'white', 'f2': 'white', 'f7': 'black', 'f8': 'black',  'g1': 'white', 'g2': 'white', 'g7': 'black', 'g8': 'black', 'h1': 'white', 'h2': 'white', 'h7': 'black', 'h8': 'black'}

def conversao_stockfish(mov_robot):
    mov_robot_convert = [int(char) if char.isdigit() else ord(char) - ord('a') for char in re.findall(r'[A-Ha-h]|[0-8]', mov_robot)]
    return mov_robot_convert


def manda_robo(manda_modbus, tabuleiro_inicio, tabuleiro_final,houve_roque,manda_o_rei):
    
    if houve_roque == 0:
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
        else:
            Tipo_mov = 1
    
        print(Tipo_mov)
        time.sleep(1)
        server.data_bank.set_input_registers(186, [Tipo_mov])
        time.sleep(1)

        while server.data_bank.get_holding_registers(331) == [0]:
            time.sleep(0.1)
    
    
    else:
        Tipo_mov = 3
        print("Fez roque")
    
        data_sent_rei = [float((i * 45) + 20) for i in manda_o_rei]
        server.data_bank.set_input_registers(180, data_sent_rei)
        

        time.sleep(1)
        server.data_bank.set_input_registers(186, [Tipo_mov])
        time.sleep(1)

        while server.data_bank.get_holding_registers(330) == [0]:
            time.sleep(0.1)

        data_sent_torre = [float((i * 45) + 20) for i in manda_modbus]  # mm
        server.data_bank.set_input_registers(180, data_sent_torre)
        time.sleep(1)
        server.data_bank.set_input_registers(186, [Tipo_mov])
        time.sleep(1)
        
        
        houve_roque = 0

        while server.data_bank.get_holding_registers(331) == [0]:
            time.sleep(0.1)


def is_rook_move(move):
    move_obj = chess.Move.from_uci(move)
    piece = board.piece_at(move_obj.from_square)
    
    # Verifica se há uma peça na casa de origem e se é um rei
    if piece and piece.symbol().lower() == 'k':
        return abs(move_obj.from_square - move_obj.to_square) == 2
    else:
        return False


print('Starting server...')
server.start()
print('Server is online')

# Variaveis
variavel = 0
houve_roque=0
contador=0

executou_bloco_do_jogador = False
executou_bloco_do_robo = True
while True:
    if not board.is_checkmate() and not board.is_stalemate():
        server.data_bank.set_input_registers(184, [0])

        
        if server.data_bank.get_holding_registers(330) == [1]:
        #if variavel==0:
            variavel = 1 - variavel  # Toggle between 0 and 1
            print('Entrou no botao')
            try:
                contador=0
                mov_user = jogada_realizada_adversario(jogada_anterior,cor_anterior)
                print(mov_user)
                jogada_anterior = mov_user[1]
                cor_anterior=mov_user[2]
                board.push_san(mov_user[0])
                print(mov_user)

                executou_bloco_do_jogador = True
                executou_bloco_do_robo = False
            except chess.IllegalMoveError as e:
                print(f"Erro ao fazer o movimento: {e}")
                
                while(contador<=5):
                    server.data_bank.set_input_registers(184, [0])
                    time.sleep(1)
                    server.data_bank.set_input_registers(184, [2])
                    time.sleep(1)
                    server.data_bank.set_input_registers(184, [0])
                    contador+=1

                variavel=0
                executou_bloco_do_jogador = False
                executou_bloco_do_robo = True

        if variavel == 0 and not executou_bloco_do_jogador:
            server.data_bank.set_input_registers(184, [1])
            time.sleep(0.2)

        if variavel == 1 and not executou_bloco_do_robo:
            server.data_bank.set_input_registers(184, [0])
            server.data_bank.set_input_registers(184, [2])

            stockfish.set_fen_position(board.fen())
            mov_robot = stockfish.get_best_move()

            manda_o_rei = []

            tabuleiro_inicio = board.copy()
            board.push_san(mov_robot)
            tabuleiro_final = board.copy()


            if is_rook_move(mov_robot):
                mov_robot_obj = chess.Move.from_uci(mov_robot)
                print("Movimento de rook detectado!")
                king_position_antes = tabuleiro_inicio.square_name(mov_robot_obj.from_square)
                rook_position_antes = tabuleiro_inicio.square_name(mov_robot_obj.to_square)
                
                king_position_depois = tabuleiro_final.square_name(mov_robot_obj.from_square)
                rook_position_depois = tabuleiro_final.square_name(mov_robot_obj.to_square)

    
                houve_roque=1

                manda_o_rei = conversao_stockfish([king_position_antes, king_position_depois])

            if houve_roque == 0: manda_modbus = conversao_stockfish(mov_robot)

            else:
                manda_modbus= conversao_stockfish([rook_position_antes,rook_position_depois])

            
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
            
    
            manda_robo(manda_modbus,tabuleiro_inicio, tabuleiro_final,houve_roque,manda_o_rei)
            time.sleep(0.2)

            server.data_bank.set_input_registers(188, [0])
            time.sleep(0.2)
            server.data_bank.set_input_registers(186, [0])

            executou_bloco_do_jogador = False
            executou_bloco_do_robo = True
            variavel = 0

        if board.is_check():

            print("O jogo está em xeque!")
            

        if board.is_checkmate():
            print("Cheque mate")
            print("O vencedor é o jogador das peças pretas!" if board.turn else "O vencedor é o jogador das peças brancas!")
            break

        if board.is_stalemate():
            print("Empate por falta de movimentos possíveis.")
            break


        


    
    











