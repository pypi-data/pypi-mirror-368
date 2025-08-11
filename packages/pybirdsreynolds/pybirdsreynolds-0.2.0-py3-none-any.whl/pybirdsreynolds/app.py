import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args
import signal
import sys
"""
pybirdsreynolds use case
"""

options = compute_args()
max_speed = options.max_speed
neighbor_radius = options.neighbor_radius
num_points = options.num_points
width, height = options.width, options.height
refresh_ms = options.refresh_ms
random_speed = options.random_speed
random_angle = options.random_angle
sep_weight = options.sep_weight
align_weight = options.align_weight
coh_weight = options.coh_weight
paused = options.interactive 
size = options.size
is_points=options.points
if options.no_color:
    canvas_bg = "black"
    fill_color = "white"
    outline_color = "black"
else:
    canvas_bg = "blue"
    fill_color = "white"
    outline_color = "black"

def app():



    def draw_points():
        for pid in point_ids:
            canvas.delete(pid)
        point_ids.clear()

        triangle_size = 6*size
        triangle_width = 4*size

        for (x, y), (vx, vy) in zip(points, velocities):
            if is_points:  # Mode point (pixel unique)
                pid = canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=fill_color, outline=outline_color)
            else:
                angle = math.atan2(vy, vx)

                # Coordonnées du sommet (pointe vers la direction)
                tip_x = x + math.cos(angle) * triangle_size
                tip_y = y + math.sin(angle) * triangle_size

                # Coordonnées des coins arrière (base)
                left_angle = angle + math.radians(150)
                right_angle = angle - math.radians(150)

                left_x = x + math.cos(left_angle) * triangle_width
                left_y = y + math.sin(left_angle) * triangle_width

                right_x = x + math.cos(right_angle) * triangle_width
                right_y = y + math.sin(right_angle) * triangle_width

                pid = canvas.create_polygon(
                    tip_x, tip_y,
                    left_x, left_y,
                    right_x, right_y,
                    fill=fill_color, outline=outline_color
                )
            point_ids.append(pid)


    def limit_speed(vx, vy, max_speed=max_speed):
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > max_speed:
            vx = (vx / speed) * max_speed
            vy = (vy / speed) * max_speed
        return vx, vy

    def generate_points(max_speed=max_speed):
        global velocities

        if not points: 
            velocities = []
            for _ in range(num_points):
                px = random.randint(5, width - 5)
                py = random.randint(5, height - 5)
                points.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            # Calcul Reynolds
            new_velocities = []
            for i, (x, y) in enumerate(points):
                move_sep_x, move_sep_y = 0, 0
                move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = 0, 0, 0, 0
                move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
                neighbors = 0

                for j, (x2, y2) in enumerate(points):
                    if i == j:
                        continue
                    dist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
                    if dist < neighbor_radius and dist > 0:
                        # SEPARATION
                        # Si un voisin est trop proche, on ajoute un vecteur pour s’en éloigner (direction opposée au voisin).
                        move_sep_x += (x - x2) / dist
                        move_sep_y += (y - y2) / dist
                        # ALIGNEMENT
                        # On ajoute la vitesse du voisin pour que l’agent tende à s’aligner avec lui.
                        # on fait la division plus bas
                        vx2, vy2 = velocities[j]
                        move_align_x_tmp += vx2
                        move_align_y_tmp += vy2
                        # COHESION
                        # On ajoute la position du voisin pour calculer ensuite un point moyen, afin de se rapprocher du centre du groupe.
                        # on fait la division plus bas
                        move_coh_x_tmp += x2
                        move_coh_y_tmp += y2
                        neighbors += 1

                if neighbors > 0:
                    move_align_x = move_align_x_tmp/neighbors
                    move_align_y = move_align_y_tmp/neighbors
                    move_coh_x = move_coh_x_tmp/neighbors
                    move_coh_y = move_coh_y_tmp/neighbors
                    move_coh_x = move_coh_x - x
                    move_coh_y = move_coh_y - y



                vx, vy = velocities[i]
                vx += sep_weight * move_sep_x + align_weight * move_align_x + coh_weight * move_coh_x
                vy += sep_weight * move_sep_y + align_weight * move_align_y + coh_weight * move_coh_y

                vx, vy = limit_speed(vx, vy)

                #ALEA
                speed_factor = 1 + random.uniform(-1 * random_speed, random_speed)
                vx *= speed_factor
                vy *= speed_factor
                angle = math.atan2(vy, vx)
                angle += math.radians(random.uniform(-1 * random_angle, random_angle))
                speed = math.sqrt(vx**2 + vy**2)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                new_velocities.append((vx, vy))

            velocities = new_velocities

            # Mise à jour des positions
            new_points = []
            for (x, y), (vx, vy) in zip(points, velocities):
                nx = x + vx
                ny = y + vy

                # Rebonds 
                margin = 5
                if nx < margin:
                    nx = margin + (margin - nx)
                    vx = -vx
                elif nx > width - margin:
                    nx = (width - margin) - (nx - (width - margin))
                    vx = -vx
                if ny < margin:
                    ny = margin + (margin - ny)
                    vy = -vy
                elif ny > height - margin:
                    ny = (height - margin) - (ny - (height - margin))
                    vy = -vy
                idx = points.index((x, y))
                velocities[idx] = (vx, vy)
                new_points.append((nx, ny))

            points[:] = new_points

        draw_points()

    def on_enter(event):
        generate_points()

    def update():
        if not paused:
            generate_points()
        root.after(refresh_ms, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)


    def toggle_pause(event=None):
        global paused
        paused = not paused
        if paused:
            print("Paused")
        else:
            print("Resumed")

                
    root = tk.Tk()
    root.title("pybirdsreynolds")

    canvas = tk.Canvas(root, width=width, height=height, bg=canvas_bg)
    canvas.pack()

    canvas.create_rectangle(
        0, 0, width, height,
        outline=fill_color, width=5
    )

    points = [] 
    point_ids = []

    generate_points()

    root.bind("<Return>", on_enter)
    root.bind("<space>", toggle_pause) 

    signal.signal(signal.SIGINT, signal_handler)
    update()
    root.mainloop()

