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
    
    server.data_bank.set_input_registers(184, [0])  #Desliga led verde 
    server.data_bank.set_input_registers(185, [1])  #Liga led vermelho 
    DATA_SENT = [float(i * 22.5) for i in manda_modbus] #mm
    server.data_bank.set_input_registers(180,DATA_SENT)
    time.sleep(5)


while True:
    print('Starting server...')
    server.start()
    print('Server is online')
    
    server.data_bank.set_input_registers(184, [1])  #Liga led verde
    server.data_bank.set_input_registers(185, [0])  #Desliga led vermelho 
    time.sleep(1)

    if not board.is_checkmate() and not board.is_stalemate():
        print(stockfish.get_board_visual())
        
        mov_user=input("Qual jogada?:")

        #mov_user='a2a3'
        board.push_san(mov_user)
    
        
        stockfish.set_fen_position(board.fen())
        mov_robot=stockfish.get_best_move()

        
        print(conversao_stockfish(mov_robot))
        manda_modbus=(conversao_stockfish(mov_robot))
        
        board.push_san(mov_robot)
        print(stockfish.get_board_visual())
        
        manda_robo(manda_modbus)
    
        if board.is_check():
            print("O jogo está em xeque!")
            # Aqui você pode adicionar a lógica para permitir apenas movimentos do rei

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
    
    
    











