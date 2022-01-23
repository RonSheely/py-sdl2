import os
import sys
import ctypes
from ctypes.util import find_library
from ctypes import c_int, c_ubyte, c_float, byref, cast, POINTER, py_object
import pytest
import sdl2
from sdl2.stdinc import SDL_FALSE, SDL_TRUE
from sdl2 import video, rect, surface, SDL_GetError

# TODO: Have optional environment variable to toggle annoying video tests
# (e.g. fullscreen, window maximize/minimize, flash window)

# Some tests don't work properly with some video drivers, so check the name
DRIVER_DUMMY = False
DRIVER_X11 = False
try:
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    driver_name = video.SDL_GetCurrentVideoDriver()
    sdl2.SDL_Quit()
    DRIVER_DUMMY = driver_name == b"dummy"
    DRIVER_X11 = driver_name == b"x11"
except:
    pass

# Some tests don't work right on PyPy
is_pypy = hasattr(sys, "pypy_version_info")

if sys.version_info[0] >= 3:
    long = int

to_ctypes = lambda seq, dtype: (dtype * len(seq))(*seq)

def has_opengl_lib():
    for libname in("gl", "opengl", "opengl32"):
        path = find_library(libname)
        if path is not None:
            return True

def get_opengl_path():
    for libname in("gl", "opengl", "opengl32"):
        path = find_library(libname)
        if path is not None:
            return path

@pytest.fixture
def window(with_sdl):
    flag = video.SDL_WINDOW_BORDERLESS
    w = video.SDL_CreateWindow(b"Test", 10, 40, 12, 13, flag)
    assert SDL_GetError() == b""
    assert isinstance(w.contents, video.SDL_Window)
    yield w
    video.SDL_DestroyWindow(w)

@pytest.fixture
def decorated_window(with_sdl):
    w = video.SDL_CreateWindow(b"Test", 10, 40, 12, 13, 0)
    assert SDL_GetError() == b""
    assert isinstance(w.contents, video.SDL_Window)
    yield w
    video.SDL_DestroyWindow(w)


# Test custom macros

def test_SDL_WINDOWPOS_UNDEFINED_DISPLAY():
    undef_mask = video.SDL_WINDOWPOS_UNDEFINED_MASK
    for x in range(0xFFFF):
        undef = video.SDL_WINDOWPOS_UNDEFINED_DISPLAY(x)
        assert undef_mask | x == undef
        assert (undef & undef_mask) == undef_mask
        assert undef != video.SDL_WINDOWPOS_CENTERED_DISPLAY(x)

def test_SDL_WINDOWPOS_ISUNDEFINED():
    assert video.SDL_WINDOWPOS_ISUNDEFINED(video.SDL_WINDOWPOS_UNDEFINED)
    assert not video.SDL_WINDOWPOS_ISUNDEFINED(video.SDL_WINDOWPOS_CENTERED)
    for x in range(0xFFFF):
        undef = video.SDL_WINDOWPOS_UNDEFINED_DISPLAY(x)
        assert video.SDL_WINDOWPOS_ISUNDEFINED(undef)

def test_SDL_WINDOWPOS_CENTERED_DISPLAY():
    centered_mask = video.SDL_WINDOWPOS_CENTERED_MASK
    for x in range(0xFFFF):
        centered = video.SDL_WINDOWPOS_CENTERED_DISPLAY(x)
        assert centered_mask | x == centered
        assert (centered & centered_mask) == centered_mask
        assert centered != video.SDL_WINDOWPOS_UNDEFINED_DISPLAY(x)

def test_SDL_WINDOWPOS_ISCENTERED():
    assert video.SDL_WINDOWPOS_ISCENTERED(video.SDL_WINDOWPOS_CENTERED)
    assert not video.SDL_WINDOWPOS_ISCENTERED(video.SDL_WINDOWPOS_UNDEFINED)
    for x in range(0xFFFF):
        centered = video.SDL_WINDOWPOS_CENTERED_DISPLAY(x)
        assert video.SDL_WINDOWPOS_ISCENTERED(centered)


# Test structures and classes

def test_SDL_Window():
    window = video.SDL_Window()
    assert isinstance(window, video.SDL_Window)


