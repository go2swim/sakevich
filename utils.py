from constants import BOARD_LENGTH, SCREEN_HEIGHT, SCREEN_WIDTH, BOARD_OFFSET, TILE_LENGTH

#(левый верхний угол доски по x + координата по x * длина клетки, левый верхний угол доски по y + координата по y * длина клетки
coordinate_builder_to_absolute_coord = \
    lambda row, col: ((SCREEN_WIDTH-BOARD_LENGTH)/BOARD_OFFSET + col*TILE_LENGTH, (SCREEN_HEIGHT-BOARD_LENGTH)/2 + row*TILE_LENGTH)

coordinate_builder_to_tile_coord = \
    lambda x, y: (int((x - (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET) // TILE_LENGTH), int((y - (SCREEN_HEIGHT - BOARD_LENGTH) / 2) // TILE_LENGTH))