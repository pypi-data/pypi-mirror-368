
"""
PySick collision checking utilities.
"""


def rectxrect(one_rect, another_rect):
    """
    Check if two rectangles collide.

    Parameters:
        one_rect (graphics.Rect)
        another_rect (graphics.Rect)

    Returns:
        bool
    """
    return (
        one_rect.x < another_rect.x + another_rect.width and
        one_rect.x + one_rect.width > another_rect.x and
        one_rect.y < another_rect.y + another_rect.height and
        one_rect.y + one_rect.height > another_rect.y
    )


def circlexcircle(one_circle, another_circle):
    """
    Check if two circles collide.

    Parameters:
        one_circle (graphics.Circle)
        another_circle (graphics.Circle)

    Returns:
        bool
    """
    dx = another_circle.x - one_circle.x
    dy = another_circle.y - one_circle.y
    distance_squared = dx * dx + dy * dy
    radius_sum = one_circle.radius + another_circle.radius

    return distance_squared < radius_sum * radius_sum



def rectxcircle(rect, circle):
    """
    Check if a rectangle and a circle collide.

    Parameters:
        rect (graphics.Rect)
        circle (graphics.Circle)

    Returns:
        bool
    """
    # Find the closest point on the rect to the circle center
    closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
    closest_y = max(rect.y, min(circle.y, rect.y + rect.height))

    dx = circle.x - closest_x
    dy = circle.y - closest_y

    return (dx * dx + dy * dy) < (circle.radius * circle.radius)