class TestSDLDisplayMode(object):

    def test_init(self):
        mode = video.SDL_DisplayMode()
        assert isinstance(mode, video.SDL_DisplayMode)
        fmt = sdl2.SDL_PIXELFORMAT_ARGB8888
        mode = video.SDL_DisplayMode(fmt, 800, 600, 60)
        assert isinstance(mode, video.SDL_DisplayMode)
        assert mode.format == fmt
        assert mode.w == 800
        assert mode.h == 600
        assert mode.refresh_rate == 60
        # Test exceptions on bad input
        with pytest.raises(TypeError):
            video.SDL_DisplayMode("Test")
        with pytest.raises(TypeError):
            video.SDL_DisplayMode(10, 10.6, 10, 10)
        with pytest.raises(TypeError):
            video.SDL_DisplayMode(10, 10, 10, None)

    def test___eq__(self):
        DMode = video.SDL_DisplayMode
        assert DMode() == DMode()
        assert DMode(10, 0, 0, 0) == DMode(10, 0, 0, 0)
        assert DMode(10, 10, 0, 0) == DMode(10, 10, 0, 0)
        assert DMode(10, 10, 10, 0) == DMode(10, 10, 10, 0)
        assert DMode(10, 10, 10, 10) == DMode(10, 10, 10, 10)
        assert DMode(0, 10, 0, 0) == DMode(0, 10, 0, 0)
        assert DMode(0, 0, 10, 0) == DMode(0, 0, 10, 0)
        assert DMode(0, 0, 0, 10) == DMode(0, 0, 0, 10)

        assert not (DMode() == DMode(10, 0, 0, 0))
        assert not (DMode(10, 0, 0, 0) == DMode(0, 0, 0, 0))
        assert not (DMode(10, 0, 0, 0) == DMode(0, 10, 0, 0))
        assert not (DMode(10, 0, 0, 0) == DMode(0, 0, 10, 0))
        assert not (DMode(10, 0, 0, 0) == DMode(0, 0, 0, 10))

    def test___ne__(self):
        DMode = video.SDL_DisplayMode
        assert not (DMode() != DMode())
        assert not (DMode(10, 0, 0, 0) != DMode(10, 0, 0, 0))
        assert not (DMode(10, 10, 0, 0) != DMode(10, 10, 0, 0))
        assert not (DMode(10, 10, 10, 0) != DMode(10, 10, 10, 0))
        assert not (DMode(10, 10, 10, 10) != DMode(10, 10, 10, 10))
        assert not (DMode(0, 10, 0, 0) != DMode(0, 10, 0, 0))
        assert not (DMode(0, 0, 10, 0) != DMode(0, 0, 10, 0))
        assert not (DMode(0, 0, 0, 10) != DMode(0, 0, 0, 10))

        assert DMode() != DMode(10, 0, 0, 0)
        assert DMode(10, 0, 0, 0) != DMode(0, 0, 0, 0)
        assert DMode(10, 0, 0, 0) != DMode(0, 10, 0, 0)
        assert DMode(10, 0, 0, 0) != DMode(0, 0, 10, 0)
        assert DMode(10, 0, 0, 0) != DMode(0, 0, 0, 10)


# Test module SDL functions

def test_SDL_VideoInitQuit():
    # Test with default driver
    assert sdl2.SDL_WasInit(0) & sdl2.SDL_INIT_VIDEO != sdl2.SDL_INIT_VIDEO
    ret = video.SDL_VideoInit(None)
    assert sdl2.SDL_GetError() == b""
    assert ret == 0
    assert video.SDL_GetCurrentVideoDriver() # If initialized, should be string
    video.SDL_VideoQuit()
    assert not video.SDL_GetCurrentVideoDriver()
    # TODO: Test with string input (fails with b"dummy" for some reason?)

def test_SDL_GetNumVideoDrivers(with_sdl):
    numdrivers = video.SDL_GetNumVideoDrivers()
    assert numdrivers >= 1

def test_SDL_GetVideoDriver(with_sdl):
    numdrivers = video.SDL_GetNumVideoDrivers()
    for i in range(numdrivers):
        name = video.SDL_GetVideoDriver(i)
        assert type(name) in (str, bytes)

def test_SDL_GetCurrentVideoDriver(with_sdl):
    curdriver = video.SDL_GetCurrentVideoDriver()
    numdrivers = video.SDL_GetNumVideoDrivers()
    drivers = []
    for i in range(numdrivers):
        drivers.append(video.SDL_GetVideoDriver(i))
    assert curdriver in drivers

