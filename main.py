import curses
from shape.generator import draw_donut, draw_box, vector_rotate
from numpy import array, pi, dot
import pickle
from datetime import datetime
import os

Running = True
rows, cols = 40, 80
scale = ".,-~:;=!*#$@"
UP_KEY, DOWN_KEY, RIGHT_KEY = 259, 258, 261
axis_x, axis_y, axis_z = (array([1,0,0]), array([0,1,0]), array([0,0,1]))
init_r = array([cols/2,0,cols/2])
light = array([0,-1,1])

def get_center_pos(title, width, height):
    x = width//2 - (len(title)//2)
    y = height//2
    return int(x), int(y)

def menu(terminal):
    global Running
    option_index = 0
    k = 0
    selected = False
    
    while True: 
        terminal.clear()
        curses.resize_term(rows, cols) 

        ltitle = "3D ASCII VIEWER"
        terminal.addstr(0, 1, ltitle, curses.A_BOLD)

        rtitle = "by Minh Pham Dinh"
        terminal.addstr(0, cols - len(rtitle) - 1, rtitle, curses.A_BOLD)

        # options
        option1 = "render new donut animation"[:cols - 1]
        option2 = "render new box animation"[:cols - 1]
        option3 = "run save files"[:cols - 1]
        option4 = "exit program"[:cols - 1]

        options = [option1, option2, option3, option4]      

        if k == UP_KEY:
            if option_index > 0:
                option_index -= 1
        elif k == DOWN_KEY:
            if option_index < len(options) - 1:
                option_index += 1
        elif k == RIGHT_KEY:
            selected = True

        if selected:
            if option_index == 0:
                return render_wizard(terminal, "donut")
            if option_index == 1:
                return render_wizard(terminal, "box")
            if option_index == 2:
                return select_save_file(terminal)
            if option_index == 3:
                selected = False
                Running = False
                return  

        for i in range(len(options)):
            if i == option_index:
                terminal.attron(curses.A_STANDOUT)
                terminal.attron(curses.color_pair(1))
            terminal.addstr(i+2, 1, options[i])
            terminal.attroff(curses.A_STANDOUT)
            terminal.attroff(curses.color_pair(1))

        k = terminal.getch()

def select_save_file(terminal):
    global Running
    option_index = 0
    k = 0
    selected = False

    while True:
        terminal.clear()
        curses.resize_term(rows, cols) 
        
        # options
        options = os.listdir("save-files/")

        if k == UP_KEY:
            if option_index > 0:
                option_index -= 1
        elif k == DOWN_KEY:
            if option_index < len(options)-1:
                option_index += 1
        elif k == RIGHT_KEY:
            selected = True
        elif k == ord('q'):
            return

        if selected:
            return run_saved(terminal, f"save-files/{options[option_index]}")

        cwd = f"{os.getcwd()}\\save-files"
        terminal.addstr(0,1, cwd)
        title = "SAVE FILES"
        terminal.addstr(0, cols - len(title) - 1, title, curses.A_BOLD)

        for i in range(len(options)):
            if i == option_index:
                terminal.attron(curses.A_STANDOUT)
                terminal.attron(curses.color_pair(1))
            terminal.addstr(i+2, 1, options[i])
            terminal.attroff(curses.A_STANDOUT)
            terminal.attroff(curses.color_pair(1))
        k = terminal.getch()

def render_wizard(terminal, type):
    k = 0
    if type == "donut":
        labels = ["file name: ", "Inner radius: ", "Crust radius: ", "Number of samples between 0 and 2pi: ", "rate of rotation around x axis: ", "rate of rotation around y axis: ", "rate of rotation around z axis: ", "Number of frames: "]
    elif type == "box":
        labels = ["file name: ", "Width: ", "Height: ", "Length: ", "rate of rotation around x axis: ", "rate of rotation around y axis: ", "rate of rotation around z axis: ", "Number of frames: "]
    fields = [f'{type}-{datetime.today().strftime("%Y%m%dT%H%M%S%z")}'] + ["__________"]*(len(labels) - 1) + ["", "RENDER", "BACK TO MENU"]
    option_index = 0
    selected = False
    while True:
        terminal.clear()
        curses.resize_term(rows, cols)

        title = f'{type.upper()} RENDERING WIZARD'
        terminal.addstr(0, cols - len(title) - 1, title)
        fields_x = 0
        for i, label in enumerate(labels):
            terminal.addstr(i+2, 1, label)
            if len(label) > fields_x:
                fields_x = len(label) + 1
        
        if k == UP_KEY:
            if option_index > 0:
                option_index -= 1
        elif k == DOWN_KEY:
            if option_index < len(fields) - 1:
                option_index += 1
        elif k == RIGHT_KEY:
            selected = True
        
        for i in range(len(fields)):
            if i == option_index:
                terminal.attron(curses.A_STANDOUT)
                terminal.attron(curses.color_pair(1))
            terminal.addstr(i+2, fields_x, fields[i])
            terminal.attroff(curses.A_STANDOUT)
            terminal.attroff(curses.color_pair(1))
        terminal.move(option_index+2, fields_x)

        if selected:
            selected = False
            if option_index < len(labels):
                curses.echo()
                curses.curs_set(2)
                for i in range(len(fields[option_index])):
                    terminal.delch(option_index+2,fields_x)
                terminal.move(option_index+2, fields_x)
                string = ""
                k = terminal.getch()
                while k != RIGHT_KEY:
                    y, x = terminal.getyx()
                    if k == 8:
                        terminal.delch(y,x)
                        string = string[:len(string)-1]
                    if (k<48 or k>57) and option_index != 0:
                        terminal.delch(y,x-1)
                    else:
                        string += chr(k)
                    k = terminal.getch()
                curses.curs_set(1)
                curses.noecho()
                terminal.delch(y, x)
                if string != "":
                    fields[option_index] = string
            elif fields[option_index] == "RENDER":
                if "__________" not in fields:
                    return render(terminal, type, fields[:len(fields)-3])
            elif fields[option_index] == "BACK TO MENU":
                return menu(terminal)
        k = terminal.getch()
        terminal.refresh()
        terminal.move(0,0)

