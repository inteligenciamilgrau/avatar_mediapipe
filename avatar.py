import mediapipe as mp
import cv2
import numpy as np
from tkinter import Tk, Canvas, PhotoImage, NW, Button
from PIL import Image, ImageTk
from ctypes import windll

#loomie
#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(3) # caso demore para abrir sua camera, teste esse
cap = cv2.VideoCapture(3, cv2.CAP_DSHOW) # caso demore para abrir sua camera, teste esse

face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def achar_pontos(pontos_da_parte):
    parte = []
    for point in pontos_da_parte:
        ponto_percentual = face_landmarks.landmark[point]
        y, x, z = frame.shape

        ponto_x = int(x * ponto_percentual.x)
        ponto_y = int(y * ponto_percentual.y)

        parte.append([ponto_x, ponto_y])
    return parte

face = face_mesh.FaceMesh(static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5)

if not cap.isOpened():
    print("nao abriu")
    exit()

## opcional: codigo para tirar a barra sem remover o icone
GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(3000, lambda: root.wm_deiconify())

rodando = True

def desligar(event):
    global rodando
    rodando = False

lastClickX = 0
lastClickY = 0
def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))

root = Tk()
root.title('Jarvis')
root.attributes('-transparentcolor','#f0f0f0')
canvas = Canvas(root, width=800, height=600)
canvas.pack()

sem_borda = True
if sem_borda:
    root.overrideredirect(True)  # remove a barra
    root.after(500, lambda: set_appwindow(root))

root.bind('<Button-3>', SaveLastClickPos)
root.bind('<B3-Motion>', Dragging)
root.bind("<ButtonRelease-2>", desligar)

image_init = np.zeros((800, 600, 3), np.uint8)
image_init_tk = ImageTk.PhotoImage(image=Image.fromarray(image_init))
pose_container = canvas.create_image(0, 0, anchor=NW, image=image_init_tk)

windowName = "Imagem Mil Grau"

while rodando:
    ret, frame = cap.read()

    if not ret:
        print("nao tem frame")
        break

    frame_shape = frame.shape
    image = np.zeros((frame_shape[0], frame_shape[1], 3), np.uint8)

    results = face.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mouth_points_1 = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291]  # labio baixo
            mouth_points_2 = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]  # labio cima
            mouth_points_3 = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]  # labio interno baixo
            mouth_points_4 = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]  # labio interno cima

            iris_left = [474, 475, 476, 477]
            iris_right = [469, 470, 471, 472]

            nose_points_1 = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2]
            nose_points_2 = [98, 97, 2, 326, 327, 294, 278, 344, 440, 275, 4, 45, 220, 115, 48, 64, 98]

            face_oval_points = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                         397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
                         150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54,
                         103, 67, 109, 10]

            boca_points = mouth_points_1 + mouth_points_2[::-1]
            boca_points_up = mouth_points_2 + mouth_points_4[::-1]
            boca_points_down = mouth_points_1 + mouth_points_3[::-1]
            iris_points_left = iris_left

            boca = achar_pontos(boca_points)
            boca_u = achar_pontos(boca_points_up)
            boca_d = achar_pontos(boca_points_down)
            iris_l = achar_pontos(iris_left)
            iris_r = achar_pontos(iris_right)
            nose1 = achar_pontos(nose_points_1)
            nose2 = achar_pontos(nose_points_2)
            face_oval = achar_pontos(face_oval_points)

            for point in boca_points:
                ponto_percentual = face_landmarks.landmark[point]
                y, x, z = frame.shape

                ponto_x = int(x * ponto_percentual.x)
                ponto_y = int(y * ponto_percentual.y)

                #boca.append([ponto_x, ponto_y])

                frame = cv2.circle(frame, (ponto_x, ponto_y), 1, (255, 0, 0), 3)

            # desenhar rosto todo
            rosto_todo = True
            if rosto_todo:

                mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections= face_mesh.FACEMESH_TESSELATION,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                landmark_drawing_spec=None)

                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=face_mesh.FACEMESH_CONTOURS,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style(),
                    landmark_drawing_spec=None)

            cv2.fillPoly(image, pts=np.array([face_oval]), color=(255, 255, 255))
            cv2.fillPoly(image, pts=np.array([boca]), color=(255, 0, 0))
            cv2.fillPoly(image, pts=np.array([boca_d]), color=(0, 255, 0))
            cv2.fillPoly(image, pts=np.array([boca_u]), color=(0, 255, 0))
            cv2.fillPoly(image, pts=np.array([iris_l]), color=(255, 255, 0))
            cv2.fillPoly(image, pts=np.array([iris_r]), color=(255, 255, 0))
            cv2.fillPoly(image, pts=np.array([nose1]), color=(0, 0, 255)) # BGR
            cv2.fillPoly(image, pts=np.array([nose2]), color=(0, 0, 255))

    # transparencia
    tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 125, cv2.THRESH_BINARY)
    b, g, r = cv2.split(image)
    image_transparency = cv2.merge([b,g,r, alpha], 4)
    image_transparency_tk = ImageTk.PhotoImage(image=Image.fromarray(image_transparency))
    canvas.itemconfig(pose_container, image=image_transparency_tk)
    root.update()

    aumento = 1.4
    image = cv2.resize(image, (int(frame_shape[1] * aumento), int(frame_shape[0] * aumento)))

cv2.destroyAllWindows()
cap.release()
print("Encerrou")