def test_SDL_GetNumVideoDisplays(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    assert numdisplays >= 1

def test_SDL_GetNumDisplayModes(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        modes = video.SDL_GetNumDisplayModes(index)
        assert modes >= 1

def test_SDL_GetDisplayMode(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        modes = video.SDL_GetNumDisplayModes(index)
        for mode in range(modes):
            dmode = video.SDL_DisplayMode()
            ret = video.SDL_GetDisplayMode(index, mode, byref(dmode))
            assert sdl2.SDL_GetError() == b""
            assert ret == 0
            if not DRIVER_DUMMY:
                assert dmode.w > 0
                assert dmode.h > 0

def test_SDL_GetCurrentDisplayMode(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        dmode = video.SDL_DisplayMode()
        ret = video.SDL_GetCurrentDisplayMode(index, byref(dmode))
        assert sdl2.SDL_GetError() == b""
        assert ret == 0
        assert dmode.w > 0
        assert dmode.h > 0

def test_SDL_GetDesktopDisplayMode(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        dmode = video.SDL_DisplayMode()
        ret = video.SDL_GetDesktopDisplayMode(index, byref(dmode))
        assert sdl2.SDL_GetError() == b""
        assert ret == 0
        assert dmode.w > 0
        assert dmode.h > 0

@pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
def test_SDL_GetClosestDisplayMode(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        dmode = video.SDL_DisplayMode()
        ret = video.SDL_GetCurrentDisplayMode(index, byref(dmode))
        assert sdl2.SDL_GetError() == b""
        assert ret == 0
        cmode = video.SDL_DisplayMode(
            dmode.format, dmode.w - 1, dmode.h - 1, dmode.refresh_rate
        )
        closest = video.SDL_DisplayMode()
        video.SDL_GetClosestDisplayMode(index, cmode, byref(closest))
        assert closest == dmode

def test_SDL_GetDisplayName(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        name = video.SDL_GetDisplayName(index)
        assert type(name) in (str, bytes)

def test_SDL_GetDisplayBounds(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        bounds = rect.SDL_Rect()
        ret = video.SDL_GetDisplayBounds(index, byref(bounds))
        assert sdl2.SDL_GetError() == b""
        assert ret == 0
        assert bounds.w > 0
        assert bounds.h > 0
        assert not rect.SDL_RectEmpty(bounds)

@pytest.mark.skipif(sdl2.dll.version < 2009, reason="not available")
def test_SDL_GetDisplayOrientation(with_sdl):
    numdisplays = video.SDL_GetNumVideoDisplays()
    for index in range(numdisplays):
        orientation = video.SDL_GetDisplayOrientation(index)
        assert isinstance(orientation, int)
        assert orientation >= 0

def test_GetDisplayInfo(with_sdl):
    current = video.SDL_GetCurrentVideoDriver().decode('utf-8')
    print("Available Video Drivers:")
    for i in range(video.SDL_GetNumVideoDrivers()):
        name = video.SDL_GetVideoDriver(i).decode('utf-8')
        if name == current:
            name += " (*)"
        print(" - " + name)
    print("")
    print("Detected Displays:")
    for i in range(video.SDL_GetNumVideoDisplays()):
        name = video.SDL_GetDisplayName(i).decode('utf-8')
        info = " - " + name
        dm = video.SDL_DisplayMode()
        ret = video.SDL_GetDesktopDisplayMode(i, byref(dm))
        if ret == 0:
            res = " ({0}x{1} @ {2}Hz)".format(dm.w, dm.h, dm.refresh_rate)
            info += res
        print(info)

def test_screensaver(with_sdl):
    video.SDL_EnableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_TRUE
    video.SDL_EnableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_TRUE
    video.SDL_DisableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_FALSE
    video.SDL_DisableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_FALSE
    video.SDL_EnableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_TRUE
    video.SDL_DisableScreenSaver()
    assert video.SDL_IsScreenSaverEnabled() == SDL_FALSE

def test_SDL_CreateDestroyWindow(with_sdl):
    flag = video.SDL_WINDOW_BORDERLESS
    window = video.SDL_CreateWindow(b"Test", 10, 40, 12, 13, flag)
    assert SDL_GetError() == b""
    assert isinstance(window.contents, video.SDL_Window)
    video.SDL_DestroyWindow(window)

@pytest.mark.skip("not implemented")
def test_SDL_CreateWindowFrom(with_sdl):
    # No obvious cross-platform way to test this
    pass

def test_SDL_GetWindowDisplayIndex(window):
    numdisplays = video.SDL_GetNumVideoDisplays()
    dindex = video.SDL_GetWindowDisplayIndex(window)
    # Make sure display index is valid
    assert 0 <= dindex <= numdisplays

def test_SDL_GetWindowDisplayMode(window):
    # NOTE: Gets fullscreen mode of parent display, not size of window
    dmode = video.SDL_DisplayMode()
    ret = video.SDL_GetWindowDisplayMode(window, byref(dmode))
    assert SDL_GetError() == b""
    assert ret == 0
    assert dmode.w > 0
    assert dmode.h > 0

def test_SDL_SetWindowDisplayMode(window):
    # NOTE: Sets the fullscreen mode of the window, so can't easily test
    # NOTE: If set mode not supported, will change to closest supported res
    dindex = video.SDL_GetWindowDisplayIndex(window)
    dmode = video.SDL_DisplayMode()
    ret = video.SDL_GetCurrentDisplayMode(dindex, byref(dmode))
    assert ret == 0
    video.SDL_SetWindowDisplayMode(window, dmode)
    wmode = video.SDL_DisplayMode()
    ret = video.SDL_GetWindowDisplayMode(window, byref(wmode))
    assert SDL_GetError() == b""
    assert ret == 0
    assert dmode == wmode

@pytest.mark.skipif(sdl2.dll.version < 2018, reason="not available")
def test_SDL_GetWindowICCProfile(window):
    prof_size = ctypes.c_size_t(0)
    prof_ptr = video.SDL_GetWindowICCProfile(window, byref(prof_size))
    # This function returns a void pointer to the loaded ICC profile, which
    # needs to be cast to bytes to be read. As per the ICC spec, bytes
    # 36 to 39 of the header should always be 'acsp' in ASCII.
    if prof_size.value > 0:
        prof = ctypes.cast(prof_ptr, ctypes.POINTER(c_ubyte))
        assert bytes(prof[36:40]) == b"acsp"

def test_SDL_GetWindowPixelFormat(window):
    fmt = video.SDL_GetWindowPixelFormat(window)
    assert fmt in sdl2.ALL_PIXELFORMATS

def test_SDL_GetWindowID(window):
    assert video.SDL_GetWindowID(window) >= 0

def test_SDL_GetWindowFromID(window):
    window2 = video.SDL_GetWindowFromID(video.SDL_GetWindowID(window))
    assert video.SDL_GetWindowID(window) == video.SDL_GetWindowID(window2)
    assert video.SDL_GetWindowTitle(window) == video.SDL_GetWindowTitle(window2)
    # Make sure sizes/positions are the same
    px1, py1, px2, py2 = c_int(0), c_int(0), c_int(0), c_int(0)
    video.SDL_GetWindowPosition(window, byref(px1), byref(py1))
    video.SDL_GetWindowPosition(window2, byref(px2), byref(py2))
    assert (px1.value, py1.value) == (px2.value, py2.value)
    video.SDL_GetWindowSize(window, byref(px1), byref(py1))
    video.SDL_GetWindowSize(window2, byref(px2), byref(py2))
    assert (px1.value, py1.value) == (px2.value, py2.value)

def test_SDL_GetWindowFlags(with_sdl):
    flags = (
        video.SDL_WINDOW_BORDERLESS,
        video.SDL_WINDOW_BORDERLESS | video.SDL_WINDOW_HIDDEN,
        video.SDL_WINDOW_RESIZABLE
    )
    for flag in flags:
        win = video.SDL_CreateWindow(b"Test", 10, 10, 10, 10, flag)
        wflags = video.SDL_GetWindowFlags(win)
        assert (wflags & flag) == flag
        video.SDL_DestroyWindow(win)

def test_SDL_GetSetWindowTitle(window):
    assert video.SDL_GetWindowTitle(window) == b"Test"
    video.SDL_SetWindowTitle(window, b"Hello there")
    assert video.SDL_GetWindowTitle(window) == b"Hello there"

def test_SDL_SetWindowIcon(window):
    sf = surface.SDL_CreateRGBSurface(
        0, 16, 16, 16, 0xF000, 0x0F00, 0x00F0, 0x000F
    )
    assert isinstance(sf.contents, surface.SDL_Surface)
    video.SDL_SetWindowIcon(window, sf)
    assert SDL_GetError() == b""

@pytest.mark.xfail(is_pypy, reason="PyPy can't create proper py_object values")
def test_SDL_GetSetWindowData(window):
    values = {
        b"text": py_object("Teststring"),
        b"list": py_object([1, 2, "a", "b"]),
        b"tuple": py_object((1, 2, 3)),
    }
    for k, v in values.items():
        video.SDL_SetWindowData(window, k, v)
        retval = video.SDL_GetWindowData(window, k)
        assert retval.contents.value == v.value

@pytest.mark.xfail(DRIVER_X11, reason="Wonky with some window managers")
def test_SDL_GetSetWindowPosition(with_sdl):
    window = video.SDL_CreateWindow(b"Test", 10, 200, 10, 10, 0)
    px, py = c_int(0), c_int(0)
    video.SDL_GetWindowPosition(window, byref(px), byref(py))
    assert (px.value, py.value) == (10, 200)
    video.SDL_SetWindowPosition(window, 0, 150)
    video.SDL_GetWindowPosition(window, byref(px), byref(py))
    assert (px.value, py.value) == (0, 150)
    video.SDL_SetWindowPosition(window, 480, 320)
    video.SDL_GetWindowPosition(window, byref(px), byref(py))
    assert (px.value, py.value) == (480, 320)
    video.SDL_DestroyWindow(window)

def test_SDL_GetSetWindowSize(window):
    sx, sy = c_int(0), c_int(0)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (12, 13)
    video.SDL_SetWindowSize(window, 1, 1)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (1, 1)
    video.SDL_SetWindowSize(window, 480, 320)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (480, 320)
    # Test that negative sizes are ignored
    video.SDL_SetWindowSize(window, -200, -10)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (480, 320)

def test_SDL_GetSetWindowMinimumSize(window):
    sx, sy = c_int(0), c_int(0)
    minx, miny = c_int(0), c_int(0)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (12, 13)
    # Set and verify the minimum window size
    video.SDL_SetWindowMinimumSize(window, 10, 10)
    assert SDL_GetError() == b""
    video.SDL_GetWindowMinimumSize(window, byref(minx), byref(miny))
    assert (minx.value, miny.value) == (10, 10)
    # Make sure window can't be set below its minimum size
    video.SDL_SetWindowSize(window, 1, 1)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (10, 10)

def test_SDL_GetSetWindowMaximumSize(window):
    sx, sy = c_int(0), c_int(0)
    maxx, maxy = c_int(0), c_int(0)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (12, 13)
    # Set and verify the maximum window size
    video.SDL_SetWindowMaximumSize(window, 32, 32)
    assert SDL_GetError() == b""
    video.SDL_GetWindowMaximumSize(window, byref(maxx), byref(maxy))
    assert (maxx.value, maxy.value) == (32, 32)
    # Make sure window can't be set above its maximum size
    video.SDL_SetWindowSize(window, 50, 50)
    video.SDL_GetWindowSize(window, byref(sx), byref(sy))
    assert (sx.value, sy.value) == (32, 32)

def test_SDL_SetWindowBordered(window):
    border_flag = video.SDL_WINDOW_BORDERLESS
    assert video.SDL_GetWindowFlags(window) & border_flag == border_flag
    video.SDL_SetWindowBordered(window, SDL_TRUE)
    if not DRIVER_DUMMY:
        assert not video.SDL_GetWindowFlags(window) & border_flag == border_flag
        video.SDL_SetWindowBordered(window, SDL_FALSE)
        assert video.SDL_GetWindowFlags(window) & border_flag == border_flag

def test_SDL_ShowHideWindow(window):
    shown_flag = video.SDL_WINDOW_SHOWN
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowFlags(window) & shown_flag == shown_flag
    video.SDL_HideWindow(window)
    assert not video.SDL_GetWindowFlags(window) & shown_flag == shown_flag

def test_SDL_RaiseWindow(window):
    # NOTE: Doesn't set any flags, so can't test this super well
    video.SDL_RaiseWindow(window)

@pytest.mark.skip("Doesn't set the maximized flag for some reason")
def test_SDL_MaximizeWindow(decorated_window):
    # NOTE: May need to pump events for this to take effect?
    shown_flag = video.SDL_WINDOW_SHOWN
    max_flag = video.SDL_WINDOW_MAXIMIZED
    window = decorated_window
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowFlags(window) & shown_flag == shown_flag
    assert not video.SDL_GetWindowFlags(window) & max_flag == max_flag
    video.SDL_MaximizeWindow(window)
    if not DRIVER_DUMMY:
        assert video.SDL_GetWindowFlags(window) & max_flag == max_flag

def test_SDL_MinimizeRestoreWindow(decorated_window):
    shown_flag = video.SDL_WINDOW_SHOWN
    min_flag = video.SDL_WINDOW_MINIMIZED
    window = decorated_window
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowFlags(window) & shown_flag == shown_flag
    assert not video.SDL_GetWindowFlags(window) & min_flag == min_flag
    video.SDL_MinimizeWindow(window)
    if not DRIVER_DUMMY:
        assert video.SDL_GetWindowFlags(window) & min_flag == min_flag
    video.SDL_RestoreWindow(window)
    if not DRIVER_DUMMY:
        assert not video.SDL_GetWindowFlags(window) & min_flag == min_flag

def test_SDL_SetWindowFullscreen(with_sdl):
    # TODO: Add non-hidden test once annoying test toggle implemented
    flags = (
        video.SDL_WINDOW_BORDERLESS | video.SDL_WINDOW_HIDDEN,
        video.SDL_WINDOW_RESIZABLE | video.SDL_WINDOW_HIDDEN,
    )
    is_fullscreen = video.SDL_WINDOW_FULLSCREEN
    for flag in flags:
        window = video.SDL_CreateWindow(b"Test", 0, 0, 1024, 768, flag)
        video.SDL_SetWindowFullscreen(window, True)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & is_fullscreen == is_fullscreen
        video.SDL_SetWindowFullscreen(window, False)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & is_fullscreen != is_fullscreen
        video.SDL_DestroyWindow(window)

def test_SDL_GetWindowSurface(window):
    sf = video.SDL_GetWindowSurface(window)
    assert SDL_GetError() == b""
    assert isinstance(sf.contents, surface.SDL_Surface)

def test_SDL_UpdateWindowSurface(window):
    sf = video.SDL_GetWindowSurface(window)
    assert isinstance(sf.contents, surface.SDL_Surface)
    ret = video.SDL_UpdateWindowSurface(window)
    assert SDL_GetError() == b""
    assert ret == 0

def test_SDL_UpdateWindowSurfaceRects(window):
    sf = video.SDL_GetWindowSurface(window)
    assert isinstance(sf.contents, surface.SDL_Surface)
    rectlist = (rect.SDL_Rect * 4)(
        rect.SDL_Rect(0, 0, 0, 0),
        rect.SDL_Rect(10, 10, 10, 10),
        rect.SDL_Rect(0, 0, 5, 4),
        rect.SDL_Rect(-5, -5, 6, 2)
    )
    rect_ptr = cast(rectlist, POINTER(rect.SDL_Rect))
    ret = video.SDL_UpdateWindowSurfaceRects(window, rect_ptr, 4)
    assert SDL_GetError() == b""
    assert ret == 0

@pytest.mark.skip("Can't set window grab for some reason")
def test_SDL_GetSetWindowGrab(decorated_window):
    window = decorated_window
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowGrab(window) == SDL_FALSE
    video.SDL_SetWindowGrab(window, SDL_TRUE)
    assert video.SDL_GetWindowGrab(window) == SDL_TRUE
    video.SDL_SetWindowGrab(window, SDL_FALSE)
    assert video.SDL_GetWindowGrab(window) == SDL_FALSE

@pytest.mark.skip("Can't set window grab for some reason")
@pytest.mark.skipif(sdl2.dll.version < 2016, reason="not available")
def test_SDL_GetSetWindowKeyboardGrab(decorated_window):
    window = decorated_window
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowKeyboardGrab(window) == SDL_FALSE
    video.SDL_SetWindowKeyboardGrab(window, SDL_TRUE)
    assert video.SDL_GetWindowKeyboardGrab(window) == SDL_TRUE
    video.SDL_SetWindowKeyboardGrab(window, SDL_FALSE)
    assert video.SDL_GetWindowKeyboardGrab(window) == SDL_FALSE

@pytest.mark.skip("Can't set window grab for some reason")
@pytest.mark.skipif(sdl2.dll.version < 2016, reason="not available")
def test_SDL_GetSetWindowMouseGrab(decorated_window):
    window = decorated_window
    video.SDL_ShowWindow(window)
    assert video.SDL_GetWindowMouseGrab(window) == SDL_FALSE
    video.SDL_SetWindowMouseGrab(window, SDL_TRUE)
    assert video.SDL_GetWindowMouseGrab(window) == SDL_TRUE
    video.SDL_SetWindowMouseGrab(window, SDL_FALSE)
    assert video.SDL_GetWindowMouseGrab(window) == SDL_FALSE

@pytest.mark.skip("not implemented")
def test_SDL_GetGrabbedWindow(window):
    # NOTE: Should implement this once the above tests are fixed
    pass


# TODO: mostly covers positive tests right now - fix this!
class TestSDLVideo(object):
    __tags__ = ["sdl"]

    @pytest.mark.skipif(sdl2.dll.version < 2018, reason="not available")
    def test_SDL_GetSetWindowMouseRect(self):
        flags = video.SDL_WINDOW_BORDERLESS
        bounds_in = rect.SDL_Rect(0, 0, 100, 50)
        window = video.SDL_CreateWindow(b"Test", 200, 200, 200, 200, flags)
        # Try setting a mouse boundary
        ret = video.SDL_SetWindowMouseRect(window, byref(bounds_in))
        err = SDL_GetError()
        assert ret == 0
        bounds_out = video.SDL_GetWindowMouseRect(window)
        assert bounds_out != None
        assert bounds_in == bounds_out.contents
        # Try removing the boundary
        ret = video.SDL_SetWindowMouseRect(window, None)
        err = SDL_GetError()
        assert ret == 0
        bounds_out = video.SDL_GetWindowMouseRect(window)
        assert not bounds_out  # bounds_out should be null pointer
        video.SDL_DestroyWindow(window)

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GetSetWindowBrightness(self):
        flags = (video.SDL_WINDOW_BORDERLESS,
                 video.SDL_WINDOW_BORDERLESS | video.SDL_WINDOW_HIDDEN,
                 video.SDL_WINDOW_RESIZABLE | video.SDL_WINDOW_MINIMIZED)
        for flag in flags:
            window = video.SDL_CreateWindow(b"Test", 200, 200, 200, 200, flag)
            orig = video.SDL_GetWindowBrightness(window)
            assert isinstance(orig, float)
            # Go from 0.0, 0.1 ... to 1.0
            gammas = (x * 0.1 for x in range(0, 10))
            count = 0
            for b in gammas:
                ret = video.SDL_SetWindowBrightness(window, b)
                if ret == 0:
                    val = video.SDL_GetWindowBrightness(window)
                    assert round(abs(val-b), 7) == 0
                    count += 1
            assert count > 0
            video.SDL_DestroyWindow(window)

    @pytest.mark.skip("not implemented")
    def test_SDL_GetSetWindowGammaRamp(self):
        # SDL_SetWindowGammaRamp & SDL_GetWindowGammaRamp
        pass

    @pytest.mark.skip("not implemented")
    @pytest.mark.skipif(sdl2.dll.version < 2016, reason="not available")
    def test_SDL_FlashWindow(self):
        # Would need to be an interactive test
        pass

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_LoadUnloadLibrary(self):
        # Try the default library
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        video.SDL_GL_UnloadLibrary()

        if has_opengl_lib():
            fpath = get_opengl_path().encode("utf-8")
            assert video.SDL_GL_LoadLibrary(fpath) == 0, SDL_GetError()
            video.SDL_GL_UnloadLibrary()

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_GetProcAddress(self):
        if sys.platform != "darwin":
            procaddr = video.SDL_GL_GetProcAddress(b"glGetString")
            assert procaddr is None

        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()

        # Behaviour is undefined as long as there is no window and context.
        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)

        ctx = video.SDL_GL_CreateContext(window)

        procaddr = video.SDL_GL_GetProcAddress(b"glGetString")
        assert procaddr is not None and int(procaddr) != 0

        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

        if sys.platform != "darwin":
            procaddr = video.SDL_GL_GetProcAddress(b"glGetString")
            assert procaddr is None

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_ExtensionSupported(self):
        assert not video.SDL_GL_ExtensionSupported(b"GL_EXT_bgra")

        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)

        ctx = video.SDL_GL_CreateContext(window)

        assert video.SDL_GL_ExtensionSupported(b"GL_EXT_bgra")

        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

        assert not video.SDL_GL_ExtensionSupported(b"GL_EXT_bgra")

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_GetSetAttribute(self):
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()

        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)

        ctx = video.SDL_GL_CreateContext(window)

        depth = c_int()
        video.SDL_GL_GetAttribute(video.SDL_GL_DEPTH_SIZE, byref(depth))

        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)

        newdepth = 24
        if depth == 8:
            newdepth = 16
        elif depth == 16:
            newdepth = 24
        elif depth == 24:
            newdepth = 16
        video.SDL_GL_SetAttribute(video.SDL_GL_DEPTH_SIZE, newdepth)

        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)
        ctx = video.SDL_GL_CreateContext(window)

        val = c_int()
        video.SDL_GL_GetAttribute(video.SDL_GL_DEPTH_SIZE, byref(val))
        assert depth != val
        assert val.value >= newdepth
        # self.assertEqual(val.value, newdepth)

        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_CreateDeleteContext(self):
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)

        ctx = video.SDL_GL_CreateContext(window)
        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)

        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)
        ctx = video.SDL_GL_CreateContext(window)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_DeleteContext(ctx)
        video.SDL_GL_UnloadLibrary()

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_MakeCurrent(self):
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        window = video.SDL_CreateWindow(b"No OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_BORDERLESS)
        ctx = video.SDL_GL_CreateContext(window)
        video.SDL_GL_MakeCurrent(window, ctx)
        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_GetSetSwapInterval(self):
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)
        ctx = video.SDL_GL_CreateContext(window)
        video.SDL_GL_MakeCurrent(window, ctx)

        ret = video.SDL_GL_SetSwapInterval(0)
        if ret == 0:
            assert video.SDL_GL_GetSwapInterval() == 0
        ret = video.SDL_GL_SetSwapInterval(1)
        if ret == 0:
            assert video.SDL_GL_GetSwapInterval() == 1

        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_SwapWindow(self):
        assert video.SDL_GL_LoadLibrary(None) == 0, SDL_GetError()
        window = video.SDL_CreateWindow(b"OpenGL", 10, 10, 10, 10,
                                        video.SDL_WINDOW_OPENGL)
        ctx = video.SDL_GL_CreateContext(window)
        video.SDL_GL_MakeCurrent(window, ctx)
        video.SDL_GL_SwapWindow(window)
        video.SDL_GL_SwapWindow(window)
        video.SDL_GL_SwapWindow(window)
        video.SDL_GL_SwapWindow(window)
        video.SDL_GL_DeleteContext(ctx)
        video.SDL_DestroyWindow(window)
        video.SDL_GL_UnloadLibrary()

    @pytest.mark.skip("not implemented")
    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GL_ResetAttributes(self):
        pass

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_GetDisplayDPI(self):
        numdisplays = video.SDL_GetNumVideoDisplays()
        for index in range(numdisplays):
            ddpi, hdpi, vdpi = c_float(0), c_float(0), c_float(0)
            ret = video.SDL_GetDisplayDPI(index, byref(ddpi), byref(hdpi),
                                          byref(vdpi))
            assert ret == 0, SDL_GetError()
            assert ddpi.value >= 96.0
            assert hdpi.value >= 96.0
            assert vdpi.value >= 96.0

    @pytest.mark.skipif(DRIVER_DUMMY, reason="Doesn't work with dummy driver")
    def test_SDL_SetWindowResizable(self):
        window = video.SDL_CreateWindow(b"Resizable", 10, 10, 10, 10,
                                        video.SDL_WINDOW_RESIZABLE)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & video.SDL_WINDOW_RESIZABLE == video.SDL_WINDOW_RESIZABLE
        video.SDL_SetWindowResizable(window, SDL_FALSE)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & video.SDL_WINDOW_RESIZABLE != video.SDL_WINDOW_RESIZABLE
        video.SDL_SetWindowResizable(window, SDL_TRUE)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & video.SDL_WINDOW_RESIZABLE == video.SDL_WINDOW_RESIZABLE
        video.SDL_DestroyWindow(window)

    @pytest.mark.skip("Test doesn't work, may need to be interactive")
    @pytest.mark.skipif(sdl2.dll.version < 2016, reason="not available")
    def test_SDL_SetWindowAlwaysOnTop(self):
        ON_TOP_FLAG = video.SDL_WINDOW_ALWAYS_ON_TOP
        window = video.SDL_CreateWindow(b"Always On Top", 10, 10, 10, 10,
                                        video.SDL_WINDOW_ALWAYS_ON_TOP)
        video.SDL_ShowWindow(window)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & ON_TOP_FLAG == ON_TOP_FLAG
        video.SDL_SetWindowAlwaysOnTop(window, SDL_FALSE)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & ON_TOP_FLAG != ON_TOP_FLAG
        video.SDL_SetWindowAlwaysOnTop(window, SDL_TRUE)
        flags = video.SDL_GetWindowFlags(window)
        assert flags & ON_TOP_FLAG == ON_TOP_FLAG
        video.SDL_DestroyWindow(window)

    def test_SDL_GetSetWindowOpacity(self):
        window = video.SDL_CreateWindow(b"Opacity", 10, 10, 10, 10, 0)
        opacity = c_float()
        ret = video.SDL_GetWindowOpacity(window, byref(opacity))
        assert ret == 0
        assert opacity.value == 1.0
        if video.SDL_GetCurrentVideoDriver() != b"dummy":
            ret = video.SDL_SetWindowOpacity(window, 0.0)
            assert ret == 0, SDL_GetError()
            ret = video.SDL_GetWindowOpacity(window, byref(opacity))
            assert ret == 0
            assert opacity.value == 0.0
            ret = video.SDL_SetWindowOpacity(window, 0.653)
            assert ret == 0
            ret = video.SDL_GetWindowOpacity(window, byref(opacity))
            assert ret == 0
            assert round(abs(opacity.value-0.653), 2) == 0
        video.SDL_DestroyWindow(window)

    def test_SDL_GetDisplayUsableBounds(self):
        numdisplays = video.SDL_GetNumVideoDisplays()
        for index in range(numdisplays):
            bounds = rect.SDL_Rect()
            ret = video.SDL_GetDisplayUsableBounds(index, byref(bounds))
            assert ret == 0
            assert not rect.SDL_RectEmpty(bounds)

    def test_SDL_GetWindowBordersSize(self):
        # Create/show a window, make sure all borders are >= 0
        window = video.SDL_CreateWindow(b"Borders", 10, 10, 10, 10, 0)
        video.SDL_ShowWindow(window)
        t, l, b, r = c_int(), c_int(), c_int(), c_int()
        ret = video.SDL_GetWindowBordersSize(
            window, byref(t), byref(l), byref(b), byref(r)
        )
        video.SDL_DestroyWindow(window)
        values = [x.value for x in (t, l, b, r)]
        assert all([v >= 0 for v in values])

        # Currently, only X11 and Windows video drivers support border size
        supports_borders = [b"x11", b"windows"]
        if video.SDL_GetCurrentVideoDriver() in supports_borders:
            assert ret == 0

        # Test again with a borderless window & make sure borders are all 0
        window = video.SDL_CreateWindow(
            b"No Borders", 10, 10, 10, 10, video.SDL_WINDOW_BORDERLESS
        )
        video.SDL_ShowWindow(window)
        ret = video.SDL_GetWindowBordersSize(
            window, byref(t), byref(l), byref(b), byref(r)
        )
        video.SDL_DestroyWindow(window)
        values = [x.value for x in (t, l, b, r)]
        assert all([v == 0 for v in values])
        if video.SDL_GetCurrentVideoDriver() in supports_borders:
            assert ret == 0
        

    @pytest.mark.skip("not implemented")
    def test_SDL_SetWindowModalFor(self):
        pass

    @pytest.mark.skip("not implemented")
    def test_SDL_SetWindowInputFocus(self):
        pass
