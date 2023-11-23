import keyboard
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
import time
import string
import os
 

dif=[]
jogada_anterior=['a3', 'a4', 'a5', 'a6', 'b3', 'b4', 'b5', 'b6', 'c3', 'c4', 'c5', 'c6', 'd3', 'd4', 'd5', 'd6', 'e3', 'e4', 'e5', 'e6', 'f3', 'f4', 'f5', 'f6', 'g3', 'g4', 'g5', 'g6', 'h3', 'h4', 'h5', 'h6']
# Inicialize a câmera
cam_port = 0
cam = cv.VideoCapture(cam_port)

# Set camera parameters
cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)   # Set frame width
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)   # Set frame height
cam.set(cv.CAP_PROP_BRIGHTNESS, 0.5)    # Set brightness (0.0 to 1.0)
cam.set(cv.CAP_PROP_CONTRAST, 0.8)      # Set contrast (0.0 to 1.0)
cam.set(cv.CAP_PROP_SATURATION, 0.5)    # Set saturation (0.0 to 1.0)
cam.set(cv.CAP_PROP_EXPOSURE, -4)       # Set exposure (-7.0 to -1.0 for manual exposure)


# Verifique se a captura de vídeo foi bem-sucedida
if not cam.isOpened():
    print("Erro ao abrir a câmera.")
else:
    # Leia a entrada da câmera
    time.sleep(3)
    ret, image = cam.read()

    if not ret:
        print("Erro ao capturar o quadro da câmera.")
    else:
        cv.imshow("original", image)
        cv.waitKey(0)
        cv.destroyAllWindows()

        cv.imwrite("board.png", image)

    board=image
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # lower boundary RED color range values; Hue (0 - 10)
    lower1 = np.array([0, 120, 150])
    upper1 = np.array([10, 255, 255])

    # upper boundary RED color range values; Hue (160 - 180)
    lower2 = np.array([160,200,20])
    upper2 = np.array([179,255,255])

    lower_mask = cv.inRange(image, lower1, upper1)
    upper_mask = cv.inRange(image, lower2, upper2)

    full_mask = lower_mask + upper_mask
    result = cv.bitwise_and(image, image, mask=full_mask)

    #realizando uma erosao seguida de uma dilatacao, na mascara
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    clean = cv.morphologyEx(full_mask, cv.MORPH_OPEN, kernel)
    clean = cv.medianBlur(clean,5)
    
    cam.release()
    cv.destroyAllWindows()

#cv.imshow('mask', clean)
#cv.imshow('result', result)
cv.imwrite("board_dots.png", clean)
#cv.waitKey(0)
#cv.destroyAllWindows()

img = cv.imread('board_dots.png', cv.COLOR_BGR2GRAY)
# Get the dimensions of the image
height, width = img.shape

# Define the range of columns for the left and right sides (20%)
left_range = int(width * 0.2)
right_range = int(width * 0.8)

# # Iterate through each pixel
# for y in range(height):
#     for x in range(width):
#         # Check if the pixel is on the 20% left or right side
#         if x <= left_range or x >= right_range:
#             # Check if the pixel color is (255, 255, 255)
#             if img[y, x] == 255:
#                 # Change the pixel color to (0, 0, 0)
#                 img[y, x] = 0

# Display the modified image
#cv.imshow('Modified Image', img)
#cv.waitKey(0)
#cv.destroyAllWindows()

circles = cv.HoughCircles(img,cv.HOUGH_GRADIENT,dp=1,minDist=300,param1=3,param2=5,minRadius=0,maxRadius=20)
#print(circles)

x_centro_ref=0
y_centro_ref=0
bottom_right=0
bottom_left=0
top_right=0
top_left=0

cimg1 = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
circles = np.uint16(np.around(circles))
for i in circles[0,:]:
    if i[0]>width/2:
        if i[1]>height/2:
            bottom_right=i
        if i[1]<height/2:
            top_right=i
    if i[0]<width/2:
        if i[1]>height/2:
            bottom_left=i
        if i[1]<height/2:
            top_left=i

    x_centro_ref=x_centro_ref+i[0]
    y_centro_ref=y_centro_ref+i[1]
    # draw the outer circle
    cv.circle(cimg1,(i[0],i[1]),i[2],(0,255,0),2)
    # draw the center of the circle
    cv.circle(cimg1,(i[0],i[1]),2,(0,0,255),3)

plt.imshow(cimg1)
plt.show()

# Window name in which image is
# displayed
window_name = 'Image'

# Polygon corner points coordinates
pts = np.array([[top_left[0], top_left[1]], [top_right[0], top_right[1]], [bottom_right[0], bottom_right[1]],[bottom_left[0], bottom_left[1]]],
            np.int32)

pts = pts.reshape((-1, 1, 2))

isClosed = True

# Blue color in BGR
color = (255, 0, 0)

# Line thickness of 2 px
thickness = 2

