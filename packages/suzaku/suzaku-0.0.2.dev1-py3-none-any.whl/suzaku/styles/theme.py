from __future__ import annotations as _

import json
import os
import pathlib
import re
import typing
import warnings

if typing.TYPE_CHECKING:
    from ..widgets.widget import SkWidget


class SkStyleNotFoundError(NameError):
    pass


class SkTheme:

    loaded_themes: list["SkTheme"] = []
    INTERNAL_THEME_DIR = pathlib.Path(__file__).parent.parent / "resources" / "themes"
    INTERNAL_THEMES: dict[str, "SkTheme"] = {}
    DEFAULT_THEME: "SkTheme"
    DEFAULT_THEME_FILENAME: str = "light"

    @classmethod
    def _load_internal_themes(cls):
        # Load default (ROOT) theme
        SkTheme.DEFAULT_THEME = SkTheme({}).load_from_file(
            SkTheme.INTERNAL_THEME_DIR / f"{SkTheme.DEFAULT_THEME_FILENAME}.json"
        )

        # Load other internal themes
        for file in os.listdir(SkTheme.INTERNAL_THEME_DIR):
            if file == f"{SkTheme.DEFAULT_THEME_FILENAME}.json":
                # For default theme, no need to reload it
                SkTheme.INTERNAL_THEMES[SkTheme.DEFAULT_THEME.name] = (
                    SkTheme.DEFAULT_THEME
                )
                continue
            _ = SkTheme({}).load_from_file(SkTheme.INTERNAL_THEME_DIR / file)
            SkTheme.INTERNAL_THEMES[_.name] = _

    @classmethod
    def find_loaded_theme(cls, theme_name: str) -> "SkTheme | typing.Literal[False]":
        """Search for a loaded theme by name, returns the SkTheme object if found, or False if not.

        Example
        -------
        .. code-block:: python
            default_theme = SkTheme.find_loaded_theme("default.light")
        This returns the SkTheme object of the default theme to `default_theme`.

        :param theme_name: Name of the theme to load
        :return: The SkTheme object if found, otherwise False
        """
        for theme in cls.loaded_themes:
            if theme.name == theme_name:
                return theme
        return False

    @classmethod
    def validate_theme_existed(cls, theme_name: str) -> bool:
        """Validate if the theme with given name existed and loaded.

        Example
        -------
        .. code-block:: python
            SkTheme.validate_theme_existed("default.light")
        This returns if the theme `default.light` is loaded.

        :param theme_name: Name of the theme to validate
        :return: If the theme loaded
        """
        return SkTheme.find_loaded_theme(theme_name) != False  # ☝🤓

    def __init__(
        self, styles: dict | None = None, parent: typing.Union["SkTheme", None] = None
    ) -> None:
        """Theme for SkWindow and SkWidgets.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme({<Some styles>})
            my_sub_theme = SkTheme(parent="default.light")
            my_external_theme = SkTheme().load_from_file("./path/to/a/theme.json")
        This shows examples of creating themes, either from a json, a parent theme or a file.

        :param styles: Styles of the theme
        :param parent: Parent theme
        """

        self.styles: dict = styles
        if styles is None:
            self.styles: dict = SkTheme.DEFAULT_THEME.styles

        self.name: str = f"untitled.{len(SkTheme.loaded_themes) + 1}"
        self.friendly_name = f"Untitled theme {len(SkTheme.loaded_themes) + 1}"
        # friendly_name感觉有点多余? ——Little White Cloud
        # Keep it 4 now currently. ——rgzz666
        self.parent: typing.Union["SkTheme", None] = parent

        SkTheme.loaded_themes.append(self)  # TODO: figure out.
        return

    def load_from_file(self, file_path: typing.Union[str, pathlib.Path]) -> "SkTheme":
        """Load styles to theme from a file.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_from_file("./path/to/a/theme.json")
            my_theme.load_from_file("./path/to/another/theme.json")
        This shows loading a theme to `my_theme` from the theme file at `./path/to/a/theme.json`,
        and change it to theme from `./path/to/another/theme.json` later.

        :param file_path: Path to the theme file
        :return self: The SkTheme itself
        """

        with open(file_path, mode="r", encoding="utf-8") as f:
            style_raw = f.read()
            theme_data = json.loads(style_raw)
            if (
                search_result := SkTheme.find_loaded_theme(theme_data["name"])
            ) != False:
                warnings.warn(
                    f"Theme <{theme_data["name"]}> already loaded or existed."
                )
                return search_result

        return self.load_from_json(theme_data)

    def load_from_json(self, theme_data: dict) -> "SkTheme":
        """Load all data (including matadata) to the theme.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_from_json({<Some JSON theme data>})
            my_theme.load_from_json({<Some JSON theme data>})
        This shows loading a theme to `my_theme` from json data, and change it to theme from
        another json later.

        :param theme_data: dict that contains the theme data
        :return self: The SkTheme itself
        """
        self.styles = theme_data["styles"]

        self.rename(theme_data["name"], theme_data["friendly_name"])
        self.set_parent(theme_data["base"])

        return self

    def load_styles_from_json(self, style_json: dict) -> "SkTheme":
        """Load styles to theme from a given dict.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_styles_from_json({<Some styles>})
            my_theme.load_from_json({<Some styles>})
        This shows loading styles data to `my_theme` from json data, and change its styles from
        that stored in another json later.

        :param style_json: dict that contains the styles
        :return self: The SkTheme itself
        """
        self.styles = style_json
        return self

    def set_parent(self, parent_name: str) -> "SkTheme":
        """Set the parent for the theme via string stored in theme json.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().set_parent("DEFAULT")
            my_theme.set_parent("default.dark")
        The first line shows setting the parent of `my_theme` to the default theme, which is
        suggested for third-party themes that act as a root. The second line shows setting the
        parent of `my_theme` to `default.dark` after its creation.

        Parent Name
        -----------
        - `ROOT` means the theme does not have a parent. This is not recommended for third-party
          themes, use `DEFAULT` instead.
        - `DEFAULT` means the parent of the theme is the default internal theme.

        If the parent name is none of above, it should be the theme of the name and will be set as
        parent directly. However, if the theme specified is not yet loaded, parent will fall back
        to `DEFAULT`.

        :param parent_name: Name of the parent
        :return self: The SkTheme itself
        """
        match parent_name:
            case "ROOT":
                self.parent = None
            case "DEFAULT":
                self.parent = self.DEFAULT_THEME
            case _:
                search_result = SkTheme.find_loaded_theme(parent_name)
                if search_result != False:
                    self.parent = search_result
                else:
                    warnings.warn(
                        f"Parent theme specified with name <{parent_name}> is not yet loaded. "
                        "Will fall back to <DEFAULT> for parent instead."
                    )
                    self.set_parent("DEFAULT")
        return self

    def rename(self, new_name: str, friendly_name: str) -> "SkTheme":
        """Rename the theme.

        Example
        -------
        .. code-block:: python
            my_theme = Theme().rename("theme.name")
            my_theme.rename("i_hate.that_name")
        This shows renaming `my_theme` to `theme.name`, and renaming it to `i_hate.that_name` after
        its creaton.

        :param new_name: The new name for the theme
        :return self: The SkTheme itself
        """
        if not SkTheme.validate_theme_existed(new_name):
            self.name = new_name
            self.friendly_name = friendly_name  # 🤔
        else:
            warnings.warn(
                f"Theme name <{new_name}> occupied. Rename for <{self.name}> is canceled."
            )
        return self

    def select(self, selector: str) -> list:
        """Parse styles selector.

        This is a selector parser mainly used by internal functions.

        Example
        -------
        See -> :func:`get_style` in source code.

        Selector
        --------
        - `<Widget>` indicates the styles of Widget at rest state, e.g. `SkButton`.
        - `<Widget>:<state>` indicates the styles of the state of Widget, e.g. `SkButton:hover`.
        - `<Widget>:ITSELF` indecates the styles of the widget, e.g. `SkButton.ITSELF`.
          Note that this is not available everywhere.

        :param selector: The selector string
        :return: Parsed selector, levels in a list
        """
        # Validation
        if not re.match("[a-zA-Z0-9-_.:]", selector):
            raise ValueError(f"Invalid styles selector [{selector}].")
        # Handling
        if ":" in selector:
            result = selector.split(":")
            if len(result) > 2:  # Validation
                raise ValueError(f"Invalid styles selector [{selector}].")
            if result[1] == "ITSELF":
                result = [result[0]]
        else:
            result = [selector, "rest"]

        # Check if the widget is not in the widgets list
        # Also check if the state is not in the widget's states
        if (
            result[0] not in self.styles.keys()
            or result[1] not in self.styles[result[0]].keys()
        ):
            raise SkStyleNotFoundError(f"Cannot find styles with selector [{selector}]")
        return result

    def get_style(self, selector: str, copy: bool = True) -> dict:
        """Get styles config using a selector.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_style = my_theme.get_style("SkButton:hover")
            my_theme.get_style("SkButton:hover", copy=False)["background"] = (255, 0, 0, 255)
        This shows getting style json of SkButton at hover state and setting its background to red.

        :param selector: The selector string, indicating which styles to get
        :param copy: Whether to copy a new styles json, otherwise returns the styles itself
        :return result: The style dict
        """
        result = self.styles
        if not selector:
            result = self.styles
        else:
            try:
                selector_parsed = self.select(selector)
            except SkStyleNotFoundError:
                if self.name == SkTheme.DEFAULT_THEME.name:
                    raise SkStyleNotFoundError(
                        "Style is not exsited in the default theme. Check your selector!"
                    )
                return default_theme.get_style(selector, copy=True)

            for selector_level in selector_parsed:
                # e.g. result = stlyes["SkButton"]
                # result = styles["SkButton"]["hover"]
                result = result[selector_level]

        if copy:
            return result.copy()
        else:
            return result

    def get_style_attr(self, selector: str, attr_name: str) -> typing.Any:
        """Get style attribute value.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            button_background = my_theme.get_style_attr("SkButton:rest", "background")
        This shows getting the value of `background` attribute from styles of `SkButton` at `rest`
        state.

        Fallback Machanism
        ------------------
        - The program first tries to get attribute from the style indicated by the selector.
        - If fails, which means that the attribute cannot be found, the program tries to fallback
          to the base state of the target state, which is specified with `"base": "<State name>"`.
        - If still fails, fallback to the rest state.
        - If still, which means that the attribute is not specified in the current theme, the
          program will try the parent theme, then the parent of parent theme, and repeat this until
          it reaches the default theme (or more accurately, the root theme).
        - As the root theme must contain all attributes available, if the selector or attribute
          still cannot be found even in root theme, the program throws an error.

        :param selector: The selector to the style
        :param attr_name: The attribute name
        :return: The attribute value
        """
        style = self.get_style(selector, copy=False)
        if attr_name not in style:
            # Fallback machanism
            # Fallback to base or rest state and try
            if self.select(selector)[-1] != "rest":
                new_selector = self.select(selector)
                new_selector[-1] = "rest" if "base" not in style else style["base"]
                return self.get_style_attr(selector, attr_name)
            # If still fails, fallback to parent
            if self.parent is not None:
                self.parent.get_style_attr(selector, attr_name)
            elif self.parent is None and self.name != SkTheme.DEFAULT_THEME.name:
                SkTheme.DEFAULT_THEME.get_style_attr(selector, attr_name)
            # If is already default theme (no parent), then go fuck your selector
            if self.name == SkTheme.DEFAULT_THEME.name:
                raise SkStyleNotFoundError(
                    "Style is not exsited in the default theme. Check your selector!"
                )

        return style[attr_name]

    def mixin(self, selector: str, new_style: dict, copy: bool = False) -> "SkTheme":
        """Mix, or in other words, override custom styles into the theme.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_theme.mixin("SkButton.ITSELF", {"rest": {"background": (255, 0, 0, 255)},
                                               "hover": {"background": (0, 0, 255, 255)}})
            my_subtheme = my_theme.mixin("SkButton:hover", {"background": (255, 0, 0, 255)},
                                         copy=True)
        The first line shows mixing in a red background style at rest state and a blue background
        style at hover state into SkButton. The second line shows creating a subtheme base on
        `my_theme`, but with red background for `SkButton` at `hover` state.

        :param selector: The selector string, indicates where to mix in
        :param new_style: A styles json, to be mixed in
        :param copy: Whether to copy a new theme, otherwise modify the current object
        :return theme_operate: The edited theme object, either self of copy of self
        """
        if copy:
            theme_operate = SkTheme(self.styles)
        else:
            theme_operate = self
        style_operate = theme_operate.get_style(selector, copy=False)
        style_operate.update(new_style)
        return theme_operate

    def special(self, selector: str, **kwargs) -> "SkTheme":
        """Create a sub-theme with few modifications on the theme.

        Can be used when applying custom styles on a specific widget.

        Example
        -------
        .. code-block:: python
            SkButton(window, styles=my_theme.special(background=(255, 0, 0, 255)))
        This shows setting a `SkButton`'s style base on `my_theme`, but with background red.

        :param selector: The selector string, indicates where to mix in
        :param **kwargs: Styles to change
        :return new_theme: The modified SkTheme object
        """
        if "ITSELF" in selector:
            warnings.warn(
                "<SkWidget.ITSELF> is not supported by SkTheme.special()! "
                "It will be regarded as <SkWidget.rest>"
            )
            selector = selector.replace("ITSELF", "rest")
        new_theme = SkTheme(self.styles, parent=self)
        style_operate = new_theme.get_style(selector, copy=False)
        style_operate.update(kwargs)
        return new_theme

    def apply_on(self, widget: SkWidget) -> SkTheme:
        """Apply theme on a widget.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_button = SkButton(my_window, text="Hello world")
            my_theme.apply_on(my_button)
        This shows applying theme on a `SkButton`

        :param widget: The widget to apply theme to
        :return self: The theme itself
        """
        widget.apply_theme(self)
        return self


# Load internal themes
SkTheme._load_internal_themes()

# Alias for defualt theme
default_theme = SkTheme.DEFAULT_THEME
