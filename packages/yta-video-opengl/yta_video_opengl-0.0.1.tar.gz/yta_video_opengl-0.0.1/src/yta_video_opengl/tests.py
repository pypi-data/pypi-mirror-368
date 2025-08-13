"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
import av
import glfw
import moderngl
import numpy as np
from PIL import Image
import time


def video_modified_displayed_on_window():
    # -------- CONFIG --------
    VIDEO_PATH = "test_files/test_1.mp4"  # Cambia por tu vídeo
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0
    # ------------------------

    # Inicializar ventana GLFW
    if not glfw.init():
        raise RuntimeError("No se pudo inicializar GLFW")

    window = glfw.create_window(1280, 720, "Wave Shader Python", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("No se pudo crear ventana GLFW")

    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    # Shader GLSL
    prog = ctx.program(
        vertex_shader='''
        #version 330
        in vec2 in_pos;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            v_uv = in_uv;
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        ''',
        fragment_shader='''
        #version 330
        uniform sampler2D tex;
        uniform float time;
        uniform float amp;
        uniform float freq;
        uniform float speed;
        in vec2 v_uv;
        out vec4 f_color;
        void main() {
            float wave = sin(v_uv.x * freq + time * speed) * amp;
            vec2 uv = vec2(v_uv.x, v_uv.y + wave);
            f_color = texture(tex, uv);
        }
        '''
    )

    # Cuadrado a pantalla completa
    vertices = np.array([
        -1, -1, 0.0, 0.0,
        1, -1, 1.0, 0.0,
        -1,  1, 0.0, 1.0,
        1,  1, 1.0, 1.0,
    ], dtype='f4')

    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_pos', 'in_uv')

    # Abrir vídeo con PyAV
    container = av.open(VIDEO_PATH)
    stream = container.streams.video[0]
    stream.thread_type = "AUTO"

    # Decodificar primer frame para crear textura
    first_frame = next(container.decode(stream))
    img = first_frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    tex = ctx.texture(img.size, 3, img.tobytes())
    tex.build_mipmaps()

    # Uniforms fijos
    prog['amp'].value = AMP
    prog['freq'].value = FREQ
    prog['speed'].value = SPEED

    start_time = time.time()

    # Render loop
    frame_iter = container.decode(stream)
    for frame in frame_iter:
        if glfw.window_should_close(window):
            break

        # Tiempo
        t = time.time() - start_time
        prog['time'].value = t

        # Convertir frame a textura
        img = frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        tex.write(img.tobytes())

        # Dibujar
        ctx.clear(0.1, 0.1, 0.1)
        tex.use()
        vao.render(moderngl.TRIANGLE_STRIP)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

def video_modified_stored():
    VIDEO_PATH = "test_files/test_1.mp4"
    OUTPUT_PATH = "test_files/output.mp4"
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0

    # Crear contexto ModernGL sin ventana
    ctx = moderngl.create_standalone_context()

    # Shader de onda
    prog = ctx.program(
        vertex_shader='''
        #version 330
        in vec2 in_pos;
        in vec2 in_uv;
        out vec2 v_uv;
        void main() {
            v_uv = in_uv;
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        ''',
        fragment_shader='''
        #version 330
        uniform sampler2D tex;
        uniform float time;
        uniform float amp;
        uniform float freq;
        uniform float speed;
        in vec2 v_uv;
        out vec4 f_color;
        void main() {
            float wave = sin(v_uv.x * freq + time * speed) * amp;
            vec2 uv = vec2(v_uv.x, v_uv.y + wave);
            f_color = texture(tex, uv);
        }
        '''
    )

    # Quad
    vertices = np.array([
        -1, -1, 0.0, 0.0,
        1, -1, 1.0, 0.0,
        -1,  1, 0.0, 1.0,
        1,  1, 1.0, 1.0,
    ], dtype='f4')
    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_pos', 'in_uv')

    # Abrir vídeo de entrada
    container = av.open(VIDEO_PATH)
    stream = container.streams.video[0]
    fps = stream.average_rate
    width = stream.width
    height = stream.height

    # Framebuffer para renderizar
    fbo = ctx.simple_framebuffer((width, height))
    fbo.use()

    # Decodificar primer frame y crear textura
    first_frame = next(container.decode(stream))
    img = first_frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    tex = ctx.texture(img.size, 3, img.tobytes())
    tex.build_mipmaps()

    # Uniforms
    prog['amp'].value = AMP
    prog['freq'].value = FREQ
    prog['speed'].value = SPEED

    # Abrir salida con PyAV (codificador H.264)
    output = av.open(OUTPUT_PATH, mode='w')
    out_stream = output.add_stream("libx264", rate=fps)
    out_stream.width = width
    out_stream.height = height
    out_stream.pix_fmt = "yuv420p"

    start_time = time.time()

    for frame in container.decode(stream):
        t = time.time() - start_time
        prog['time'].value = t

        # Subir frame a textura
        img = frame.to_image().transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
        tex.write(img.tobytes())

        # Renderizar con shader al framebuffer
        fbo.clear(0.0, 0.0, 0.0)
        tex.use()
        vao.render(moderngl.TRIANGLE_STRIP)

        # Leer píxeles del framebuffer
        data = fbo.read(components=3, alignment=1)
        img_out = Image.frombytes("RGB", (width, height), data).transpose(Image.FLIP_TOP_BOTTOM)

        # Convertir a frame de PyAV y escribir
        video_frame = av.VideoFrame.from_image(img_out)
        packet = out_stream.encode(video_frame)
        if packet:
            output.mux(packet)

    # Vaciar buffers de codificación
    packet = out_stream.encode(None)
    if packet:
        output.mux(packet)

    output.close()
    print(f"Vídeo guardado en {OUTPUT_PATH}")
