from PIL import Image
import random

def save_rgb(rgb_data, width, height, filename):
    """Saves an a 3D list with RGB data as a png"""
    # Converting RGB list into something pillow can use to save an image.
    colors = bytes(rgb_data)
    img = Image.frombytes('RGB', (width, height), colors)
    img.save(f'{filename}.png')
    # Letting user know the image is saved.
    print(f'{filename}.png Saved')

def process_array(input_array, filename):
    """Processes 2D array to RGB data."""
    colors = []
    width = len(input_array[0])
    height = len(input_array)
    # Goes through 2D array and process it into RGB values.
    for Y in range(height):
        for X in range(width):
            if input_array[X][Y] > 255:
                input_array[X][Y] = 255
            elif input_array[X][Y] < 0:
                input_array[X][Y] = 0

            colors.extend([input_array[X][Y], input_array[X][Y], input_array[X][Y]])
    # Passing RGB values to save function
    save_rgb(colors, width, height, filename)

def Empty(width, height):
    MAP = []
    for Y in range(height):
        MAP.append([])
        for X in range(width):
            MAP[Y].append(0)
    return MAP

def valid_pos(room_tuple):
    global Width, Height, Map, Border
    if (Border >= room_tuple[0] - room_tuple[2] // 2) or (Width - Border <= room_tuple[0] + room_tuple[2] // 2) or (Border >= room_tuple[1] - room_tuple[3] // 2) or (Height - Border <= room_tuple[1] + room_tuple[3] // 2):
        return False
    else:
        return not intersection(room_tuple)

def intersection(room_tuple):
    '''Checks if two rectangles intersect. room_tuple = CenterX, CenterY, Width, Height'''
    global Room_List, Room_Border
    room_tuple_right = room_tuple[0] + room_tuple[2] // 2
    room_tuple_left = room_tuple[0] - room_tuple[2] // 2
    room_tuple_bottom = room_tuple[1] + room_tuple[3] // 2
    room_tuple_top = room_tuple[1] - room_tuple[3] // 2
    for room in Room_List:
        room_right = room[0] + room[2] // 2
        room_left = room[0] - room[2] // 2
        room_bottom = room[1] + room[3] // 2
        room_top = room[1] - room[3] // 2
        if (room_tuple_right+Room_Border > room_left-Room_Border and room_right+Room_Border > room_tuple_left-Room_Border) and (room_tuple_top-Room_Border < room_bottom+Room_Border and room_top-Room_Border < room_tuple_bottom+Room_Border):
            return True
    return False

Width = 100
Height = 100
Border = 3  # Border Surrounding the edge of the map
Map = Empty(Width, Height)
Room_List = []  #(CenterX, CenterY, Width, Height)
Failed_Attempts = 0
Failed_Rooms = 0
valid_room = False
# Room Properties
Num_Rooms = 15
Room_Border = 2  # Border Surrounding the edge of each room
Min_Room_X = 6
Max_Room_X = 30
Min_Room_Y = 6
Max_Room_Y = 30
# Generate Dungeon Rooms
for Room in range(Num_Rooms):
    # Gives up generating that room if it fails too many times.
    valid_room = False
    while not valid_room and Failed_Attempts <= 20:
        x = random.randint(5, Width - 5)
        y = random.randint(5, Width - 5)
        room_width = random.randint(Min_Room_X, Max_Room_X)
        room_height = random.randint(Min_Room_Y, Max_Room_Y)
        # Ensures room is within bounds and not intersecting a different room.
        if valid_pos((x, y, room_width, room_height)):
            Room_List.append((x, y, room_width, room_height))
            x_offset = x - room_width//2
            y_offset = y - room_height//2
            for Y in range(room_height):
                for X in range(room_width):
                    Map[X + x_offset][Y + y_offset] = 255
            valid_room = True
        else:
            Failed_Attempts += 1
    # Resets while loop and fail attempts.
    if Failed_Attempts == 21:
        Failed_Rooms += 1
        Failed_Attempts = 0
print(Failed_Rooms, "Rooms Failed to Generate")

# Generating Hallways
for i in range(len(Room_List)):
    room = Room_List[i]
    # Ensures the room points to the correct next room
    if i == len(Room_List)-1:
        next_room = Room_List[-1]
    else:
        next_room = Room_List[i+1]
    # Horizontal Hallway
    if room[0] < next_room[0]:
        Hallway_Length = next_room[0] - room[0]
        for X in range(Hallway_Length):
            Map[next_room[0] - X][room[1]] = 255
    else:
        Hallway_Length = room[0] - next_room[0]
        for X in range(Hallway_Length):
            Map[next_room[0] + X][room[1]] = 255
    # Vertical Hallway
    if room[1] < next_room[1]:
        Hallway_Length = next_room[1] - room[1]
        for Y in range(Hallway_Length):
            Map[next_room[0]][room[1] + Y] = 255
    else:
        Hallway_Length = room[1] - next_room[1]
        for Y in range(Hallway_Length):
            Map[next_room[0]][room[1] - Y] = 255

process_array(Map, "Dungeon Generator")