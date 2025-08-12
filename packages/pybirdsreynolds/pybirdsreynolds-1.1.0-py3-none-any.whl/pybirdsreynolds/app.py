import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args
import signal
import sys
import copy
from importlib.metadata import version

version_prog = version("pybirdsreynolds")
options = compute_args()
max_speed = options.max_speed
neighbor_radius = options.neighbor_radius
num_birds = options.num_birds
width, height = options.width, options.height
refresh_ms = options.refresh_ms
random_speed = options.random_speed
random_angle = options.random_angle
sep_weight = options.sep_weight
align_weight = options.align_weight
coh_weight = options.coh_weight
paused = True
size = options.size
points= options.points
no_color=options.no_color

if no_color:
    canvas_bg = "black"
    fill_color = "white"
    outline_color = "black"
else:
    canvas_bg = "blue"
    fill_color = "white"
    outline_color = "black"

# Sauvegarde profonde
max_speed_init = copy.deepcopy(max_speed)
neighbor_radius_init = copy.deepcopy(neighbor_radius)
num_birds_init = copy.deepcopy(num_birds)
width_init = copy.deepcopy(width)
height_init = copy.deepcopy(height)
refresh_ms_init = copy.deepcopy(refresh_ms)
random_speed_init = copy.deepcopy(random_speed)
random_angle_init = copy.deepcopy(random_angle)
sep_weight_init = copy.deepcopy(sep_weight)
align_weight_init = copy.deepcopy(align_weight)
coh_weight_init = copy.deepcopy(coh_weight)
size_init = copy.deepcopy(size)
points_init = copy.deepcopy(points)
no_color_init= copy.deepcopy(no_color)

params=400
margin=1
selected_index=0
parameters = ["num_birds", "neighbor_radius", "sep_weight", "align_weight", "coh_weight" , "max_speed" , "random_speed", "random_angle", "refresh_ms", "width", "height", "size", "points", "no_color"]

# Dictionnaire de documentation associée
param_docs = {
    "num_birds"      : "Number of birds in the simulation (1–1000, default: 500)",
    "neighbor_radius": "Distance to detect neighbors in pixels (default: 50)",
    "sep_weight"     : "Separation weight (0–10, default: 1)",
    "align_weight"   : "Alignment weight (0–10, default: 1)",
    "coh_weight"     : "Cohesion weight (0–10, default: 1)",
    "max_speed"      : "Maximum speed of birds (1–100, default: 10)",
    "random_speed"   : "Random speed variation ratio (%) (0–100, default: 10)",
    "random_angle"   : "Random angle variation in degrees (0–360, default: 10)",
    "refresh_ms"     : "Refresh interval in milliseconds (min 10, default: 10)",
    "width"          : "Simulation area width (200–1500, default: 1000)",
    "height"         : "Simulation area height (200-1000, default: 500)",
    "size"           : "Visual size of birds (1–3, default: 1)",
    "points"         : "Render birds as points instead of triangles",
    "no_color"       : "Disable colors (monochrome display)"
}

# Correspondance index -> nom du paramètre
param_order = [
    "num_birds",
    "neighbor_radius",
    "sep_weight",
    "align_weight",
    "coh_weight",
    "max_speed",
    "random_speed",
    "random_angle",
    "refresh_ms",
    "width",
    "height",
    "size",
    "points",
    "no_color"
]

