from pictex import Canvas, Row, Column, Text, Image, Shadow

# ----------------------------------------------------
# 1. Datos de Entrada (Simulando un Producto)
# ----------------------------------------------------
LOGO_PATH = "logo.jpg"  # The user needs a square logo image (e.g., 60x60)
PRODUCT_NAME = "PicTex v1.1"
TAGLINE = "Create beautiful graphics with a component-based API."
UPVOTE_COUNT = 248

# ----------------------------------------------------
# 2. Construcción de los Componentes
# ----------------------------------------------------

# -- La sección de información del producto (lado izquierdo) --
product_logo = Image(LOGO_PATH).size(60, 60).border_radius(8)

product_text = Column(
    Text(PRODUCT_NAME).font_size(20).font_weight(700),
    Text(TAGLINE).font_size(15).color("#536471").line_height(1.3)
).gap(4)

# We combine the logo and text in a Row.
# This entire Row will define the height for the stretch.
product_info = Row(
    product_logo,
    product_text
).gap(15).vertical_align('center')


# -- El botón de Upvote (lado derecho) --
# We build this inside a Column so it can be stretched vertically.
upvote_button = (
    Column(
        Text("▲").font_size(14),
        Text(str(UPVOTE_COUNT)).font_size(18).font_weight(700)
    )
    .horizontal_align('center')   # Center the triangle and number horizontally
    .vertical_distribution('center') # Center them vertically within the button
    .padding(10, 20, 10, 20)
    .border(1, "#CFD9DE")
    .border_radius(8)
    .gap(4)
)


# ----------------------------------------------------
# 3. Ensamblaje Final con `stretch` y Renderizado
# ----------------------------------------------------

# Assemble the final card in a Row.
# The .vertical_align('stretch') is the star of the show here.
card = (
    Row(
        product_info,
        upvote_button
    )
    .size(width=500) # Give the card a fixed width
    .vertical_align('stretch') # <-- THE HERO FEATURE!
    .background_color("white")
    .padding(20)
    .border_radius(12)
    .border(1, "#CFD9DE")
    .box_shadows(Shadow(offset=(0, 6), blur_radius=18, color="#14171A20")) # A soft shadow
)


# Set up the Canvas to provide a nice background.
canvas = (
    Canvas()
    .font_family("Arial")
    .background_color("#F5F8FA") # A very light gray
    .padding(50)
)

# Render and show the final image.
canvas.render(card).show()