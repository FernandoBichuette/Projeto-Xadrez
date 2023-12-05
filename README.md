# Projeto de Róbótica Industrial - automatic chess player

## Introdução

## Visão Computacional

O uso da biblioteca OpenCV, para visão computacional, através da linguagem de programação em Python, foi essencial para avanço do projeto.
Foi utilizada uma Câmera Web Logitech C920e Full HD 30FPS, que captura uma imagem do tabuleiro após a jogada feita pelo adversário. O robô entende que a jogada foi finalizada após o adversário ter apertado o botão de finaização de sua jogada. 

O processo da análise de imagem, cujo objetivo é recohecer a jogada feita pelo adversário, ocorrre nos seguintes passos:
- preparação do tabuleiro
- captura da imagem
- transformação para HSV
- limpeza de imperfeições
- detecção do tabuleiro
- detetecção de casas vazias e cores das peças

### Preparação do tabuleiro
Nos vértices do tabuleiro de xadrez, foi colocado adesivos de cor vermelha, para facilitar a idnetificação pela WebCam. A foto do tabuleiro, pela visão da camera se encontra abaixo.

![Screenshot](screenshot.png)
