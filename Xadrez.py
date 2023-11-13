from stockfish import Stockfish
import chess
import re
import time

from pyModbusTCP.server import ModbusServer,DataBank
from time import sleep
from random import uniform

stockfish_path = "C:\\Users\\ferna\\OneDrive\\Documentos\\Insper\\7° Periodo\\Robotica Industrial\\Projeto Xadrez\\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(stockfish_path)

board=chess.Board()

SERVER_ADDRESS = '10.103.16.103'
SERVER_PORT = 502
server = ModbusServer(SERVER_ADDRESS, SERVER_PORT, no_block = True)


def conversao_stockfish(mov_robot):
    mov_robot_convert=re.findall(r'[A-Ha-h]|[0-8]', mov_robot)
    for i in range(len(mov_robot_convert)):
            if mov_robot_convert[i].isdigit():
                mov_robot_convert[i] = int(mov_robot_convert[i])
            else:
                mov_robot_convert[i] = ord(mov_robot_convert[i])- ord('a') + 1
    return mov_robot_convert

def manda_robo(manda_modbus):
    
    DATA_SENT = [float((i * 45)+22.5) for i in manda_modbus] #mm

    while server.data_bank.get_discrete_inputs(331)==1:
        server.data_bank.set_input_registers(180,DATA_SENT)
        print("entrou")
        time.sleep(10)

def is_rook_move(move):
    move_obj = chess.Move.from_uci(move)
    piece = board.piece_at(move_obj.from_square)
    return piece.symbol().lower() == 'k' and abs(move_obj.from_square - move_obj.to_square) == 2


print('Starting server...')
server.start()
print('Server is online')

#Variaveis
contador_de_xeques=0
state=server.data_bank.get_discrete_inputs(330)


while True:

    server.data_bank.set_input_registers(184, [0])  #Liga led
    time.sleep(1)

    if not board.is_checkmate() and not board.is_stalemate():
        
        stockfish.set_fen_position(board.fen())
        mov_user=stockfish.get_best_move()
        #mov_user=input("Qual jogada?:")
        #mov_user='a2a3'

        board.push_san(mov_user)
        tabuleiro_anterior = board.copy()
        print("Vez peça branca")
        print(stockfish.get_board_visual())
        print("")
        time.sleep(1)

        stockfish.set_fen_position(board.fen())
        mov_robot=stockfish.get_best_move()
        
        if is_rook_move(mov_robot):
            mov_robot_obj = chess.Move.from_uci(mov_robot)
            print("Movimento de rook detectado!")
            king_position = chess.square_name(mov_robot_obj.from_square)
            rook_position = chess.square_name(mov_robot_obj.to_square)
            print(f"Posição do Rei: {king_position}")
            print(f"Posição da Torre: {rook_position}")
            
        
        manda_modbus=(conversao_stockfish(mov_robot))
        
        tabuleiro_inicio = board.copy()
        board.push_san(mov_robot)
        tabuleiro_final = board.copy()

        for square in chess.SQUARES:
            if tabuleiro_final.piece_at(square) is not None and tabuleiro_inicio.piece_at(square) is None:
                print("Uma peça foi capturada na posição: ", chess.square_name(square))
                server.data_bank.set_input_registers(188,[1])#Captura

        stockfish.set_fen_position(board.fen())
        print("Vez peça preta")
        print(stockfish.get_board_visual())
        print(manda_modbus)
        print("")
        time.sleep(1)

        manda_robo(manda_modbus)
        
        time.sleep(1)

        server.data_bank.set_input_registers(180,[0,0,0,0])        
        server.data_bank.set_input_registers(188,[0])#Movimento

        if board.is_check():
            print("O jogo está em xeque!")
            contador_de_xeques+=1
            if contador_de_xeques>=3:
                print("Fim de jogo, empate")
                break

        if board.is_checkmate():
            print("Cheque mate")
            if board.turn:
                print("O vencedor é o jogador das peças pretas!")
            else:
                print("O vencedor é o jogador das peças brancas!")
            break

        elif board.is_stalemate():
            print("Empate por falta de movimentos possíveis.")
            break

    
    











