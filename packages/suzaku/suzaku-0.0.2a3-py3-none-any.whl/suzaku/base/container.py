import warnings

from ..event import SkEvent


class SkLayoutError(TypeError):
    pass


class SkContainer:

    # region __init__ 初始化

    def __init__(self, pos: tuple[int, int] = (0, 0), size: tuple[int, int] = (0, 0)):
        """A SkContainer represents a widget that has the ability to contain other widgets inside.

        SkContainer is only for internal use. If any user would like to create a widget from
        several of existed ones, they should use SkComboWidget instead. The authors will not
        guarantee the stability of inheriting SkContainer for third-party widgets.

        SkContainer class contains code for widget embedding, and layout handling, providing the
        ability of containing `children` to widgets inerit from it. All other classes with such
        abilities should be inherited from SkContainer.

        SkContainer has a `children` list, each item is a `SkWidget`, called `child`. This helps
        the SkContainer knows which `SkWidget`s it should handle.

        SkContainer has a `draw_list` that stores all widgets contained in it that should be drawn.
        They are separated into a few layers which are listed below, in the order of from behind to
        the top:

        1. `Layout layer`: The layer for widgets using pack or grid layout.
        2. `Floating layer`: The layer for widgets using place layout.
        3. `Fixed layer`: The layer for widgets using fixed layout.

        In each layer, items will be drawn in the order of index. Meaning that those with lower
        index will be drawn first, and may get covered by those with higher index. Same for layers,
        layers with higher index cover those with lower index.

        :param pos: The coordinates of the container in tuple (x, y), default is (0, 0)
        :param size: Size of the container, in tuple (width, height), default is (0, 0)
        """
        # self.parent = None
        self.children = []  # Children

        from ..widgets.widget import SkWidget

        self.draw_list: list[list[SkWidget]] = [
            [],  # Layout layer [SkWidget1, SkWidget2, ...]
            [],  # Floating layer [SkWidget1, SkWidget2, ...]
            [],  # Fixed layer [SkWidget1, SkWidget2, ...]
        ]
        # self.layers_layout_type = ["none" for i in range(len(self.draw_list))]  # ['none', 'none', 'none']

        self._box_direction = None  # h(horizontal) or v(vertical)

        self.bind("resize", self._handle_layout)

        if isinstance(self, SkWidget):

            def children_resize(event: SkEvent):
                for child in self.children:
                    child.event_generate("resize", event)

            self.bind("resize", children_resize)

        if not hasattr(self, "x"):
            self.x = pos[0]
            self.y = pos[1]
            self.width = size[0]
            self.height = size[1]

    # endregion

    # region add_child 添加子元素
    def add_child(self, child):
        """Add child widget to window.

        :param child: The child to add
        """
        from .appbase import SkAppBase

        if not isinstance(self.parent, SkAppBase):
            self.parent.add_child(child)
        self.children.append(child)

    def add_layout_child(self, child):
        """Add layout child widget to window.

        :arg child: SkWidget
        :return: None
        """
        layout_config = child.layout_config

        if "box" in layout_config:
            side = layout_config["box"]["side"]
            if side == "left" or side == "right":
                direction = "h"
            elif side == "top" or side == "bottom":
                direction = "v"
            else:
                raise ValueError("Box layout side must be left, right, top or bottom.")

            if self._box_direction == "v":
                if direction == "h":
                    raise ValueError(
                        "Box layout can only be used with vertical direction."
                    )
            elif self._box_direction == "h":
                if direction == "v":
                    raise ValueError(
                        "Box layout can only be used with horizontal direction."
                    )
            else:
                self._box_direction = direction

        self.draw_list[0].append(child)
        self._handle_layout()

    def add_floating_child(self, child):
        """Add floating child widget to window.

        :arg child: SkWidget
        :return: None
        """
        self.draw_list[1].append(child)
        self._handle_layout()

    def add_fixed_child(self, child):
        """Add fixed child widget to window.

        :arg child: SkWidget
        :return: None
        """
        self.draw_list[2].append(child)
        self._handle_layout()

    # endregion

    # region draw 绘制

    def draw_children(self, canvas):
        """Draw children widgets.

        :param canvas: The canvas to draw on
        :return: None
        """
        for layer in self.draw_list:
            for child in layer:
                if child.visible:
                    child.draw(canvas)

    # endregion

    # region layout 布局

    def update_layout(self):
        self._handle_layout()

    def _handle_layout(self, evt=None):
        """Handle layout of the container.

        :return: None
        """
        """for child in self.children:
            if child.visible:
                layout_type = list(child.layout_config.keys())[0]
                # Build draw_item dict
                draw_item = {
                    "widget": child,
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0,
                }
                # Sort children
                match layout_type:
                    case "none":
                        continue
                    case "pack" | "box" | "grid":  # -> Layout layer
                        if self.layers_layout_type[0] == "none":
                            self.layers_layout_type[0] = layout_type
                        elif self.layers_layout_type[0] != layout_type:
                            raise SkLayoutError("Layout layer can only contain no more than " + \
                                                f"one layout type. Not {layout_type} with " + \
                                                f"{self.layers_layout_type[0]} which is existed.")
                        self.draw_list[0].append(draw_item)
                    case "place":  # -> Floating layer
                        if self.layers_layout_type[1] != "place":
                            self.layers_layout_type[1] = layout_type
                        self.draw_list[1].append(draw_item)
                    case "fixed":  # -> Fixed layer
                        if self.layers_layout_type[2] != "fixed":
                            self.layers_layout_type[2] = layout_type
                        self.draw_list[2].append(draw_item)

        # Process layouts
        for layout_type in self.layers_layout_type:
            if layout_type != "none":
                getattr(self, f"_handle_{layout_type}")(event)
        # self._handle_fixed()"""
        for layer in self.draw_list:
            for child in layer:
                if child.visible:
                    match child.layout_config:
                        case {"place": _}:
                            pass
                        case {"box": _}:
                            self._handle_box()
                            break
                        case {"fixed": _}:
                            self._handle_fixed(child)

    def _handle_pack(self):
        pass

    def _handle_place(self):
        pass

    def _handle_grid(self):
        pass

    def _handle_box(self) -> None:
        """Process box layout.

        :return: None
        """

        from ..widgets.widget import SkWidget

        if isinstance(self, SkWidget):
            x = self.x
            y = self.y
        else:
            x = 0
            y = 0
        width = self.width  # container width
        height = self.height  # container height
        start_children: list[SkWidget] = []  # side="top" or "left" children
        end_children: list[SkWidget] = []  # side="bottom" or "right" children
        expanded_children: list[SkWidget] = []  # expand=True children
        fixed_children: list[SkWidget] = []  # expand=False children
        children: list[SkWidget] = self.draw_list[0]  # Components using the Box layout

        # Iterate through all the subcomponents first, categorize them, and separate components with different values for expand, side.
        # 先遍历一遍所有子组件，将它们分类，将expand、side值不同的组件分开
        for child in children:
            layout_config = child.layout_config
            match layout_config["box"]["side"].lower():
                case "top" | "left":
                    start_children.append(child)
                case "bottom" | "right":
                    end_children.append(child)
            if layout_config["box"]["expand"]:
                expanded_children.append(child)
            else:
                fixed_children.append(child)

        # Horizontal Layout
        if self._box_direction == "h":
            # Calculate the width of the fixed children
            fixed_width: int | float = 0  # Occupied width of all fixed widgets enabled
            for fixed_child in fixed_children:
                fixed_child_layout_config = fixed_child.layout_config["box"]

                if type(fixed_child_layout_config["padx"]) is tuple:
                    fixed_width += fixed_child_layout_config["padx"][0]
                else:
                    fixed_width += fixed_child_layout_config["padx"]
                fixed_width += fixed_child.width

                if type(fixed_child_layout_config["padx"]) is tuple:
                    fixed_width += fixed_child_layout_config["padx"][1]
                else:
                    fixed_width += fixed_child_layout_config["padx"]

            if len(expanded_children):
                expanded_width = (width - fixed_width) / len(expanded_children)
            else:
                expanded_width = 0

            # Left side
            last_child_left_x = 0
            for child in start_children:
                if type(child.layout_config["box"]["padx"]) is tuple:
                    left = child.layout_config["box"]["padx"][0]
                    right = child.layout_config["box"]["padx"][1]
                else:
                    left = right = child.layout_config["box"]["padx"]

                if type(child.layout_config["box"]["pady"]) is tuple:
                    top = child.layout_config["box"]["pady"][0]
                    bottom = child.layout_config["box"]["pady"][1]
                else:
                    top = bottom = child.layout_config["box"]["pady"]

                if not child.layout_config["box"]["expand"]:
                    child.width = child.cget("dheight")
                else:
                    child.width = expanded_width - left - right
                child.height = height - top - bottom
                child.x = last_child_left_x + left
                child.y = top
                last_child_left_x = child.x + child.width + right

            # Right side
            last_child_right_x = width
            for child in end_children:
                if type(child.layout_config["box"]["padx"]) is tuple:
                    left = child.layout_config["box"]["padx"][0]
                    right = child.layout_config["box"]["padx"][1]
                else:
                    left = right = child.layout_config["box"]["padx"]

                if type(child.layout_config["box"]["pady"]) is tuple:
                    top = child.layout_config["box"]["pady"][0]
                    bottom = child.layout_config["box"]["pady"][1]
                else:
                    top = bottom = child.layout_config["box"]["pady"]

                if not child.layout_config["box"]["expand"]:
                    child.width = child.cget("dheight")
                else:
                    child.width = expanded_width - left - right
                child.height = height - top - bottom
                child.x = last_child_right_x - child.width - right
                child.y = top
                last_child_right_x = last_child_right_x - child.width - left * 2
        else:  # Vertical Layout
            # Calculate the height of the fixed children
            fixed_height = 0  # Occupied height of all fixed widgets enabled
            for fixed_child in fixed_children:
                fixed_child_layout_config = fixed_child.layout_config["box"]

                if type(fixed_child_layout_config["pady"]) is tuple:
                    fixed_height += fixed_child_layout_config["pady"][0]
                else:
                    fixed_height += fixed_child_layout_config["pady"]
                fixed_height += fixed_child.height

                if type(fixed_child_layout_config["pady"]) is tuple:
                    fixed_height += fixed_child_layout_config["pady"][1]
                else:
                    fixed_height += fixed_child_layout_config["pady"]

            if len(expanded_children):
                expanded_height = (height - fixed_height) / len(
                    expanded_children
                )  # Height of expanded children
            else:
                expanded_height = 0

            last_child_bottom_y = 0  # Last bottom y position of the child component
            for child in start_children:  # Top side
                child_layout_config = child.layout_config["box"]
                if type(child_layout_config["padx"]) is tuple:
                    left = child_layout_config["padx"][0]
                    right = child_layout_config["padx"][1]
                else:
                    left = right = child_layout_config["padx"]

                if type(child_layout_config["pady"]) is tuple:
                    top = child_layout_config["pady"][0]
                    bottom = child_layout_config["pady"][1]
                else:
                    top = bottom = child_layout_config["pady"]

                child.width = width - left - right
                if not child_layout_config["expand"]:
                    child.height = child.cget("dheight")
                else:
                    child.height = expanded_height - top - bottom
                child.x = x + left
                child.y = y + last_child_bottom_y + top
                last_child_bottom_y = child.y + child.height + bottom

            last_child_top_y = height  # Last top y position of the child component
            for child in end_children:  # Bottom side
                child_layout_config = child.layout_config["box"]
                if type(child_layout_config["padx"]) is tuple:
                    left = child_layout_config["padx"][0]
                    right = child_layout_config["padx"][1]
                else:
                    left = right = child_layout_config["padx"]

                if type(child_layout_config["pady"]) is tuple:
                    top = child_layout_config["pady"][0]
                    bottom = child_layout_config["pady"][1]
                else:
                    top = bottom = child_layout_config["pady"]

                child.width = width - left - right
                if not child_layout_config["expand"]:
                    child.height = child.cget("dheight")
                else:
                    child.height = expanded_height - top - bottom
                child.x = x + left
                child.y = y + last_child_top_y - child.height - bottom
                last_child_top_y = last_child_top_y - child.height - top * 2

    def _handle_fixed(self, child):
        """Process fixed layout.

        :param child: The child widget
        """
        from ..widgets.window import SkWindow

        if isinstance(self, SkWindow):
            x = y = 0
        else:
            x = self.x, y = self.y
        child.x = child.layout_config["fixed"]["x"] + x
        child.y = child.layout_config["fixed"]["y"] + y
        child.width = child.layout_config["fixed"]["width"]
        child.height = child.layout_config["fixed"]["height"]

    # endregion

    # region other 其他
    def bind(self, *args, **kwargs):
        raise RuntimeError(
            "Anything inherited from SkContainer should support binding events!"
            + "This error should be overrode by the actual bind function of "
            + "SkWindow or SkWidget in normal cases."
        )

    # endregion
