class Color:
    pass


def isInrectangle(pos, pos0, width, height):
    """
    Returns True if the point defined by the position is in the rectangle
    :param pos:
    :param pos0: top left point of the rectangle
    :param width:
    :param height:
    :return:bool
    """
    return pos0[0] <= pos[0] <= pos0[0] + width and pos0[1] <= pos[1] <= pos0[1] + height


def isInbounds(i, j):
    return 0 <= i <= 7 and 0 <= j <= 7


def other_color(color: Color):
    from pieces import Color
    return Color.WHITE if color == Color.BLACK else Color.BLACK