# Using cv2.polylines() method
# Draw a Blue polygon with 
# thickness of 1 px
square = cv.polylines(board, [pts], 
                    isClosed, color, thickness)

# Criar a máscara preta do mesmo tamanho da imagem
mask = np.zeros_like(board)

#Preencha o polígono na máscara com branco
cv.fillPoly(mask, [pts], (255, 255, 255))

# Aplique a máscara à imagem original para obter a ROI
result = cv.bitwise_and(board, mask)

# Encontre os limites da região não-nula na máscara
(y, x) = np.where(mask[:, :, 0] != 0)
(top_y, bottom_y) = (np.min(y), np.max(y))
(left_x, right_x) = (np.min(x), np.max(x))

# Corte a região de interesse da imagem
cropped_image = result[top_y:bottom_y, left_x:right_x]

# Exibir a imagem original, o polígono e a imagem cortada
#cv.imshow('Imagem Original', board)
#cv.imshow('Polígono', square)
#cv.imshow('Imagem Cortada', cropped_image)
cv.imwrite("board_square.png", cropped_image)

#cv.waitKey(0)


# Convert to RGB so as to display via matplotlib
# Using Matplotlib we can easily find the coordinates
# of the 4 points that is essential for finding the 
# transformation matrix
img_copy = cv.cvtColor(square,cv.COLOR_BGR2RGB)

# Defina os pontos na ordem correta
input_pts = np.float32([[top_left[0], top_left[1]],
                        [bottom_left[0], bottom_left[1]],
                        [bottom_right[0], bottom_right[1]],
                        [top_right[0], top_right[1]]])

# Defina as coordenadas de saída
output_pts = np.float32([[0, 0], [0, height],
                        [width, height], [width, 0]])

# Calcule a matriz de transformação
M = cv.getPerspectiveTransform(input_pts, output_pts)

# Aplique a transformação de perspectiva
out = cv.warpPerspective(img_copy, M, (img_copy.shape[1], img_copy.shape[0]), flags=cv.INTER_LINEAR)

#cv.imshow('Imagem Cortada', out)
#cv.waitKey(0)
# Round to next smaller multiple of 8
def round_down_to_next_multiple_of_8(a):
    return a & (-8)

# Read image, and shrink to quadratic shape with width and height of
# next smaller multiple of 8
img = out

wh = np.min(round_down_to_next_multiple_of_8(np.array(img.shape[:2])))
#print(wh)
img = cv.resize(img, (wh, wh))

# Prepare some visualization output
out2 = img.copy()
out2 = cv.rotate(out2, cv.ROTATE_180) 

#plt.imshow(img)
#plt.show()


# Assuming 'out2' is your image
altura, largura = out2.shape[:2]

linhas = 8
colunas = 8
bloco_altura = altura // linhas
bloco_largura = largura // colunas

blocos = {}
blocos_sem_circulos = []

letras_linha = string.ascii_lowercase[:linhas]
numeros_coluna = [str(i + 1) for i in range(colunas)]

for i, letra in enumerate(letras_linha):
    for j, numero in enumerate(numeros_coluna):
        nome_bloco = f"{letra}{numero}"
        bloco = out2[i * bloco_altura: (i + 1) * bloco_altura, j * bloco_largura: (j + 1) * bloco_largura]
        blocos[nome_bloco] = bloco

        gray = cv.cvtColor(bloco, cv.COLOR_BGR2GRAY)
        gray = cv.medianBlur(gray, 5)
        circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=0, maxRadius=0)

        if circles is None:
            blocos_sem_circulos.append(nome_bloco)
        else:
            circles = np.uint16(np.around(circles))

            # Adjust circle coordinates according to the block position in the original image
            for circle in circles[0, :]:
                center = (circle[0] + j * bloco_largura, circle[1] + i * bloco_altura)  # Adjusting center coordinates
                radius = circle[2]
                cv.circle(out2, center, radius, (0, 255, 0), 2)

        cv.putText(out2, nome_bloco, (j * bloco_largura + 10, (i + 1) * bloco_altura - 10),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

for i in range(1, linhas):
    cv.line(out2, (0, i * bloco_altura), (largura, i * bloco_altura), (0, 255, 0), 2)
for j in range(1, colunas):
    cv.line(out2, (j * bloco_largura, 0), (j * bloco_largura, altura), (0, 255, 0), 2)

cv.imshow('Imagem com Grid e Rótulos', out2)
cv.waitKey(0)
cv.destroyAllWindows()

# Imprimir a lista de blocos sem círculos
#print(" Chessboard Empty Slots:")
#print(blocos_sem_circulos)
jogada_seguinte=blocos_sem_circulos

# Convert lists to sets and find the difference

dif.append(list(set(jogada_seguinte).symmetric_difference(set(jogada_anterior))))
dif[0]=dif[0][1]+dif[0][0]
print(dif)

#dif.clear()
#print(dif)
jogada_anterior=jogada_seguinte
#print(jogada_anterior)




