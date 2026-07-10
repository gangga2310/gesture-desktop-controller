import cv2


def draw_point(frame, x, y, color=(0, 255, 0), radius=5):
    """
    Menggambar satu titik landmark.
    """
    cv2.circle(
        frame,
        (x, y),
        radius,
        color,
        -1
    )


def draw_label(frame, text, x, y,
               color=(255, 0, 0),
               scale=0.5,
               thickness=1):
    """
    Menggambar label di dekat landmark.
    """

    cv2.putText(
        frame,
        str(text),
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness
    )


def draw_line(frame, start, end,
              color=(255, 255, 255),
              thickness=2):
    """
    Menggambar garis.
    """

    cv2.line(
        frame,
        start,
        end,
        color,
        thickness
    )