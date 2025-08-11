try:
    from suzaku import *
except:
    raise ModuleNotFoundError(
        "Suzaku module not found! Install suzaku or run with python3 -m suzaku in parent dir."
    )
import glfw
import skia

if __name__ == "__main__":
    # 修改主窗口创建代码
    app = SkApp(window_event_wait=False, draw_on_focus=False)

    def create1window():
        window = SkWindow(
            app,
            title="Suzaku GUI",
            size=(280, 460),
            force_hardware_acceleration=True,  # overrideredirect=True,
        )
        # print(glfw.default_window_hints())
        window.bind("closed", lambda evt: print("SkWindowBase closed"))
        window.bind("drop", lambda evt: print("drop", evt))

        SkTextButton(
            window, text="This is a SkButton / 这是一个按钮", command=window.restore
        ).box(padx=10, pady=10)
        text = SkText(window, text="This is a SkLabel / 这是一个标签").box(
            padx=10, pady=10
        )

        var = SkStringVar()
        SkEntry(window, placeholder="数值绑定", textvariable=var).box(padx=10, pady=10)
        SkText(window, textvariable=var).box(padx=10, pady=10)
        SkTextButton(window, text="Close the window", command=window.destroy).box(
            side="bottom"
        )
        SkTextButton(window, text="Create 1 Window", command=create1window).box(
            padx=10, pady=10, side="bottom"
        )

    # create1window()
    create1window()

    app.run()