def render(terminal, type, fields):
    k = 0
    selected = False
    if type == "donut":
        dic, dalpha, dbeta, dtheta, t, filename = draw_donut(init_r, fields)
    if type == "box":
        dic, dalpha, dbeta, dtheta, t, filename = draw_box(init_r, fields)
    frames = [t, [], [], int(fields[len(fields)-1])]
    frame_num = 0
    
    terminal.clear()
    terminal.refresh()
    while frame_num < frames[0]:
        curses.resize_term(rows, cols)
        terminal.clear()
        
        for key in dic.keys():
            r = dic[key]["coord"]- init_r
            n = dic[key]["n"]
            if dalpha != 0:
                r = vector_rotate(r, dalpha, axis_x)
                n = vector_rotate(n, dalpha, axis_x)
            if dbeta != 0:
                r = vector_rotate(r, dtheta, axis_y)
                n = vector_rotate(n, dtheta, axis_y)
            if dtheta != 0:
                r = vector_rotate(r, dtheta, axis_z)
                n = vector_rotate(n, dtheta, axis_z)
            r = r + init_r
            dic[key] = {"coord": r,"n": n, "L": dot(n, light)}
        
        values_arr = dic.values()
        Ls = [item['L'] for item in values_arr]
        maxmin_illu = [min(Ls), max(Ls)]
        frames[2].append(maxmin_illu)
        coords = array([item['coord'] for item in values_arr])
        y_index = {i: {i: [float("-inf"),0] for i in range(cols)} for i in range(rows)}
        for idx, coord in enumerate(coords): 
            x, y, z = coord
            L = Ls[idx]
            if y > y_index[round(z * rows/cols)][round(x)][0]:
                y_index[round(z * rows/cols)][round(x)] = [y, L]

        min_illu, max_illu = maxmin_illu        
        for row in range(rows):
            for col in range(cols):
                if y_index[row][col] != [float("-inf"),0]:
                    L = y_index[row][col][1]
                    scale_index = (L - min_illu) * 11/(max_illu - min_illu)
                    string = scale[round(scale_index)]
                    terminal.addstr(row, col, string)

        frames[1].append(y_index)
        string = str(round(frame_num/frames[0] * 100)) + "%"
        terminal.addstr(rows-1,1,string)
        terminal.refresh()
        terminal.move(0,0)
        frame_num += 1

    option = 0
    terminal.nodelay(False)
    filename = "save-files/" + filename
    outfile = open(filename, 'wb')
    pickle.dump(frames, outfile)
    outfile.close()

    while True:
        curses.resize_term(rows, cols)
        terminal.clear()
        
        
        if k == UP_KEY:
            if option > 0:
                    option -= 1
        elif k == DOWN_KEY:
            if option < 1:
                option += 1
        elif k == RIGHT_KEY:
            selected = True

        if selected:
            if option == 0:
                return run_saved(terminal, filename)
            if option == 1:
                selected = False
                return 

        title = "Animation is rendered and saved in save file folder"[:cols-1]
        option1 = "play animation"[:cols-1]
        option2 = "return to menu"[:cols-1]
        options = [option1, option2]

        x, y = get_center_pos(title, cols, rows) 
        terminal.addstr(y-1, x, title)
        
        terminal.attron(curses.A_STANDOUT)
        terminal.attron(curses.color_pair(1))
        x, y = get_center_pos(options[option], cols, rows)
        terminal.addstr(y+option, x, options[option])
        terminal.attroff(curses.A_STANDOUT)
        terminal.attroff(curses.color_pair(1))

        x, y = get_center_pos(options[len(options)-1-option], cols, rows)
        terminal.addstr(y+len(options)-1-option, x, options[len(options)-1-option])
        k = terminal.getch()
        terminal.refresh()
        terminal.move(0,0)

def run_saved(terminal, filename):
    file = open(filename, "rb")
    frames = pickle.load(file, encoding='bytes')
    file.close()
    terminal.clear()
    terminal.refresh()
    
    k = 0
    i = 0
    dt = 15
    terminal.nodelay(True)
    while True:
        if k == ord('q'):
            return
        elif k == UP_KEY:
            dt += 5
        elif k == DOWN_KEY and dt - 5 >= 0:
            dt -= 5    
        frame = frames[1][i]
        terminal.clear()
        curses.resize_term(rows, cols)
        
        scale = ".,-~:;=!*#$@"
        min_illu, max_illu = frames[2][i]
        title = "press 'q' to return to menu"
        x, y = get_center_pos(title, cols, rows)
        terminal.addstr(rows - 3, x, title)
        spf = f"milliseconds between frames: {dt}"
        terminal.addstr(0,0,spf)
        for row in range(rows):
            for col in range(cols):
                if frame[row][col] != [float("-inf"),0]:
                    L = frame[row][col][1]
                    scale_index = (L - min_illu) * 11/(max_illu - min_illu)
                    str = scale[round(scale_index)]
                    terminal.addstr(row, col, str)
        if i == len(frames[1]) - 1:
            i = 0
        i += 1

        k = terminal.getch()
        terminal.timeout(dt)
        terminal.move(0,0)
        terminal.refresh()

def draw(terminal):
    global Running
    terminal.clear()
    terminal.refresh()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    while Running:
       menu(terminal)

if __name__ == "__main__":
    curses.wrapper(draw)
