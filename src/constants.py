#logic constants

DEFAULT_SELECTED_OBJECT = "Point"
POSSIBLE_OBJECTS = ["Point", "Line", "Wireframe", "Curve", "3DObject"]
AVAILABLE_CURVES = ["Bezier", "B-Spline"]
AVAILABLE_SURFACES = ["BezierSurface"]

CURVE_TYPE_BEZIER = "Bezier"
CURVE_TYPE_BSPLINE = "B-Spline"

WINDOW_BOUNDS = [(0, 0), (1920, 1080)]
WINDOW_TO_VIEWPORT_RATIO = 0.95

VIEW_UP_VECTOR = (0, 1, 0)
VIEW_PLANE_NORMAL = (0, 0, 1)
VIEW_REFERENCE_POINT = [0, 0, 0]

PARALLEL_PROJECTION = "parallel"
PERSPECTIVE_PROJECTION = "perspective"

# ui constants

UI_BACKGROUND_COLOR = "#848a88"

APPLICATION_SIZE = "1600x900"

APPLICATION_WIDTH = 1600
APPLICATION_HEIGHT = 900

VIEWPORT_BG_COLOR = "#3f2a78"

VIEWPORT_WIDTH = 1034
VIEWPORT_HEIGHT = 582

DEFAULT_OBJECT_COLOR = "black"

POPUP_WIDTH = 640
POPUP_HEIGHT = 360
POPUP_Y_OFFSET = 50 #o quão para cima a janela popup deve ser criada em relação ao centro da janela principal


# paths

ROTATE_ICON_PATH = "assets/rotate.png"