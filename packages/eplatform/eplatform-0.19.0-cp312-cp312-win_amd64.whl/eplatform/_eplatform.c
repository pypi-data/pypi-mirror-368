
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <SDL3/SDL.h>

#include "emath.h"

#define CHECK_UNEXPECTED_ARG_COUNT_ERROR(expected_count)\
    if (expected_count != nargs)\
    {\
        PyErr_Format(PyExc_TypeError, "expected %zi args, got %zi", expected_count, nargs);\
        goto error;\
    }

#define CHECK_UNEXPECTED_PYTHON_ERROR()\
    if (PyErr_Occurred())\
    {\
        goto error;\
    }

#define RAISE_SDL_ERROR()\
    {\
        PyObject *cause = PyErr_GetRaisedException();\
        PyErr_Format(\
            PyExc_RuntimeError,\
            "sdl error: %s\nfile: %s\nfunction: %s\nline: %i",\
            SDL_GetError(),\
            __FILE__,\
            __func__,\
            __LINE__\
        );\
        if (cause)\
        {\
            PyObject *ex = PyErr_GetRaisedException();\
            PyErr_SetRaisedException(ex);\
            PyException_SetCause(ex, cause);\
            if (cause){ Py_DECREF(cause); cause = 0; }\
        }\
        goto error;\
    }

static const int SUB_SYSTEMS = SDL_INIT_VIDEO | SDL_INIT_JOYSTICK | SDL_INIT_GAMEPAD;

static double
normalize_sdl_joystick_axis_value_(Sint16 value)
{
    double f_value = (
        ((double)value - SDL_JOYSTICK_AXIS_MIN) /
        ((double)SDL_JOYSTICK_AXIS_MAX - SDL_JOYSTICK_AXIS_MIN)
    );
    f_value = (f_value * 2) - 1;
    if (f_value < -1.0){ f_value = -1.0; }
    else if (f_value > 1.0){ f_value = 1.0; }
    return f_value;
}

typedef struct ModuleState
{
    int dummy;
} ModuleState;

static PyObject *
reset_module_state(PyObject *module, PyObject *unused)
{
    ModuleState *state = (ModuleState *)PyModule_GetState(module);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    if (!state){ Py_RETURN_NONE; }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
initialize_sdl(PyObject *module, PyObject *unused)
{
    if (!SDL_InitSubSystem(SUB_SYSTEMS)){ RAISE_SDL_ERROR(); }
    SDL_SetHint("SDL_HINT_IME_SHOW_UI", "1");
    SDL_SetHint("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1");
    SDL_SetJoystickEventsEnabled(true);
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
deinitialize_sdl(PyObject *module, PyObject *unused)
{
    SDL_QuitSubSystem(SUB_SYSTEMS);
    SDL_Quit();
    Py_RETURN_NONE;
}

static PyObject *
create_sdl_window(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    SDL_Window *sdl_window = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    int open_gl_major_version = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    int open_gl_minor_version = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE))
    {
        RAISE_SDL_ERROR();
    }
    if (!SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 1))
    {
        RAISE_SDL_ERROR();
    }
    if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, open_gl_major_version))
    {
        RAISE_SDL_ERROR();
    }
    if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, open_gl_minor_version))
    {
        RAISE_SDL_ERROR();
    }

    sdl_window = SDL_CreateWindow("", 200, 200, SDL_WINDOW_HIDDEN | SDL_WINDOW_OPENGL);
    if (!sdl_window){ RAISE_SDL_ERROR(); }
    if (!SDL_StopTextInput(sdl_window)){ RAISE_SDL_ERROR(); }
    int x;
    int y;
    if (!SDL_GetWindowPosition(sdl_window, &x, &y)){ RAISE_SDL_ERROR(); }

    PyObject *py_sdl_window = PyCapsule_New(sdl_window, "_eplatform.SDL_Window", 0);
    if (!py_sdl_window){ goto error; }
    return Py_BuildValue("(Oii)", py_sdl_window, x, y);
error:
    if (sdl_window){ SDL_DestroyWindow(sdl_window); }
    return 0;
}

