import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args
import signal
import sys
import copy

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
paused = True
size = options.size
is_points= options.points



if options.no_color:
    canvas_bg = "black"
    fill_color = "white"
    outline_color = "black"
else:
    canvas_bg = "blue"
    fill_color = "white"
    outline_color = "black"
margin=5
selected_index=0
parameters = ["num_points", "max_speed", "neighbor_radius", "sep_weight", "align_weight", "coh_weight" , "size", "random_speed", "random_angle", "is_points", "refresh_ms", "width", "height"]

# Sauvegarde profonde
max_speed_init = copy.deepcopy(max_speed)
neighbor_radius_init = copy.deepcopy(neighbor_radius)
num_points_init = copy.deepcopy(num_points)
width_init = copy.deepcopy(width)
height_init = copy.deepcopy(height)
refresh_ms_init = copy.deepcopy(refresh_ms)
random_speed_init = copy.deepcopy(random_speed)
random_angle_init = copy.deepcopy(random_angle)
sep_weight_init = copy.deepcopy(sep_weight)
align_weight_init = copy.deepcopy(align_weight)
coh_weight_init = copy.deepcopy(coh_weight)
size_init = copy.deepcopy(size)
is_points_init = copy.deepcopy(is_points)

def app():

    def restore_options():
        global max_speed, neighbor_radius, num_points, width, height
        global refresh_ms, random_speed, random_angle
        global sep_weight, align_weight, coh_weight
        global paused, size, is_points
        
        max_speed = copy.deepcopy(max_speed_init)
        neighbor_radius = copy.deepcopy(neighbor_radius_init)
        num_points = copy.deepcopy(num_points_init)
        width = copy.deepcopy(width_init)
        height = copy.deepcopy(height_init)
        refresh_ms = copy.deepcopy(refresh_ms_init)
        random_speed = copy.deepcopy(random_speed_init)
        random_angle = copy.deepcopy(random_angle_init)
        sep_weight = copy.deepcopy(sep_weight_init)
        align_weight = copy.deepcopy(align_weight_init)
        coh_weight = copy.deepcopy(coh_weight_init)
        size = copy.deepcopy(size_init)

    is_points = copy.deepcopy(is_points_init)    
    def draw_status():
        lines = [
            f"num_points      : {num_points}",
            f"max_speed       : {max_speed:.2f}",
            f"neighbor_radius : {neighbor_radius}",
            f"sep_weight      : {sep_weight:.2f}",
            f"align_weight    : {align_weight:.2f}",
            f"coh_weight      : {coh_weight:.2f}",
            f"size            : {size}",
            f"random_speed    : {random_speed}",
            f"random_angle    : {random_angle}",
            f"is_points       : {is_points}",
            f"refresh_ms      : {refresh_ms}",
            f"width           : {width}",
            f"height          : {height}",
            f"",
            f"",
            f"",
            f"space to unpause/pause",
            f"r to reset parameters",
            f"enter to frame",

        ]

        x_text = width + 10
        y_text = 10

        # Supprime l'ancien texte de statut avant de redessiner
        canvas.delete("status")
        for i, line in enumerate(lines):
            fill = fill_color
            if i == selected_index:
                fill = "red"  # couleur de la sélection
                line = line + " <"
            canvas.create_text(
                x_text,
                y_text + i * 18,
                anchor="nw",
                fill=fill,
                font=("Consolas", 10),
                tags="status",
                text=line
            )

    def on_key(event):
        global selected_index, num_points, max_speed, neighbor_radius, sep_weight, align_weight, coh_weight, size, random_speed, random_angle, is_points, refresh_ms, width, height

        if event.keysym == "Up":
            selected_index = (selected_index - 1) % len(parameters)
        elif event.keysym == "Down":
            selected_index = (selected_index + 1) % len(parameters)
        elif event.keysym == "Right":
            param = parameters[selected_index]
            if param == "num_points":
                num_points = min(num_points + 1, 1000)
                generate_points()
            elif param == "max_speed":
                max_speed = min(max_speed + 1, 100)
            elif param == "neighbor_radius":
                neighbor_radius += 1
            elif param == "sep_weight":
                sep_weight = min(sep_weight + 1, 10)  
            elif param == "align_weight":
                align_weight = min(align_weight + 1, 10)
            elif param == "coh_weight":
                coh_weight = min(coh_weight + 1, 10)
            elif param == "size":
                size = min(size + 1, 3)
            elif param == "random_speed":
                random_speed = min(random_speed + 1, 100) 
            elif param == "random_angle":
                random_angle += 1
            elif param == "is_points":
                is_points = not is_points
            elif param == "refresh_ms":
                refresh_ms += 10
            elif param == "width":
                width = min(width + 1, 1500)
            elif param == "height":
                height = min(height + 1, 1000)                                                                                                                   
        elif event.keysym == "Left":
            param = parameters[selected_index]
            if param == "num_points":
                num_points = max(num_points - 1, 1)
            elif param == "max_speed":
                max_speed = max(max_speed - 1, 0)
            elif param == "neighbor_radius":
                neighbor_radius = max(neighbor_radius - 1, 0)
            elif param == "sep_weight":
                sep_weight = max(sep_weight - 1, 0) 
            elif param == "align_weight":
                sep_weight = max(sep_weight - 1, 0) 
            elif param == "coh_weight":
                sep_weight = max(sep_weight - 1, 0) 
            elif param == "size":
                size = max(size - 1, 1)
            elif param == "random_speed":
                random_speed = max(random_speed - 1, 0) 
            elif param == "random_angle":
                random_angle -= 1
            elif param == "is_points":
                is_points = not is_points
            elif param == "refresh_ms":
                refresh_ms = max(refresh_ms - 10, 10)
            elif param == "width":
                width = max(width - 1, 200)
            elif param == "height":
                height = max(height - 1, 300)                 
        elif event.char.lower() == 'r':
            restore_options()
        draw_status()

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


    def limit_speed(vx, vy):
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > max_speed:
            vx = (vx / speed) * max_speed
            vy = (vy / speed) * max_speed
        return vx, vy

    def generate_points():
        global velocities

        if not points: 
            velocities = []
            for _ in range(num_points):
                px = random.randint(margin, width - margin)
                py = random.randint(margin, height - margin)
                points.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            # Supprimer les points hors du rectangle
            inside_points = []
            inside_velocities = []
            for (x, y), (vx, vy) in zip(points, velocities):
                if 0 + margin <= x <= width - margin and 0 + margin <= y <= height - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
                # Sinon on "kill" l'oiseau en ne le gardant pas

            points[:] = inside_points
            velocities[:] = inside_velocities            
            # Calcul Reynolds
            new_velocities = []
            current_count = len(points)
            
            # Ajouter aléatoirement des oiseaux
            if num_points > current_count:
                for _ in range(num_points - current_count):
                    px = random.randint(margin, width - margin)
                    py = random.randint(margin, height - margin)
                    points.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, max_speed)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Supprimer aléatoirement des oiseaux
            elif num_points < current_count:
                for _ in range(current_count - num_points):
                    idx = random.randint(0, len(points) - 1)
                    points.pop(idx)
                    velocities.pop(idx)            
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
                speed_factor = 1 + random.uniform(-1 * random_speed / 100, random_speed / 100)
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

    def draw_rectangle():
        canvas.delete("boundary")
        canvas.create_rectangle(
            0, 0, width, height,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def draw_canvas():
        canvas.config(width=width + 300, height=height)

    def on_enter(event):
        global paused
        paused = True
        draw_canvas()
        draw_status()
        generate_points()
        draw_rectangle()

    def update():
        if not paused:
            draw_canvas()
            draw_status()
            generate_points()
            draw_rectangle()
        root.after(refresh_ms, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)


    def toggle_pause(event=None):
        global paused
        paused = not paused
        draw_status()


                
    root = tk.Tk()
    root.title("pybirdsreynolds")

    canvas = tk.Canvas(root, width=width+300, height=height, bg=canvas_bg)
    canvas.pack()

    points = [] 
    point_ids = []

    draw_canvas()
    draw_status()
    generate_points()
    draw_rectangle()

    root.bind("<Return>", on_enter)
    root.bind("<space>", toggle_pause)
    root.bind("<Key>", on_key)

    signal.signal(signal.SIGINT, signal_handler)
    update()
    root.mainloop()