def app():

    def restore_options():
        global max_speed, neighbor_radius, num_birds, width, height
        global refresh_ms, random_speed, random_angle
        global sep_weight, align_weight, coh_weight
        global paused, size, points, no_color, canvas_bg, fill_color, outline_color
        
        max_speed = copy.deepcopy(max_speed_init)
        neighbor_radius = copy.deepcopy(neighbor_radius_init)
        num_birds = copy.deepcopy(num_birds_init)
        width = copy.deepcopy(width_init)
        height = copy.deepcopy(height_init)
        refresh_ms = copy.deepcopy(refresh_ms_init)
        random_speed = copy.deepcopy(random_speed_init)
        random_angle = copy.deepcopy(random_angle_init)
        sep_weight = copy.deepcopy(sep_weight_init)
        align_weight = copy.deepcopy(align_weight_init)
        coh_weight = copy.deepcopy(coh_weight_init)
        size = copy.deepcopy(size_init)
        no_color = copy.deepcopy(no_color_init)
        if no_color:
            canvas_bg = "black"
            fill_color = "white"
            outline_color = "black"
        else:
            canvas_bg = "blue"
            fill_color = "white"
            outline_color = "black"    
        points = copy.deepcopy(points_init)    

    def draw():
        draw_canvas()
        draw_status()
        draw_points()
        draw_rectangle()

    def on_next_frame(event):
        global paused
        paused = True
        generate_points_and_facultative_move(True)
        draw()

        
    def toggle_pause(event=None):
        global paused
        paused = not paused
        draw_status()

    def on_other_key(event):
        global selected_index, num_birds, max_speed, neighbor_radius, sep_weight, align_weight, coh_weight, size, random_speed, random_angle, points, refresh_ms, width, height, no_color, canvas_bg, fill_color, outline_color

        if event.keysym == "Up":
            selected_index = (selected_index - 1) % len(parameters)
        elif event.keysym == "Down":
            selected_index = (selected_index + 1) % len(parameters)
        elif event.keysym == "Right":
            param = parameters[selected_index]
            if param == "num_birds":
                num_birds = min(num_birds + 1, 1000)
                generate_points_and_facultative_move(False)
                draw_points()
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
                draw()
            elif param == "random_speed":
                random_speed = min(random_speed + 1, 100) 
            elif param == "random_angle":
                random_angle = min(random_angle + 1, 360) 
            elif param == "points":
                points = not points
                draw()
            elif param == "refresh_ms":
                refresh_ms += 10
            elif param == "width":
                width = min(width + 1, 1500)
                generate_points_and_facultative_move(False)
                draw()
            elif param == "height":
                height = min(height + 1, 1000)
                generate_points_and_facultative_move(False)
                draw()
            elif param == "no_color":
                no_color = not no_color 
                if no_color:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "blue"
                    fill_color = "white"
                    outline_color = "black" 
                draw()    
        elif event.keysym == "Left":
            param = parameters[selected_index]
            if param == "num_birds":
                num_birds = max(num_birds - 1, 1)
                generate_points_and_facultative_move(False)
                draw_points()                
            elif param == "max_speed":
                max_speed = max(max_speed - 1, 1)
            elif param == "neighbor_radius":
                neighbor_radius = max(neighbor_radius - 1, 0)
            elif param == "sep_weight":
                sep_weight = max(sep_weight - 1, 0) 
            elif param == "align_weight":
                align_weight = max(align_weight - 1, 0) 
            elif param == "coh_weight":
                coh_weight = max(coh_weight - 1, 0) 
            elif param == "size":
                size = max(size - 1, 1)
                draw()
            elif param == "random_speed":
                random_speed = max(random_speed - 1, 0) 
            elif param == "random_angle":
                random_angle = max(random_angle - 1, 0) 
            elif param == "points":
                points = not points
                draw()
            elif param == "refresh_ms":
                refresh_ms = max(refresh_ms - 10, 10)
            elif param == "width":
                width = max(width - 1, 200)
                generate_points_and_facultative_move(False)
                draw()
            elif param == "height":
                height = max(height - 1, 200)
                generate_points_and_facultative_move(False)
                draw() 
            elif param == "no_color":
                no_color = not no_color 
                if no_color:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "blue"
                    fill_color = "white"
                    outline_color = "black" 
                draw()    
        elif event.char.lower() == 'r':
            restore_options()
            generate_points_and_facultative_move(False)
            draw()            
        elif event.char.lower() == 'n':
            global velocities
            global birds
            global paused
            pause= True
            velocities = []
            birds= [] 
            generate_points_and_facultative_move(False)
            draw()
        draw_status()

    def draw_canvas():
        global canvas_bg
        canvas.config(width=width + params, height=max(height,500), bg=canvas_bg)

    def draw_status():
        lines = [
            f"num_birds       : {num_birds}",
            f"neighbor_radius : {neighbor_radius}",
            f"sep_weight      : {sep_weight}",
            f"align_weight    : {align_weight}",
            f"coh_weight      : {coh_weight}",
            f"max_speed       : {max_speed}",
            f"random_speed    : {random_speed}",
            f"random_angle    : {random_angle}",
            f"refresh_ms      : {refresh_ms}",
            f"width           : {width}",
            f"height          : {height}",
            f"size            : {size}",
            f"points          : {points}",
            f"no_color        : {no_color}",            
            "",
            "[Up/Down]    Navigate between parameters",
            "[Left/Right] Adjust selected parameter",
            "[r]          Reset all parameters",
            "[Space]      Toggle pause / resume",
            "[r]          Reset all parameters",
            "             to their initial values",
            "[n]          New generation of birds",
            "[Enter]      Advance the simulation by ",
            "             one frame",
            "",
            f"----pybirdsreynolds {version_prog}----",
        ]

        x_text = 10
        y_text = 10
        canvas.delete("status")
        
        for i, line in enumerate(lines):
            fill = fill_color
            if i == selected_index:
                fill = "red"
                line += " <"
            canvas.create_text(
                x_text,
                y_text + i * 18,
                anchor="nw",
                fill=fill,
                font=("Consolas", 8),
                tags="status",
                text=line
            )

        if selected_index < len(param_order):
            param_name = param_order[selected_index]
            doc_text = param_docs.get(param_name, "")
            if doc_text:
                canvas.create_text(
                    x_text + 175,
                    y_text + selected_index * 18,
                    anchor="nw",
                    fill="yellow",
                    font=("Consolas", 8, "italic"),
                    tags="status",
                    text=doc_text,
                    width=200
                )



    def draw_rectangle():
        canvas.delete("boundary")
        canvas.create_rectangle(
            params, 0, params + width, height,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def generate_points_and_facultative_move(with_move):
        global velocities
        global new_velocities
        if not birds: 
            velocities = []
            for _ in range(num_birds):
                px = random.randint(margin + params, width - margin + params)
                py = random.randint(margin, height - margin)
                birds.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            # Supprimer les birds hors du rectangle
            inside_points = []
            inside_velocities = []
            for (x, y), (vx, vy) in zip(birds, velocities):
                if params + margin <= x <= params + width - margin and 0 + margin <= y <= height - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
                # Sinon on "kill" l'oiseau en ne le gardant pas

            birds[:] = inside_points
            velocities[:] = inside_velocities            
            # Calcul Reynolds
            new_velocities = []
            current_count = len(birds)
            
            # Ajouter aléatoirement des oiseaux
            if num_birds > current_count:
                for _ in range(num_birds - current_count):
                    px = random.randint(margin + params, width - margin + params)
                    py = random.randint(margin, height - margin)
                    birds.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, max_speed)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Supprimer aléatoirement des oiseaux
            elif num_birds < current_count:
                for _ in range(current_count - num_birds):
                    idx = random.randint(0, len(birds) - 1)
                    birds.pop(idx)
                    velocities.pop(idx)
            if with_move:                    
                move()
    def move():
        global velocities
        global new_velocities
        for i, (x, y) in enumerate(birds):
            move_sep_x, move_sep_y = 0, 0
            move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = 0, 0, 0, 0
            move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
            neighbors = 0

            for j, (x2, y2) in enumerate(birds):
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

            
            #ALEA
            speed = math.sqrt(vx**2 + vy**2)
            speed_factor = 1 + random.uniform(-random_speed / 100, random_speed / 100)
            new_speed = speed * speed_factor
            min_speed = 0.1 * max_speed
            if new_speed < min_speed:
                new_speed = min_speed
            if speed > 0:
                factor = new_speed / speed
                vx *= factor
                vy *= factor                
            angle = math.atan2(vy, vx)
            angle += math.radians(random.uniform(-1 * random_angle, random_angle))
            speed = math.sqrt(vx**2 + vy**2)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            vx, vy = limit_speed(vx, vy)
            
            new_velocities.append((vx, vy))

        velocities = new_velocities

        # Mise à jour des positions
        new_points = []
        for (x, y), (vx, vy) in zip(birds, velocities):
            nx = x + vx
            ny = y + vy

            # Rebonds 
            if nx < margin + params:
                nx = margin + (margin - nx) + params + params
                vx = -vx
            elif nx > width - margin + params:
                nx = (width - margin) - (nx - (width - margin)) + params + params
                vx = -vx
            if ny < margin:
                ny = margin + (margin - ny)
                vy = -vy
            elif ny > height - margin:
                ny = (height - margin) - (ny - (height - margin))
                vy = -vy
            idx = birds.index((x, y))
            velocities[idx] = (vx, vy)
            new_points.append((nx, ny))

        birds[:] = new_points


    def draw_points():
        for pid in point_ids:
            canvas.delete(pid)
        point_ids.clear()

        triangle_size = 6*size
        triangle_width = 4*size

        for (x, y), (vx, vy) in zip(birds, velocities):
            if points: 
                pid = canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=fill_color, outline=outline_color)
            else:
                angle = math.atan2(vy, vx)
                tip_x = x + math.cos(angle) * triangle_size
                tip_y = y + math.sin(angle) * triangle_size
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

    def update():
        if not paused:
            generate_points_and_facultative_move(True)
            draw()
        root.after(refresh_ms, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)

    root = tk.Tk()
    root.title("pybirdsreynolds")

    canvas = tk.Canvas(root, width=width+params, height=height, bg=canvas_bg)
    canvas.pack()

    birds = [] 
    point_ids = []

    generate_points_and_facultative_move(True)
    draw()

    root.bind("<Return>", on_next_frame)
    root.bind("<space>", toggle_pause)
    root.bind("<Key>", on_other_key)

    signal.signal(signal.SIGINT, signal_handler)
    update()
    root.mainloop()             


