from stockfish import Stockfish
import chess
import re
import time

from pyModbusTCP.server import ModbusServer,DataBank
from time import sleep
from random import uniform

from FINAL_VISAO import jogada_realizada_adversario

stockfish_path = "C:\\Users\\ferna\\OneDrive\\Documentos\\Insper\\7Periodo\\RoboticaIndustrial\\Projeto Xadrez\\stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(stockfish_path)

board=chess.Board()

SERVER_ADDRESS = '10.103.16.103'
SERVER_PORT = 502
server = ModbusServer(SERVER_ADDRESS, SERVER_PORT, no_block = True)

dif=[]
jogada_anterior=['a3', 'a4', 'a5', 'a6', 'b3', 'b4', 'b5', 'b6', 'c3', 'c4', 'c5', 'c6', 'd3', 'd4', 'd5', 'd6', 'e3', 'e4', 'e5', 'e6', 'f3', 'f4', 'f5', 'f6', 'g3', 'g4', 'g5', 'g6', 'h3', 'h4', 'h5', 'h6']


def conversao_stockfish(mov_robot):
    mov_robot_convert=re.findall(r'[A-Ha-h]|[0-8]', mov_robot)
    for i in range(len(mov_robot_convert)):
            if mov_robot_convert[i].isdigit():
                mov_robot_convert[i] = int(mov_robot_convert[i])
            else:
                mov_robot_convert[i] = ord(mov_robot_convert[i])- ord('a') 
    return mov_robot_convert

def manda_robo(manda_modbus):
    
    DATA_SENT = [float((i * 45)+20) for i in manda_modbus] #mm
    server.data_bank.set_input_registers(180,DATA_SENT)
    time.sleep(0.2)
    server.data_bank.set_input_registers(186,[1])
    while server.data_bank.get_holding_registers(331) == [0]:
        time.sleep(0.1)
           
    

def is_rook_move(move):
    move_obj = chess.Move.from_uci(move)
    piece = board.piece_at(move_obj.from_square)
    return piece.symbol().lower() == 'k' and abs(move_obj.from_square - move_obj.to_square) == 2


print('Starting server...')
server.start()
print('Server is online')

#Variaveis
contador_de_xeques=0
variavel=0

executou_bloco_do_jogador=False
executou_bloco_do_robo=True
while True:

    if not board.is_checkmate() and not board.is_stalemate():
        
        
        
        if server.data_bank.get_holding_registers(330) == [1]:
            variavel = 1-variavel # Toggle between 0 and 1
            print('Entrou no botao')
            mov_user=jogada_realizada_adversario(jogada_anterior)
            print(mov_user)
            jogada_anterior=mov_user[1]
            board.push_san(mov_user[0])
            print(mov_user)
            print('Entrou no botao2')
            executou_bloco_do_jogador=True
            executou_bloco_do_robo=False
            

        if variavel == 0 and not executou_bloco_do_jogador:
            print('Entrou no variavel 0')
            time.sleep(0.2)

        if variavel == 1 and not executou_bloco_do_robo:
            
        
            stockfish.set_fen_position(board.fen())
            mov_robot=stockfish.get_best_move()
            #mov_robot='a7a5'
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
                    print("A peça capturada foi: ", tabuleiro_inicio.piece_at(square))
                    server.data_bank.set_input_registers(188,[1])#Captura

            stockfish.set_fen_position(board.fen())
            print("Vez peça preta")
            print(stockfish.get_board_visual())
            print(manda_modbus)
            print("")
            time.sleep(1)

            empty_squares = [chess.square_name(square) for square in chess.SQUARES if board.piece_at(square) is None]
            jogada_anterior.extend(empty_squares)

            manda_robo(manda_modbus)
            time.sleep(0.2)

            server.data_bank.set_input_registers(188,[0])
            time.sleep(0.2)
            server.data_bank.set_input_registers(186,[0]) 
        

            executou_bloco_do_jogador=False
            executou_bloco_do_robo==True
            variavel=0
                


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

        if board.is_stalemate():
            print("Empate por falta de movimentos possíveis.")
            break

        


    
    