static PyObject *
delete_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    SDL_DestroyWindow(sdl_window);
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
show_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_ShowWindow(sdl_window)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
hide_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_HideWindow(sdl_window)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_size(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *size = emath_api->IVector2_GetValuePointer(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    EMathApi_Release();
    emath_api = 0;

    if (!SDL_SetWindowSize(sdl_window, size[0], size[1])){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
set_sdl_window_position(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *position = emath_api->IVector2_GetValuePointer(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    EMathApi_Release();
    emath_api = 0;

    if (!SDL_SetWindowPosition(sdl_window, position[0], position[1])){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
set_sdl_window_title(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    const char *title = PyUnicode_AsUTF8AndSize(args[1], 0);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    if (!SDL_SetWindowTitle(sdl_window, title)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
center_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_SetWindowPosition(sdl_window, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED))
    {
        RAISE_SDL_ERROR();
    }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
swap_sdl_window(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    long sync = PyLong_AsLong(args[1]);
    if (sync == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    while(true)
    {
        if (SDL_GL_SetSwapInterval(sync)){ break; }
        // not all systems support adaptive vsync, so try regular vsync
        // instead
        if (sync == -1) // adaptive
        {
            sync = 1;
        }
        else
        {
            // not all systems are double buffered, so setting any swap
            // interval will result in an error
            // we don't actually need to swap the window in this case
            Py_RETURN_NONE;
        }
    }

    SDL_GL_SwapWindow(sdl_window);

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
enable_sdl_window_text_input(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(6);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    SDL_Rect rect;
    rect.x = PyLong_AsLong(args[1]);
    if (rect.x == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.y = PyLong_AsLong(args[2]);
    if (rect.y == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.w = PyLong_AsLong(args[3]);
    if (rect.w == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.h = PyLong_AsLong(args[4]);
    if (rect.h == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    int cursor = PyLong_AsLong(args[5]);
    if (cursor == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    if (!SDL_SetTextInputArea(sdl_window, &rect, cursor)){ RAISE_SDL_ERROR(); }
    if (!SDL_StartTextInput(sdl_window)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
disable_sdl_window_text_input(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_StopTextInput(sdl_window)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_border(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_SetWindowBordered(sdl_window, args[1] == Py_True)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_resizeable(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_SetWindowResizable(sdl_window, args[1] == Py_True)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_always_on_top(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_SetWindowAlwaysOnTop(sdl_window, args[1] == Py_True)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_fullscreen(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(5);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    SDL_DisplayID sdl_display = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    int w = PyLong_AsLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    int h = PyLong_AsLong(args[3]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    double refresh_rate = PyFloat_AsDouble(args[4]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    int count;
    SDL_DisplayMode *display_mode = 0;
    SDL_DisplayMode **display_modes = SDL_GetFullscreenDisplayModes(sdl_display, &count);
    if (!display_modes){ RAISE_SDL_ERROR(); }
    for (int i = 0; i < count; i++)
    {
        display_mode = display_modes[i];
        if (
            display_mode->w == w &&
            display_mode->h == h &&
            (int)display_mode->refresh_rate == (int)refresh_rate
        )
        {
            break;
        }
        display_mode = 0;
    }
    if (display_mode == 0)
    {
        PyErr_Format(PyExc_ValueError, "display does not support the requested mode");
        goto error;
    }

    if (!SDL_SetWindowFullscreenMode(sdl_window, display_mode)){ RAISE_SDL_ERROR(); }
    if (!SDL_SetWindowFullscreen(sdl_window, true)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_not_fullscreen(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_SetWindowFullscreen(sdl_window, false)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}


static PyObject *
set_sdl_window_icon(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;
    SDL_Surface *icon = 0;

    if (nargs < 2)
    {
        PyErr_Format(PyExc_TypeError, "expected at least 2 args, got %zi", nargs);
        goto error;
    }

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    for (int i = 0; i < nargs - 1; i++)
    {
        PyObject *py_icon = args[i + 1];
        PyObject *py_pixels = PyObject_GetAttrString(py_icon, "pixels");
        CHECK_UNEXPECTED_PYTHON_ERROR();
        const uint8_t *pixels = emath_api->U8Vector4Array_GetValuePointer(py_pixels);
        CHECK_UNEXPECTED_PYTHON_ERROR();

        PyObject *py_size = PyObject_GetAttrString(py_icon, "size");
        CHECK_UNEXPECTED_PYTHON_ERROR();
        const int *size = emath_api->IVector2_GetValuePointer(py_size);
        CHECK_UNEXPECTED_PYTHON_ERROR();

        SDL_Surface *i_icon = SDL_CreateSurfaceFrom(size[0], size[1], SDL_PIXELFORMAT_RGBA32, (void *)pixels, size[0] * 4);
        if (!i_icon){ RAISE_SDL_ERROR(); }

        if (i == 0)
        {
            icon = i_icon;
        }
        else
        {
            bool success = SDL_AddSurfaceAlternateImage(icon, i_icon);
            SDL_DestroySurface(i_icon);
            if (!success){ RAISE_SDL_ERROR(); }
        }
    }

    EMathApi_Release();
    emath_api = 0;

    if (!SDL_SetWindowIcon(sdl_window, icon)){ RAISE_SDL_ERROR(); }

    SDL_DestroySurface(icon);

    Py_RETURN_NONE;
error:
    if (icon){ SDL_DestroySurface(icon); }
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
maximize_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (SDL_GetWindowFlags(sdl_window) & SDL_WINDOW_RESIZABLE)
    {
        if (!SDL_MaximizeWindow(sdl_window)){ RAISE_SDL_ERROR(); }
    }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
create_sdl_gl_context(PyObject *module, PyObject *py_sdl_window)
{
    SDL_GLContext sdl_gl_context = 0;

    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    sdl_gl_context = SDL_GL_CreateContext(sdl_window);
    if (!sdl_gl_context)
    {
        PyErr_Format(PyExc_RuntimeError, "unable to create open gl context");
        SDL_ClearError();
        goto error;
    }

    PyObject *py_sdl_gl_context = PyCapsule_New(sdl_gl_context, "_eplatform.SDL_GLContext", 0);
    if (!py_sdl_gl_context){ goto error; }
    return py_sdl_gl_context;
error:
    if (sdl_gl_context)
    {
        if (!SDL_GL_DestroyContext(sdl_gl_context))
        {
            RAISE_SDL_ERROR();
        }
    }
    return 0;
}

static PyObject *
delete_sdl_gl_context(PyObject *module, PyObject *py_sdl_gl_context)
{
    SDL_GLContext sdl_gl_context = PyCapsule_GetPointer(
        py_sdl_gl_context,
        "_eplatform.SDL_GLContext"
    );
    if (!sdl_gl_context){ goto error; }
    if (!SDL_GL_DestroyContext(sdl_gl_context)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_gl_attrs(PyObject *module, PyObject *unused)
{
    int red = 0;
    int green = 0;
    int blue = 0;
    int alpha = 0;
    int depth = 0;
    int stencil = 0;

    if (!SDL_GL_GetAttribute(SDL_GL_RED_SIZE, &red)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_GREEN_SIZE, &green)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_BLUE_SIZE, &blue)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_ALPHA_SIZE, &alpha)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_DEPTH_SIZE, &depth)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE, &stencil)){ RAISE_SDL_ERROR(); }

    return Py_BuildValue("(iiiiii)", red, green, blue, alpha, depth, stencil);
error:
    return 0;
}

static PyObject *
set_clipboard(PyObject *module, PyObject *py_str)
{
    Py_ssize_t str_size;
    const char *str = PyUnicode_AsUTF8AndSize(py_str, &str_size);
    if (!str){ goto error; }
    if (!SDL_SetClipboardText(str)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_clipboard(PyObject *module, PyObject *unused)
{
    char *str = SDL_GetClipboardText();
    if (!str)
    {
        SDL_free(str);
        if (SDL_HasClipboardText())
        {
            RAISE_SDL_ERROR();
        }
        return PyUnicode_FromString("");
    }
    PyObject *py_str = PyUnicode_FromString(str);
    SDL_free(str);
    return py_str;
error:
    return 0;
}

static PyObject *
clear_sdl_events(PyObject *module, PyObject *unused)
{
    SDL_PumpEvents();
    SDL_FlushEvents(SDL_EVENT_FIRST, SDL_EVENT_LAST);
    Py_RETURN_NONE;
}

static PyObject *
push_sdl_event(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    if (nargs == 0)
    {
        PyErr_Format(PyExc_TypeError, "expected at least 1 arg, got %zi",  nargs);
        goto error;
    }

    SDL_Event event;
    event.type = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    switch(event.type)
    {
        case SDL_EVENT_MOUSE_MOTION:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(5);
            event.motion.x = (float)PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.y = (float)PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.xrel = (float)PyLong_AsLong(args[3]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.yrel = (float)PyLong_AsLong(args[4]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_MOUSE_WHEEL:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(4);
            event.wheel.direction = SDL_MOUSEWHEEL_NORMAL;
            if (args[1] == Py_True)
            {
                event.wheel.direction = SDL_MOUSEWHEEL_FLIPPED;
            }
            event.wheel.x = (float)PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.wheel.y = (float)PyLong_AsLong(args[3]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_MOUSE_BUTTON_DOWN:
        case SDL_EVENT_MOUSE_BUTTON_UP:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);
            event.button.button = (Uint8)PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.button.down = args[2] == Py_True;
            break;
        }
        case SDL_EVENT_KEY_DOWN:
        case SDL_EVENT_KEY_UP:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(4);
            event.key.scancode = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.key.down = args[2] == Py_True;
            event.key.repeat = args[3] == Py_True;
            break;
        }
        case SDL_EVENT_TEXT_INPUT:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);
            event.text.text = PyUnicode_AsUTF8(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_WINDOW_RESIZED:
        case SDL_EVENT_WINDOW_MOVED:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);
            event.window.data1 = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.window.data2 = PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_DISPLAY_ADDED:
        case SDL_EVENT_DISPLAY_REMOVED:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);
            event.display.displayID = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_DISPLAY_ORIENTATION:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);
            event.display.displayID = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.display.data1 = PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_JOYSTICK_ADDED:
        case SDL_EVENT_JOYSTICK_REMOVED:
        case SDL_EVENT_JOYSTICK_AXIS_MOTION:
        case SDL_EVENT_JOYSTICK_BUTTON_DOWN:
        case SDL_EVENT_JOYSTICK_BUTTON_UP:
        case SDL_EVENT_JOYSTICK_HAT_MOTION:
        {
            PyErr_Format(
                PyExc_RuntimeError,
                "unable to meaningfully push this kind of event, "
                "use a virtual joystick"
            );
            goto error;
        }
        case SDL_EVENT_DISPLAY_MOVED:
        case SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED:
        {
            PyErr_Format(
                PyExc_RuntimeError,
                "unable to meaningfully push this kind of event, "
                "we really on SDL state to complete the event data when polling"
            );
            goto error;
        }
    }

    if (!SDL_PushEvent(&event)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_sdl_event(PyObject *module, PyObject *unused)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;

    SDL_Event event;
    int result = SDL_PollEvent(&event);
    if (result == 0)
    {
        Py_RETURN_NONE;
    }

    switch(event.type)
    {
        case SDL_EVENT_MOUSE_MOTION:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int position[2] = {(int)event.motion.x, (int)event.motion.y};
            PyObject *py_position = emath_api->IVector2_Create(position);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int delta[2] = {(int)event.motion.xrel, (int)event.motion.yrel};
            PyObject *py_delta = emath_api->IVector2_Create(delta);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iOO)", event.type, py_position, py_delta);
        }
        case SDL_EVENT_MOUSE_WHEEL:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            int c = 1;
            if (event.wheel.direction == SDL_MOUSEWHEEL_FLIPPED)
            {
                c = -1;
            }

            const int delta[2] = {(int)event.wheel.x * c, (int)event.wheel.y * c};
            PyObject *py_delta = emath_api->IVector2_Create(delta);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iO)", event.type, py_delta);
        }
        case SDL_EVENT_MOUSE_BUTTON_DOWN:
        case SDL_EVENT_MOUSE_BUTTON_UP:
        {
            return Py_BuildValue(
                "(iBO)",
                event.type,
                event.button.button,
                event.button.down ? Py_True : Py_False
            );
        }
        case SDL_EVENT_KEY_DOWN:
        case SDL_EVENT_KEY_UP:
        {
            return Py_BuildValue(
                "(iiOO)",
                event.type,
                event.key.scancode,
                event.key.down ? Py_True : Py_False,
                event.key.repeat ? Py_True: Py_False
            );
        }
        case SDL_EVENT_TEXT_INPUT:
        {
            return Py_BuildValue("(is)", event.type, event.text.text);
        }
        case SDL_EVENT_WINDOW_RESIZED:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int size[2] = {(int)event.window.data1, (int)event.window.data2};
            PyObject *py_size = emath_api->IVector2_Create(size);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iO)", event.type, py_size);
        }
        case SDL_EVENT_WINDOW_MOVED:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int position[2] = {(int)event.window.data1, (int)event.window.data2};
            PyObject *py_position = emath_api->IVector2_Create(position);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iO)", event.type, py_position);
        }
        case SDL_EVENT_DISPLAY_ADDED:
        case SDL_EVENT_DISPLAY_REMOVED:
        {
            return Py_BuildValue("(ii)", event.type, event.display.displayID);
        }
        case SDL_EVENT_DISPLAY_ORIENTATION:
        {
            return Py_BuildValue(
                "(iii)",
                event.type,
                event.display.displayID,
                event.display.data1
            );
        }
        case SDL_EVENT_DISPLAY_MOVED:
        {
            SDL_Rect display_bounds;
            if (!SDL_GetDisplayBounds(event.display.displayID, &display_bounds))
            {
                RAISE_SDL_ERROR();
            }

            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int position[2] = {display_bounds.x, display_bounds.y};
            PyObject *py_position = emath_api->IVector2_Create(position);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iiO)", event.type, event.display.displayID, py_position);
        }
        case SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED:
        {
            SDL_Rect display_bounds;
            if (!SDL_GetDisplayBounds(event.display.displayID, &display_bounds))
            {
                RAISE_SDL_ERROR();
            }
            const SDL_DisplayMode *display_mode = SDL_GetCurrentDisplayMode(
                event.display.displayID
            );
            if (!display_mode){ RAISE_SDL_ERROR(); }

            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int size[2] = {display_bounds.w, display_bounds.h};
            PyObject *py_size = emath_api->IVector2_Create(size);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue(
                "(iiOf)",
                event.type,
                event.display.displayID,
                py_size,
                display_mode->refresh_rate
            );
        }
        case SDL_EVENT_JOYSTICK_ADDED:
        case SDL_EVENT_JOYSTICK_REMOVED:
        {
            return Py_BuildValue("(ii)", event.type, event.jdevice.which);
        }
        case SDL_EVENT_JOYSTICK_AXIS_MOTION:
        {
            return Py_BuildValue(
                "(iiid)",
                event.type,
                event.jaxis.which,
                event.jaxis.axis,
                normalize_sdl_joystick_axis_value_(event.jaxis.value)
            );
        }
        case SDL_EVENT_JOYSTICK_BUTTON_DOWN:
        case SDL_EVENT_JOYSTICK_BUTTON_UP:
        {
            return Py_BuildValue("(iii)", event.type, event.jbutton.which, event.jbutton.button);
        }
        case SDL_EVENT_JOYSTICK_HAT_MOTION:
        {
            return Py_BuildValue(
                "(iiii)",
                event.type,
                event.jhat.which,
                event.jhat.hat,
                (int)event.jhat.value
            );
        }
    }

    return Py_BuildValue("(i)", event.type);
error:
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
show_cursor(PyObject *module, PyObject *unused)
{
    if (!SDL_ShowCursor()){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
hide_cursor(PyObject *module, PyObject *unused)
{
    if (!SDL_HideCursor()){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_sdl_joysticks(PyObject *module, PyObject *unused)
{
    PyObject *py_joysticks = 0;
    int count;
    SDL_JoystickID *joysticks = SDL_GetJoysticks(&count);
    if (joysticks == 0){ RAISE_SDL_ERROR(); }

    py_joysticks = PyTuple_New(count);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    for (int i = 0; i < count; i++)
    {
        SDL_JoystickID joystick = joysticks[i];
        PyObject *py_joystick = PyLong_FromUnsignedLong(joystick);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_joysticks, i, py_joystick);
    }

    SDL_free(joysticks);
    joysticks = 0;

    return py_joysticks;
error:
    Py_XDECREF(py_joysticks);
    SDL_free(joysticks);
    return 0;
}

static PyObject *
get_sdl_joystick_axis_details_(SDL_JoystickID joystick)
{
    PyObject *py_result = 0;

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    int count = SDL_GetNumJoystickAxes(open_joystick);
    if (count == -1){ RAISE_SDL_ERROR(); }

    py_result = PyTuple_New(count);
    for (int i = 0; i < count; i++)
    {
        Sint16 position = SDL_GetJoystickAxis(open_joystick, i);
        PyObject *py_item = Py_BuildValue("(d)", normalize_sdl_joystick_axis_value_(position));
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_result, i, py_item);
    }
    return py_result;
error:
    Py_XDECREF(py_result);
    return 0;
}

static PyObject *
get_sdl_joystick_button_details_(SDL_JoystickID joystick)
{
    PyObject *py_result = 0;

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    int count = SDL_GetNumJoystickButtons(open_joystick);
    if (count == -1){ RAISE_SDL_ERROR(); }

    py_result = PyTuple_New(count);
    for (int i = 0; i < count; i++)
    {
        bool is_pressed = SDL_GetJoystickButton(open_joystick, i);
        PyObject *py_item = Py_BuildValue("(O)", is_pressed ? Py_True : Py_False);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_result, i, py_item);
    }
    return py_result;
error:
    Py_XDECREF(py_result);
    return 0;
}

static PyObject *
get_sdl_joystick_hat_details_(SDL_JoystickID joystick)
{
    PyObject *py_result = 0;

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    int count = SDL_GetNumJoystickHats(open_joystick);
    if (count == -1){ RAISE_SDL_ERROR(); }

    py_result = PyTuple_New(count);
    for (int i = 0; i < count; i++)
    {
        Uint8 value = SDL_GetJoystickHat(open_joystick, i);
        PyObject *py_item = Py_BuildValue("(B)", (unsigned char)value);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_result, i, py_item);
    }
    return py_result;
error:
    Py_XDECREF(py_result);
    return 0;
}


static PyObject *
get_sdl_joystick_mapping_details_(SDL_JoystickID joystick)
{
    SDL_Gamepad *open_gamepad = 0;
    PyObject *py_bindings = 0;
    PyObject *py_item = 0;
    SDL_GamepadBinding **bindings = 0;
    if (!SDL_IsGamepad(joystick))
    {
        Py_RETURN_NONE;
    }

    open_gamepad = SDL_OpenGamepad(joystick);
    if (!open_gamepad){ RAISE_SDL_ERROR(); }

    int count;
    bindings = SDL_GetGamepadBindings(open_gamepad, &count);
    if (!bindings){ RAISE_SDL_ERROR(); }

    py_bindings = PyTuple_New(count);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    for (int i = 0; i < count; i++)
    {
        SDL_GamepadBinding *binding = bindings[i];

        PyObject *py_item = PyTuple_New(2);

        PyObject *py_input;
        switch(binding->input_type)
        {
            case SDL_GAMEPAD_BINDTYPE_BUTTON:
            {
                py_input = Py_BuildValue(
                    "(ii)",
                    binding->input_type,
                    binding->input.button
                );
                break;
            }
            case SDL_GAMEPAD_BINDTYPE_AXIS:
            {
                py_input = Py_BuildValue(
                    "(iidd)",
                    binding->input_type,
                    binding->input.axis.axis,
                    normalize_sdl_joystick_axis_value_(binding->input.axis.axis_min),
                    normalize_sdl_joystick_axis_value_(binding->input.axis.axis_max)
                );
                break;
            }
            case SDL_GAMEPAD_BINDTYPE_HAT:
            {
                py_input = Py_BuildValue(
                    "(iii)",
                    binding->input_type,
                    binding->input.hat.hat,
                    binding->input.hat.hat_mask
                );
                break;
            }
            default:
            {
                continue;
            }
        }
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_item, 0, py_input);

        PyObject *py_output;
        switch(binding->output_type)
        {
            case SDL_GAMEPAD_BINDTYPE_BUTTON:
            {
                py_output = Py_BuildValue(
                    "(iii)",
                    binding->output_type,
                    binding->output.button,
                    SDL_GetGamepadButtonLabel(open_gamepad, binding->output.button)
                );
                break;
            }
            case SDL_GAMEPAD_BINDTYPE_AXIS:
            {
                py_output = Py_BuildValue(
                    "(iidd)",
                    binding->output_type,
                    binding->output.axis.axis,
                    normalize_sdl_joystick_axis_value_(binding->output.axis.axis_min),
                    normalize_sdl_joystick_axis_value_(binding->output.axis.axis_max)
                );
                break;
            }
            default:
            {
                continue;
            }
        }
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_item, 1, py_output);

        PyTuple_SET_ITEM(py_bindings, i, py_item);
    }

    SDL_GamepadType type = SDL_GetGamepadType(open_gamepad);

    SDL_free(bindings);
    SDL_CloseGamepad(open_gamepad);

    return Py_BuildValue("(Oi)", py_bindings, type);
error:
    SDL_free(bindings);
    Py_XDECREF(py_item);
    Py_XDECREF(py_bindings);
    if (open_gamepad){ SDL_CloseGamepad(open_gamepad); }
    return 0;
}

static PyObject *
open_sdl_joystick(PyObject *module, PyObject *py_joystick)
{
    SDL_Joystick *open_joystick = 0;
    PyObject *mapping_details = 0;
    PyObject *axis_details = 0;
    PyObject *button_details = 0;
    PyObject *hat_details = 0;

    SDL_JoystickID joystick = PyLong_AsLong(py_joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    open_joystick = SDL_OpenJoystick(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }
    const char *name = SDL_GetJoystickNameForID(joystick);
    if (!name){ RAISE_SDL_ERROR(); }
    SDL_GUID sdl_guid = SDL_GetJoystickGUIDForID(joystick);
    char guid[33];
    SDL_GUIDToString(sdl_guid, guid, sizeof(guid));
    const char *serial = SDL_GetJoystickSerial(open_joystick);
    int player_index = SDL_GetJoystickPlayerIndex(open_joystick);
    axis_details = get_sdl_joystick_axis_details_(joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    button_details = get_sdl_joystick_button_details_(joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    hat_details = get_sdl_joystick_hat_details_(joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    mapping_details = get_sdl_joystick_mapping_details_(joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *py_result = Py_BuildValue(
        "(sssiOOOO)",
        name,
        guid,
        serial,
        player_index,
        axis_details,
        button_details,
        hat_details,
        mapping_details
    );
    CHECK_UNEXPECTED_PYTHON_ERROR();

    return py_result;
error:
    Py_XDECREF(axis_details);
    Py_XDECREF(button_details);
    Py_XDECREF(hat_details);
    Py_XDECREF(mapping_details);
    if (open_joystick){ SDL_CloseJoystick(open_joystick); }
    return 0;
}

static PyObject *
close_sdl_joystick(PyObject *module, PyObject *py_joystick)
{
    SDL_JoystickID joystick = PyLong_AsLong(py_joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (open_joystick)
    {
        SDL_CloseJoystick(open_joystick);
    }
    else
    {
        SDL_ClearError();
    }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
connect_virtual_joystick(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(5);

    SDL_VirtualJoystickDesc desc;
    SDL_INIT_INTERFACE(&desc);
    desc.name = PyUnicode_AsUTF8AndSize(args[0], 0);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    desc.naxes = (Uint16)PyLong_AsUnsignedLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    desc.nballs = (Uint16)PyLong_AsUnsignedLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    desc.nbuttons = (Uint16)PyLong_AsUnsignedLong(args[3]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    desc.nhats = (Uint16)PyLong_AsUnsignedLong(args[4]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    SDL_JoystickID joystick = SDL_AttachVirtualJoystick(&desc);
    if (joystick == 0){ RAISE_SDL_ERROR(); }
    return PyLong_FromUnsignedLong(joystick);
error:
    return 0;
}

static PyObject *
disconnect_virtual_joystick(PyObject *module, PyObject *py_joystick)
{
    SDL_JoystickID joystick = PyLong_AsLong(py_joystick);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    SDL_DetachVirtualJoystick(joystick);
    SDL_ClearError();
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_virtual_joystick_axis_position(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

    SDL_JoystickID joystick = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    long axis = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    double value = PyFloat_AsDouble(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    value = -SDL_JOYSTICK_AXIS_MIN * value;
    if (value < SDL_JOYSTICK_AXIS_MIN){ value = SDL_JOYSTICK_AXIS_MIN; }
    if (value > SDL_JOYSTICK_AXIS_MAX){ value = SDL_JOYSTICK_AXIS_MAX; }

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    if (!SDL_SetJoystickVirtualAxis(open_joystick, axis, (Sint16)value)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_virtual_joystick_button_press(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

    SDL_JoystickID joystick = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    long button = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    bool is_pressed = args[2] == Py_True;

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    if (!SDL_SetJoystickVirtualButton(open_joystick, button, is_pressed)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_virtual_joystick_hat_value(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

    SDL_JoystickID joystick = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    long hat = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    long value = PyLong_AsLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    SDL_Joystick *open_joystick = SDL_GetJoystickFromID(joystick);
    if (!open_joystick){ RAISE_SDL_ERROR(); }

    if (!SDL_SetJoystickVirtualHat(open_joystick, hat, (Uint8)value)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}


static PyObject *
add_sdl_gamepad_mapping(PyObject *module, PyObject *py_mapping)
{
    const char *mapping = PyUnicode_AsUTF8AndSize(py_mapping, 0);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    if (SDL_AddGamepadMapping(mapping) == -1){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}


static PyObject *
get_sdl_displays(PyObject *module, PyObject *unused)
{
    PyObject *py_displays = 0;
    int count;
    SDL_DisplayID *displays = SDL_GetDisplays(&count);
    if (displays == 0){ RAISE_SDL_ERROR(); }

    py_displays = PyTuple_New(count);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    for (int i = 0; i < count; i++)
    {
        SDL_DisplayID display = displays[i];
        PyObject *py_display = PyLong_FromUnsignedLong(display);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PyTuple_SET_ITEM(py_displays, i, py_display);
    }

    SDL_free(displays);
    displays = 0;

    return py_displays;
error:
    Py_XDECREF(py_displays);
    SDL_free(displays);
    return 0;
}

static PyObject *
get_sdl_display_display_modes_(SDL_DisplayID display)
{
    PyObject *py_modes = 0;
    PyObject *py_mode = 0;
    int count;
    SDL_DisplayMode **modes = SDL_GetFullscreenDisplayModes(display, &count);
    if (!modes){ RAISE_SDL_ERROR(); }

    py_modes = PySet_New(0);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    for (int i = 0; i < count; i++)
    {
        SDL_DisplayMode *mode = modes[i];
        py_mode = Py_BuildValue("(iif)", mode->w, mode->h, mode->refresh_rate);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        PySet_Add(py_modes, py_mode);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        Py_DECREF(py_mode);
        py_mode = 0;
    }

    return py_modes;
error:
    Py_XDECREF(py_mode);
    Py_XDECREF(py_modes);
    return 0;
}

static PyObject *
get_sdl_display_details(PyObject *module, PyObject *py_display)
{
    SDL_DisplayID display = PyLong_AsLong(py_display);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const char *display_name = SDL_GetDisplayName(display);
    if (!display_name){ RAISE_SDL_ERROR(); }
    SDL_DisplayOrientation display_orientation = SDL_GetCurrentDisplayOrientation(display);
    SDL_Rect display_bounds;
    if (!SDL_GetDisplayBounds(display, &display_bounds)){ RAISE_SDL_ERROR(); }
    const SDL_DisplayMode *display_mode = SDL_GetCurrentDisplayMode(display);
    if (!display_mode){ RAISE_SDL_ERROR(); }
    PyObject *py_display_modes = get_sdl_display_display_modes_(display);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *py_details = Py_BuildValue(
        "(siiiiifO)",
        display_name,
        display_orientation,
        display_bounds.x,
        display_bounds.y,
        display_bounds.w,
        display_bounds.h,
        display_mode->refresh_rate,
        py_display_modes
    );
    CHECK_UNEXPECTED_PYTHON_ERROR();
    Py_DECREF(py_display_modes);
    return py_details;
error:
    return 0;
}

static PyMethodDef module_PyMethodDef[] = {
    {"initialize_sdl", initialize_sdl, METH_NOARGS, 0},
    {"deinitialize_sdl", deinitialize_sdl, METH_NOARGS, 0},
    {"create_sdl_window", (PyCFunction)create_sdl_window, METH_FASTCALL, 0},
    {"delete_sdl_window", delete_sdl_window, METH_O, 0},
    {"show_sdl_window", show_sdl_window, METH_O, 0},
    {"hide_sdl_window", hide_sdl_window, METH_O, 0},
    {"set_sdl_window_size", (PyCFunction)set_sdl_window_size, METH_FASTCALL, 0},
    {"set_sdl_window_position", (PyCFunction)set_sdl_window_position, METH_FASTCALL, 0},
    {"set_sdl_window_title", (PyCFunction)set_sdl_window_title, METH_FASTCALL, 0},
    {"center_sdl_window", center_sdl_window, METH_O, 0},
    {"swap_sdl_window", (PyCFunction)swap_sdl_window, METH_FASTCALL, 0},
    {"enable_sdl_window_text_input", (PyCFunction)enable_sdl_window_text_input, METH_FASTCALL, 0},
    {"disable_sdl_window_text_input", disable_sdl_window_text_input, METH_O, 0},
    {"set_sdl_window_border", (PyCFunction)set_sdl_window_border, METH_FASTCALL, 0},
    {"set_sdl_window_resizeable", (PyCFunction)set_sdl_window_resizeable, METH_FASTCALL, 0},
    {"set_sdl_window_always_on_top", (PyCFunction)set_sdl_window_always_on_top, METH_FASTCALL, 0},
    {"set_sdl_window_fullscreen", (PyCFunction)set_sdl_window_fullscreen, METH_FASTCALL, 0},
    {"set_sdl_window_not_fullscreen", set_sdl_window_not_fullscreen, METH_O, 0},
    {"set_sdl_window_icon", (PyCFunction)set_sdl_window_icon, METH_FASTCALL, 0},
    {"maximize_sdl_window", maximize_sdl_window, METH_O, 0},
    {"create_sdl_gl_context", create_sdl_gl_context, METH_O, 0},
    {"delete_sdl_gl_context", delete_sdl_gl_context, METH_O, 0},
    {"get_gl_attrs", get_gl_attrs, METH_NOARGS, 0},
    {"set_clipboard", set_clipboard, METH_O, 0},
    {"get_clipboard", get_clipboard, METH_NOARGS, 0},
    {"clear_sdl_events", clear_sdl_events, METH_NOARGS, 0},
    {"push_sdl_event", (PyCFunction)push_sdl_event, METH_FASTCALL, 0},
    {"get_sdl_event", get_sdl_event, METH_NOARGS, 0},
    {"show_cursor", show_cursor, METH_NOARGS, 0},
    {"hide_cursor", hide_cursor, METH_NOARGS, 0},
    {"get_sdl_joysticks", get_sdl_joysticks, METH_NOARGS, 0},
    {"open_sdl_joystick", open_sdl_joystick, METH_O, 0},
    {"close_sdl_joystick", close_sdl_joystick, METH_O, 0},
    {"connect_virtual_joystick", (PyCFunction)connect_virtual_joystick, METH_FASTCALL, 0},
    {"disconnect_virtual_joystick", disconnect_virtual_joystick, METH_O, 0},
    {"set_virtual_joystick_axis_position", (PyCFunction)set_virtual_joystick_axis_position, METH_FASTCALL, 0},
    {"set_virtual_joystick_button_press", (PyCFunction)set_virtual_joystick_button_press, METH_FASTCALL, 0},
    {"set_virtual_joystick_hat_value", (PyCFunction)set_virtual_joystick_hat_value, METH_FASTCALL, 0},
    {"add_sdl_gamepad_mapping", add_sdl_gamepad_mapping, METH_O, 0},
    {"get_sdl_displays", get_sdl_displays, METH_NOARGS, 0},
    {"get_sdl_display_details", get_sdl_display_details, METH_O, 0},
    {0},
};

static struct PyModuleDef module_PyModuleDef = {
    PyModuleDef_HEAD_INIT,
    "eplatform._eplatform",
    0,
    sizeof(ModuleState),
    module_PyMethodDef,
};

PyMODINIT_FUNC
PyInit__eplatform()
{
    PyObject *module = PyModule_Create(&module_PyModuleDef);
    if (!module){ return 0; }

    if (PyState_AddModule(module, &module_PyModuleDef) == -1)
    {
        Py_DECREF(module);
        return 0;
    }
    {
        PyObject *r = reset_module_state(module, 0);
        if (!r)
        {
            Py_DECREF(module);
            return 0;
        }
        Py_DECREF(r);
    }

#define ADD_CONSTANT(n)\
    {\
        PyObject *constant = PyLong_FromLong(n);\
        if (!constant){ return 0; }\
        if (PyModule_AddObject(module, #n, constant) != 0)\
        {\
            Py_DECREF(constant);\
            return 0;\
        }\
    }

    ADD_CONSTANT(SDL_EVENT_QUIT);
    ADD_CONSTANT(SDL_EVENT_MOUSE_MOTION);
    ADD_CONSTANT(SDL_EVENT_MOUSE_WHEEL);
    ADD_CONSTANT(SDL_EVENT_MOUSE_BUTTON_DOWN);
    ADD_CONSTANT(SDL_EVENT_MOUSE_BUTTON_UP);
    ADD_CONSTANT(SDL_EVENT_KEY_DOWN);
    ADD_CONSTANT(SDL_EVENT_KEY_UP);
    ADD_CONSTANT(SDL_EVENT_TEXT_INPUT);
    ADD_CONSTANT(SDL_EVENT_WINDOW_RESIZED);
    ADD_CONSTANT(SDL_EVENT_WINDOW_SHOWN);
    ADD_CONSTANT(SDL_EVENT_WINDOW_HIDDEN);
    ADD_CONSTANT(SDL_EVENT_WINDOW_MOVED);
    ADD_CONSTANT(SDL_EVENT_WINDOW_FOCUS_GAINED);
    ADD_CONSTANT(SDL_EVENT_WINDOW_FOCUS_LOST);
    ADD_CONSTANT(SDL_EVENT_DISPLAY_ADDED);
    ADD_CONSTANT(SDL_EVENT_DISPLAY_REMOVED);
    ADD_CONSTANT(SDL_EVENT_DISPLAY_ORIENTATION);
    ADD_CONSTANT(SDL_EVENT_DISPLAY_MOVED);
    ADD_CONSTANT(SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_ADDED);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_REMOVED);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_AXIS_MOTION);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_BUTTON_DOWN);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_BUTTON_UP);
    ADD_CONSTANT(SDL_EVENT_JOYSTICK_HAT_MOTION);
    ADD_CONSTANT(SDL_EVENT_WINDOW_MAXIMIZED);
    ADD_CONSTANT(SDL_EVENT_WINDOW_RESTORED);

    ADD_CONSTANT(SDL_ORIENTATION_UNKNOWN);
    ADD_CONSTANT(SDL_ORIENTATION_LANDSCAPE);
    ADD_CONSTANT(SDL_ORIENTATION_LANDSCAPE_FLIPPED);
    ADD_CONSTANT(SDL_ORIENTATION_PORTRAIT);
    ADD_CONSTANT(SDL_ORIENTATION_PORTRAIT_FLIPPED);

    ADD_CONSTANT(SDL_BUTTON_LEFT);
    ADD_CONSTANT(SDL_BUTTON_MIDDLE);
    ADD_CONSTANT(SDL_BUTTON_RIGHT);
    ADD_CONSTANT(SDL_BUTTON_X1);
    ADD_CONSTANT(SDL_BUTTON_X2);

    ADD_CONSTANT(SDL_GAMEPAD_BINDTYPE_BUTTON);
    ADD_CONSTANT(SDL_GAMEPAD_BINDTYPE_AXIS);
    ADD_CONSTANT(SDL_GAMEPAD_BINDTYPE_HAT);

    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_A);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_B);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_X);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_Y);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_CROSS);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_CIRCLE);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_SQUARE);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LABEL_TRIANGLE);

    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_SOUTH);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_EAST);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_WEST);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_NORTH);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_BACK);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_GUIDE);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_START);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LEFT_STICK);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_RIGHT_STICK);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LEFT_SHOULDER);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_DPAD_UP);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_DPAD_LEFT);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_DPAD_RIGHT);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC1);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_RIGHT_PADDLE1);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LEFT_PADDLE1);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_RIGHT_PADDLE2);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_LEFT_PADDLE2);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_TOUCHPAD);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC2);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC3);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC4);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC5);
    ADD_CONSTANT(SDL_GAMEPAD_BUTTON_MISC6);

    ADD_CONSTANT(SDL_GAMEPAD_AXIS_LEFTX);
    ADD_CONSTANT(SDL_GAMEPAD_AXIS_LEFTY);
    ADD_CONSTANT(SDL_GAMEPAD_AXIS_RIGHTX);
    ADD_CONSTANT(SDL_GAMEPAD_AXIS_RIGHTY);
    ADD_CONSTANT(SDL_GAMEPAD_AXIS_LEFT_TRIGGER);
    ADD_CONSTANT(SDL_GAMEPAD_AXIS_RIGHT_TRIGGER);

    ADD_CONSTANT(SDL_HAT_UP);
    ADD_CONSTANT(SDL_HAT_RIGHT);
    ADD_CONSTANT(SDL_HAT_DOWN);
    ADD_CONSTANT(SDL_HAT_LEFT);

    ADD_CONSTANT(SDL_GAMEPAD_TYPE_UNKNOWN);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_STANDARD);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_XBOX360);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_XBOXONE);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_PS3);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_PS4);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_PS5);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_LEFT);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT);
    ADD_CONSTANT(SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_JOYCON_PAIR);

    // number
    ADD_CONSTANT(SDL_SCANCODE_0);
    ADD_CONSTANT(SDL_SCANCODE_1);
    ADD_CONSTANT(SDL_SCANCODE_2);
    ADD_CONSTANT(SDL_SCANCODE_3);
    ADD_CONSTANT(SDL_SCANCODE_4);
    ADD_CONSTANT(SDL_SCANCODE_5);
    ADD_CONSTANT(SDL_SCANCODE_6);
    ADD_CONSTANT(SDL_SCANCODE_7);
    ADD_CONSTANT(SDL_SCANCODE_8);
    ADD_CONSTANT(SDL_SCANCODE_9);
    // function
    ADD_CONSTANT(SDL_SCANCODE_F1);
    ADD_CONSTANT(SDL_SCANCODE_F2);
    ADD_CONSTANT(SDL_SCANCODE_F3);
    ADD_CONSTANT(SDL_SCANCODE_F4);
    ADD_CONSTANT(SDL_SCANCODE_F5);
    ADD_CONSTANT(SDL_SCANCODE_F6);
    ADD_CONSTANT(SDL_SCANCODE_F7);
    ADD_CONSTANT(SDL_SCANCODE_F8);
    ADD_CONSTANT(SDL_SCANCODE_F9);
    ADD_CONSTANT(SDL_SCANCODE_F10);
    ADD_CONSTANT(SDL_SCANCODE_F11);
    ADD_CONSTANT(SDL_SCANCODE_F12);
    ADD_CONSTANT(SDL_SCANCODE_F13);
    ADD_CONSTANT(SDL_SCANCODE_F14);
    ADD_CONSTANT(SDL_SCANCODE_F15);
    ADD_CONSTANT(SDL_SCANCODE_F16);
    ADD_CONSTANT(SDL_SCANCODE_F17);
    ADD_CONSTANT(SDL_SCANCODE_F18);
    ADD_CONSTANT(SDL_SCANCODE_F19);
    ADD_CONSTANT(SDL_SCANCODE_F20);
    ADD_CONSTANT(SDL_SCANCODE_F21);
    ADD_CONSTANT(SDL_SCANCODE_F22);
    ADD_CONSTANT(SDL_SCANCODE_F23);
    ADD_CONSTANT(SDL_SCANCODE_F24);
    // letters
    ADD_CONSTANT(SDL_SCANCODE_A);
    ADD_CONSTANT(SDL_SCANCODE_B);
    ADD_CONSTANT(SDL_SCANCODE_C);
    ADD_CONSTANT(SDL_SCANCODE_D);
    ADD_CONSTANT(SDL_SCANCODE_E);
    ADD_CONSTANT(SDL_SCANCODE_F);
    ADD_CONSTANT(SDL_SCANCODE_G);
    ADD_CONSTANT(SDL_SCANCODE_H);
    ADD_CONSTANT(SDL_SCANCODE_I);
    ADD_CONSTANT(SDL_SCANCODE_J);
    ADD_CONSTANT(SDL_SCANCODE_K);
    ADD_CONSTANT(SDL_SCANCODE_L);
    ADD_CONSTANT(SDL_SCANCODE_M);
    ADD_CONSTANT(SDL_SCANCODE_N);
    ADD_CONSTANT(SDL_SCANCODE_O);
    ADD_CONSTANT(SDL_SCANCODE_P);
    ADD_CONSTANT(SDL_SCANCODE_Q);
    ADD_CONSTANT(SDL_SCANCODE_R);
    ADD_CONSTANT(SDL_SCANCODE_S);
    ADD_CONSTANT(SDL_SCANCODE_T);
    ADD_CONSTANT(SDL_SCANCODE_U);
    ADD_CONSTANT(SDL_SCANCODE_V);
    ADD_CONSTANT(SDL_SCANCODE_W);
    ADD_CONSTANT(SDL_SCANCODE_X);
    ADD_CONSTANT(SDL_SCANCODE_Y);
    ADD_CONSTANT(SDL_SCANCODE_Z);
    // symbols/operators
    ADD_CONSTANT(SDL_SCANCODE_APOSTROPHE);
    ADD_CONSTANT(SDL_SCANCODE_BACKSLASH);
    ADD_CONSTANT(SDL_SCANCODE_COMMA);
    ADD_CONSTANT(SDL_SCANCODE_DECIMALSEPARATOR);
    ADD_CONSTANT(SDL_SCANCODE_EQUALS);
    ADD_CONSTANT(SDL_SCANCODE_GRAVE);
    ADD_CONSTANT(SDL_SCANCODE_LEFTBRACKET);
    ADD_CONSTANT(SDL_SCANCODE_MINUS);
    ADD_CONSTANT(SDL_SCANCODE_NONUSBACKSLASH);
    ADD_CONSTANT(SDL_SCANCODE_NONUSHASH);
    ADD_CONSTANT(SDL_SCANCODE_PERIOD);
    ADD_CONSTANT(SDL_SCANCODE_RIGHTBRACKET);
    ADD_CONSTANT(SDL_SCANCODE_RSHIFT);
    ADD_CONSTANT(SDL_SCANCODE_SEMICOLON);
    ADD_CONSTANT(SDL_SCANCODE_SEPARATOR);
    ADD_CONSTANT(SDL_SCANCODE_SLASH);
    ADD_CONSTANT(SDL_SCANCODE_SPACE);
    ADD_CONSTANT(SDL_SCANCODE_TAB);
    ADD_CONSTANT(SDL_SCANCODE_THOUSANDSSEPARATOR);
    // actions
    ADD_CONSTANT(SDL_SCANCODE_AGAIN);
    ADD_CONSTANT(SDL_SCANCODE_ALTERASE);
    ADD_CONSTANT(SDL_SCANCODE_APPLICATION);
    ADD_CONSTANT(SDL_SCANCODE_BACKSPACE);
    ADD_CONSTANT(SDL_SCANCODE_CANCEL);
    ADD_CONSTANT(SDL_SCANCODE_CAPSLOCK);
    ADD_CONSTANT(SDL_SCANCODE_CLEAR);
    ADD_CONSTANT(SDL_SCANCODE_CLEARAGAIN);
    ADD_CONSTANT(SDL_SCANCODE_COPY);
    ADD_CONSTANT(SDL_SCANCODE_CRSEL);
    ADD_CONSTANT(SDL_SCANCODE_CURRENCYSUBUNIT);
    ADD_CONSTANT(SDL_SCANCODE_CURRENCYUNIT);
    ADD_CONSTANT(SDL_SCANCODE_CUT);
    ADD_CONSTANT(SDL_SCANCODE_DELETE);
    ADD_CONSTANT(SDL_SCANCODE_END);
    ADD_CONSTANT(SDL_SCANCODE_ESCAPE);
    ADD_CONSTANT(SDL_SCANCODE_EXECUTE);
    ADD_CONSTANT(SDL_SCANCODE_EXSEL);
    ADD_CONSTANT(SDL_SCANCODE_FIND);
    ADD_CONSTANT(SDL_SCANCODE_HELP);
    ADD_CONSTANT(SDL_SCANCODE_HOME);
    ADD_CONSTANT(SDL_SCANCODE_INSERT);
    ADD_CONSTANT(SDL_SCANCODE_LALT);
    ADD_CONSTANT(SDL_SCANCODE_LCTRL);
    ADD_CONSTANT(SDL_SCANCODE_LGUI);
    ADD_CONSTANT(SDL_SCANCODE_LSHIFT);
    ADD_CONSTANT(SDL_SCANCODE_MENU);
    ADD_CONSTANT(SDL_SCANCODE_MODE);
    ADD_CONSTANT(SDL_SCANCODE_NUMLOCKCLEAR);
    ADD_CONSTANT(SDL_SCANCODE_OPER);
    ADD_CONSTANT(SDL_SCANCODE_OUT);
    ADD_CONSTANT(SDL_SCANCODE_PAGEDOWN);
    ADD_CONSTANT(SDL_SCANCODE_PAGEUP);
    ADD_CONSTANT(SDL_SCANCODE_PASTE);
    ADD_CONSTANT(SDL_SCANCODE_PAUSE);
    ADD_CONSTANT(SDL_SCANCODE_POWER);
    ADD_CONSTANT(SDL_SCANCODE_PRINTSCREEN);
    ADD_CONSTANT(SDL_SCANCODE_PRIOR);
    ADD_CONSTANT(SDL_SCANCODE_RALT);
    ADD_CONSTANT(SDL_SCANCODE_RCTRL);
    ADD_CONSTANT(SDL_SCANCODE_RETURN);
    ADD_CONSTANT(SDL_SCANCODE_RETURN2);
    ADD_CONSTANT(SDL_SCANCODE_RGUI);
    ADD_CONSTANT(SDL_SCANCODE_SCROLLLOCK);
    ADD_CONSTANT(SDL_SCANCODE_SELECT);
    ADD_CONSTANT(SDL_SCANCODE_SLEEP);
    ADD_CONSTANT(SDL_SCANCODE_STOP);
    ADD_CONSTANT(SDL_SCANCODE_SYSREQ);
    ADD_CONSTANT(SDL_SCANCODE_UNDO);
    ADD_CONSTANT(SDL_SCANCODE_VOLUMEDOWN);
    ADD_CONSTANT(SDL_SCANCODE_VOLUMEUP);
    ADD_CONSTANT(SDL_SCANCODE_MUTE);
    // media
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_SELECT);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_EJECT);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_FAST_FORWARD);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_NEXT_TRACK);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_PLAY);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_PREVIOUS_TRACK);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_REWIND);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_STOP);
    // ac
    ADD_CONSTANT(SDL_SCANCODE_AC_BACK);
    ADD_CONSTANT(SDL_SCANCODE_AC_BOOKMARKS);
    ADD_CONSTANT(SDL_SCANCODE_AC_FORWARD);
    ADD_CONSTANT(SDL_SCANCODE_AC_HOME);
    ADD_CONSTANT(SDL_SCANCODE_AC_REFRESH);
    ADD_CONSTANT(SDL_SCANCODE_AC_SEARCH);
    ADD_CONSTANT(SDL_SCANCODE_AC_STOP);
    // arrows
    ADD_CONSTANT(SDL_SCANCODE_DOWN);
    ADD_CONSTANT(SDL_SCANCODE_LEFT);
    ADD_CONSTANT(SDL_SCANCODE_RIGHT);
    ADD_CONSTANT(SDL_SCANCODE_UP);
    // international
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL1);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL2);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL3);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL4);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL5);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL6);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL7);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL8);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL9);
    // numpad numbers
    ADD_CONSTANT(SDL_SCANCODE_KP_0);
    ADD_CONSTANT(SDL_SCANCODE_KP_00);
    ADD_CONSTANT(SDL_SCANCODE_KP_000);
    ADD_CONSTANT(SDL_SCANCODE_KP_1);
    ADD_CONSTANT(SDL_SCANCODE_KP_2);
    ADD_CONSTANT(SDL_SCANCODE_KP_3);
    ADD_CONSTANT(SDL_SCANCODE_KP_4);
    ADD_CONSTANT(SDL_SCANCODE_KP_5);
    ADD_CONSTANT(SDL_SCANCODE_KP_6);
    ADD_CONSTANT(SDL_SCANCODE_KP_7);
    ADD_CONSTANT(SDL_SCANCODE_KP_8);
    ADD_CONSTANT(SDL_SCANCODE_KP_9);
    // numpad letters
    ADD_CONSTANT(SDL_SCANCODE_KP_A);
    ADD_CONSTANT(SDL_SCANCODE_KP_B);
    ADD_CONSTANT(SDL_SCANCODE_KP_C);
    ADD_CONSTANT(SDL_SCANCODE_KP_D);
    ADD_CONSTANT(SDL_SCANCODE_KP_E);
    ADD_CONSTANT(SDL_SCANCODE_KP_F);
    // numpad symbols/operators
    ADD_CONSTANT(SDL_SCANCODE_KP_AMPERSAND);
    ADD_CONSTANT(SDL_SCANCODE_KP_AT);
    ADD_CONSTANT(SDL_SCANCODE_KP_COLON);
    ADD_CONSTANT(SDL_SCANCODE_KP_COMMA);
    ADD_CONSTANT(SDL_SCANCODE_KP_DBLAMPERSAND);
    ADD_CONSTANT(SDL_SCANCODE_KP_DBLVERTICALBAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_DECIMAL);
    ADD_CONSTANT(SDL_SCANCODE_KP_DIVIDE);
    ADD_CONSTANT(SDL_SCANCODE_KP_ENTER);
    ADD_CONSTANT(SDL_SCANCODE_KP_EQUALS);
    ADD_CONSTANT(SDL_SCANCODE_KP_EQUALSAS400);
    ADD_CONSTANT(SDL_SCANCODE_KP_EXCLAM);
    ADD_CONSTANT(SDL_SCANCODE_KP_GREATER);
    ADD_CONSTANT(SDL_SCANCODE_KP_HASH);
    ADD_CONSTANT(SDL_SCANCODE_KP_LEFTBRACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_LEFTPAREN);
    ADD_CONSTANT(SDL_SCANCODE_KP_LESS);
    ADD_CONSTANT(SDL_SCANCODE_KP_MINUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_MULTIPLY);
    ADD_CONSTANT(SDL_SCANCODE_KP_PERCENT);
    ADD_CONSTANT(SDL_SCANCODE_KP_PERIOD);
    ADD_CONSTANT(SDL_SCANCODE_KP_PLUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_PLUSMINUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_POWER);
    ADD_CONSTANT(SDL_SCANCODE_KP_RIGHTBRACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_RIGHTPAREN);
    ADD_CONSTANT(SDL_SCANCODE_KP_SPACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_TAB);
    ADD_CONSTANT(SDL_SCANCODE_KP_VERTICALBAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_XOR);
    // numpad actions
    ADD_CONSTANT(SDL_SCANCODE_KP_BACKSPACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_BINARY);
    ADD_CONSTANT(SDL_SCANCODE_KP_CLEAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_CLEARENTRY);
    ADD_CONSTANT(SDL_SCANCODE_KP_HEXADECIMAL);
    ADD_CONSTANT(SDL_SCANCODE_KP_OCTAL);
    // memory
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMADD);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMCLEAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMDIVIDE);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMMULTIPLY);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMRECALL);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMSTORE);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMSUBTRACT);
    // language
    ADD_CONSTANT(SDL_SCANCODE_LANG1);
    ADD_CONSTANT(SDL_SCANCODE_LANG2);
    ADD_CONSTANT(SDL_SCANCODE_LANG3);
    ADD_CONSTANT(SDL_SCANCODE_LANG4);
    ADD_CONSTANT(SDL_SCANCODE_LANG5);
    ADD_CONSTANT(SDL_SCANCODE_LANG6);
    ADD_CONSTANT(SDL_SCANCODE_LANG7);
    ADD_CONSTANT(SDL_SCANCODE_LANG8);
    ADD_CONSTANT(SDL_SCANCODE_LANG9);

    return module;
}
