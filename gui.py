#
# gui.py
# Classes for each element of the GUI
#

import textwrap
import libtcodpy as libt
import config
import data


class GUIElement(object):
    """Base class for GUI elements."""
    def __init__(self):
        pass

    def draw(self):
        pass


class Border(GUIElement):
    """Border that surrounds the GUI."""
    def __init__(self):
        GUIElement.__init__(self)

    def objects_under_mouse(self):
        """Returns list of entities that mouse is hovering over."""
        x = self.handler.mouse.cx
        y = self.handler.mouse.cy
        names = []

        # Names of mobs
        for entity in self.handler.map_objects['mobs']:
            if (entity.x == x and entity.y == y and 
                libt.map_is_in_fov(self.handler.fov_map, entity.x, entity.y)):
                if entity.state == data.DEAD:
                    names.append(entity.name)
                else:
                    names.append("{} [{}/{}]".format(entity.name, entity.hp, entity.max_hp))

        # Names of items
        for item in self.handler.map_objects['items']:
            if (item.x == x and item.y == y and
                libt.map_is_in_fov(self.handler.fov_map, item.x, item.y)):
                names.append(item.name)

        names = ", ".join(names)
        return names

    def draw(self):
        """Draws borders around the info panel."""
        libt.console_set_default_background(self.handler.gui, data.COLOURS['gui_bg'])
        libt.console_clear(self.handler.gui)

        upper_height = config.BORDER_WIDTH / 2
        left_height = config.GUI_HEIGHT - upper_height*2

        libt.console_set_default_background(self.handler.gui, data.COLOURS['gui_border'])
        # Upper border
        libt.console_rect(self.handler.gui, 0, 0, config.GUI_WIDTH, upper_height, 
                          False, libt.BKGND_SCREEN)
        # Lower border
        libt.console_rect(self.handler.gui, 0, config.GUI_HEIGHT - config.BORDER_WIDTH/2,  
                          config.GUI_WIDTH, upper_height, False, libt.BKGND_SCREEN)
        # Left border
        libt.console_rect(self.handler.gui, 0, upper_height, config.BORDER_WIDTH / 2, 
                          left_height, False, libt.BKGND_SCREEN)
        # Right border
        libt.console_rect(self.handler.gui, config.GUI_WIDTH - config.BORDER_WIDTH/2, upper_height, 
                          config.BORDER_WIDTH / 2, left_height, False, libt.BKGND_SCREEN)
        # Middle border
        libt.console_rect(self.handler.gui, (config.GUI_WIDTH - 1)/2 - config.BORDER_WIDTH/2, upper_height, 
                          config.BORDER_WIDTH, left_height, False, libt.BKGND_SCREEN)

        # Hover details
        libt.console_set_default_foreground(self.handler.gui, data.COLOURS['text'])
        libt.console_print_ex(self.handler.gui, (config.GUI_WIDTH - 1)/2, 0,
                              libt.BKGND_NONE, libt.CENTER, self.objects_under_mouse())


class StatusBar(GUIElement):
    """
    Class for status bars.

    x: x-coordinate of the bar
    y: y-coordinate of the bar
    name: name displayed for the bar
    val: current value out of the maximum
    max_val: the largest value the bar can contain
    bar_colour: colour of the bar portion that is filled
    back_colour: colour of the bar portion that is unfilled
    """
    def __init__(self, x, y, name, val, max_val, bar_colour, back_colour):
        GUIElement.__init__(self)
        self.x = x
        self.y = y
        self.name = name
        self.val = val
        self.max_val = max_val
        self.bar_colour = bar_colour
        self.back_colour = back_colour

    def draw(self):
        """
        Creates a bar that shows the current value 
        out of the given maximum.
        """
        filled_width = int(float(self.val) / self.max_val * config.BAR_WIDTH)

        libt.console_set_default_background(self.handler.gui, self.back_colour)
        libt.console_rect(self.handler.gui, self.x, self.y, config.BAR_WIDTH, config.BAR_HEIGHT, 
                          False, libt.BKGND_SCREEN)

        libt.console_set_default_background(self.handler.gui, self.bar_colour)
        if filled_width > 0:
            libt.console_rect(self.handler.gui, self.x, self.y, filled_width, config.BAR_HEIGHT, 
                              False, libt.BKGND_SCREEN)

        bar_midpoint = (int(config.BAR_WIDTH/2 + self.x), int(config.BAR_HEIGHT/2 + self.y))

        libt.console_set_default_foreground(self.handler.gui, data.COLOURS['text'])
        libt.console_print_ex(self.handler.gui, bar_midpoint[0], bar_midpoint[1], 
                              libt.BKGND_NONE, libt.CENTER,
                              "{}: {}/{}".format(self.name, self.val, self.max_val))

        libt.console_set_default_foreground(self.handler.gui, data.COLOURS['text'])


class HealthBar(StatusBar):
    """The health bar."""
    def __init__(self):
        StatusBar.__init__(self, config.BORDER_WIDTH, config.BORDER_WIDTH, "HP", 
                           self.handler.player.hp, self.handler.player.max_hp, 
                           data.COLOURS['bar_hp'], data.COLOURS['bar_hp_unfilled'])


class MessageBox(GUIElement):
    """Messages are displayed here."""
    def __init__(self):
        GUIElement.__init__(self)
        self.messages = []
        self.max_messages = config.MSG_HEIGHT - config.BORDER_WIDTH

    def add_msg(self, msg, colour=data.COLOURS['text']):
        """Adds a message to the message box."""
        wrapped = textwrap.wrap(msg, config.MSG_WIDTH - config.BORDER_WIDTH*2)

        for line in wrapped:
            if len(self.messages) == self.max_messages:
                del self.messages[0]
            self.messages.append((line, colour))

    def draw(self):
        """Draws messages in the message box."""
        y = config.BORDER_WIDTH
        for (msg, colour) in self.messages:
            libt.console_set_default_foreground(self.handler.gui, colour)
            libt.console_print_ex(self.handler.gui, config.MSG_WIDTH - 1 + config.BORDER_WIDTH, y, 
                                  libt.BKGND_NONE, libt.LEFT, msg)
            y += 1


class Overlay(GUIElement):
    """
    Base class for anything that pops up over the game screen.
    Requires that the given header is exactly one line high.

    header: title of the overlay
    header_align: alignment of the header; left, centre or right
    width: width of the overlay
    height: height of the overlay
    pad: minimum amount of space on all sides between text and border
    """
    def __init__(self, header, header_align, width, height, pad=1):
        GUIElement.__init__(self)
        self.header = header
        self.header_align = header_align
        self.width = width
        self.height = height
        self.pad = pad

        head_height = libt.console_get_height_rect(self.handler.game_map, 0, 0, 
                                                   config.SCREEN_WIDTH, 
                                                   config.SCREEN_HEIGHT, 
                                                   self.header)
        assert head_height == 1

        # Initialize overlay and define some parameters
        self.overlay = libt.console_new(self.width, self.height)
        self.x = (config.SCREEN_WIDTH - 1)/2 - self.width/2
        self.y = (config.SCREEN_HEIGHT - 1)/2 - self.height/2
        self.header_height = 1
        self.header_pad = 1
        
    def draw(self):
        """
        Adds the header to the overlay and blits its contents
        to the root console.
        """
        if self.header_align == data.LEFT:
            self.header_x = self.pad
            self.libt_align = libt.LEFT
        elif self.header_align == data.CENTER:
            self.header_x = (self.width - 1)/2
            self.libt_align = libt.CENTER
        else:
            self.header_x = self.width - 1 - self.pad
            self.libt_align = libt.RIGHT

        libt.console_set_default_foreground(self.overlay, data.COLOURS['text'])
        libt.console_print_ex(self.overlay, self.header_x, self.header_pad, 
                              libt.BKGND_NONE, self.libt_align, self.header)
        libt.console_blit(self.overlay, 0, 0, self.width, self.height, 
                          0, self.x, self.y, 1.0, 0.7)


class SelectMenu(Overlay):
    """
    Class for menu that allows selection of options.

    align: alignment of the options; anything other than left align
    requires that column2 is empty
    options: the selections that can be made in the menu
    empty_options: string that is displayed when no options exist
    column2: additional text that is aligned right of each option,
    must be same length as options
    max_options: number of options to show at once
    bindings: additional keys that enable additional interactivity
    within the menu
    escape: list of keys that dismiss the menu
    """
    def __init__(self, align, header, header_align, width, height, 
                 options, empty_options, column2, max_options, bindings,
                 escape):
        Overlay.__init__(self, header, header_align, width, height)
        self.align = align
        self.options = options
        self.empty_options = empty_options
        self.column2 = column2
        self.max_options = max_options
        self.max_selection = len(self.options) - 1
        self.slice_head = 0
        self.slice_tail = min(self.max_options, self.max_selection + 1)
        self.selection_index = 0
        self.bindings = bindings
        self.escape = escape
        self.active = True
        self.status = None

        if self.align != data.LEFT:
            assert not column2

    def draw(self):
        """
        Prints all the given options up to the specified max_options,
        then draws the background and header.
        """
        libt.console_clear(self.overlay)

        if self.options:
            def print_options():
                """Prints each option out in a column."""
                if self.header_align == data.LEFT:
                    self.option_x = self.pad
                    self.libt_align = libt.LEFT
                elif self.header_align == data.CENTER:
                    self.option_x = (self.width - 1)/2
                    self.libt_align = libt.CENTER
                else:
                    self.option_x = self.width - 1 - self.pad
                    self.libt_align = libt.RIGHT

                if y - self.header_height - self.header_pad == self.selection_index - self.slice_head:
                    libt.console_set_default_foreground(self.overlay, 
                                                        data.COLOURS['selection_text'])
                    libt.console_print_ex(self.overlay, self.option_x, y + self.pad,
                                          libt.BKGND_NONE, self.libt_align, text)
                else:
                    libt.console_set_default_foreground(self.overlay, 
                                                        data.COLOURS['text'])
                    libt.console_print_ex(self.overlay, self.option_x, y + self.pad, 
                                          libt.BKGND_NONE, self.libt_align, text)

            y = self.header_height + self.header_pad

            if self.column2:
                for option, col2 in zip(self.options[self.slice_head:self.slice_tail], 
                                        self.column2[self.slice_head:self.slice_tail]):
                    padding = " " * (self.width - len(option) - len(col2) - 2*self.pad)
                    text = option + padding + col2
                    print_options()
                    y += 1
            else:
                for option in self.options[self.slice_head:self.slice_tail]:
                    text = option
                    print_options()
                    y += 1
        else:
            libt.console_set_default_foreground(self.overlay, data.COLOURS['text'])
            libt.console_print_ex(self.overlay, self.pad, self.header_height + self.header_pad + self.pad, 
                                  libt.BKGND_NONE, libt.LEFT, self.empty_options)

        Overlay.draw(self)
        libt.console_flush()

    def select(self, game_render=True):
        """Handles selection of options in the menu."""
        choice = libt.console_check_for_keypress(True)

        while self.active:
            if self.escape:
                for key in self.escape:
                    if choice.vk == key or chr(choice.c) == key:
                        self.active = False
                        break

                if not self.active:
                    break

            libt.console_wait_for_keypress(True)
            choice = libt.console_wait_for_keypress(True)

            if choice.vk == libt.KEY_UP:
                if self.selection_index > self.slice_head:
                    self.selection_index -= 1
                elif self.slice_head > 0:
                    self.selection_index -= 1
                    self.slice_head -= 1
                    self.slice_tail -= 1
            elif choice.vk == libt.KEY_DOWN:
                if self.selection_index < self.slice_tail - 1:
                    self.selection_index += 1
                elif self.slice_tail < self.max_selection + 1:
                    self.selection_index += 1
                    self.slice_head += 1
                    self.slice_tail += 1
            elif choice.vk == libt.KEY_ENTER and self.options:
                self.bindings[self.selection_index]()
            else:
                for key in self.bindings:
                    if chr(choice.c) == key:
                        self.bindings[key]()
                        break

            if game_render:
                self.handler.render_all()

            self.draw()

        return self.status


class StandardMenu(SelectMenu):
    """
    Menu with one pixel border around the edges 
    and one pixel space between the header and body.
    """
    def __init__(self, align, header, header_align, width, options, 
                 empty_options, column2, max_options, bindings, escape):
        SelectMenu.__init__(self, align, header, header_align, width, 
                            max_options + 4, options, empty_options, 
                            column2, max_options, bindings, escape)


class InventoryMenu(StandardMenu):
    """Popup that appears when entering inventory view."""
    def __init__(self):
        self.bindings = {
            'd': self.bind_drop
        }

        self.item_names = []
        self.item_qty = []
        index = 0

        for item in self.handler.player.inv:
            if not item.stackable:
                for i in range(self.handler.player.inv[item]):
                    self.item_names.append(item.name)
                    self.item_qty.append("")
            else:
                self.item_names.append(item.name)
                self.item_qty.append("Qty: {}".format(self.handler.player.inv[item]))

            self.bindings[index] = item.use

        StandardMenu.__init__(self, data.LEFT, "Inventory", data.CENTER, 40, 
                              self.item_names, "Your inventory is empty.", 
                              self.item_qty, config.ITEMS_PER_PAGE, 
                              self.bindings, [libt.KEY_ESCAPE, "i"])

    def bind_drop(self):
        """Binding for dropping an item."""
        if self.options:
            for item in self.handler.player.inv:
                if item.name == self.options[self.selection_index]:
                    if self.handler.player.inv[item] == 1 or not item.stackable:
                        del self.options[self.selection_index]
                        del self.column2[self.selection_index]

                        if self.selection_index == self.max_selection and self.slice_head > 0:
                            self.slice_head -= 1
                            self.slice_tail -= 1
                            self.selection_index -= 1
                        elif self.selection_index == self.max_selection:
                            self.slice_tail -= 1
                            self.selection_index -= 1

                        self.max_selection -= 1
                    else:
                        new_count = int(self.column2[self.selection_index])
                        new_count -= 1
                        self.column2[self.selection_index] = str(new_count)

                    self.handler.player.player_drop(item)
                    break


class InGameMenu(StandardMenu):
    """Options menu when currently within a game."""
    def __init__(self):
        self.options = ["Resume", "Main Menu"]
        self.bindings = {
            0: self.bind_resume,
            1: self.bind_main_menu
        }

        StandardMenu.__init__(self, data.CENTER, "Options", data.CENTER, 15, 
                              self.options, "", [], 2, self.bindings, 
                              [libt.KEY_ESCAPE])

    def bind_main_menu(self):
        """Brings up the main menu."""
        self.active = False
        self.status = data.EXIT

    def bind_resume(self):
        """Dismisses menu."""
        self.active = False


class MainMenu(StandardMenu):
    """The main menu."""
    def __init__(self):
        self.options = ["New Game", "Quit"]
        self.bindings = {
            0: self.bind_new_game,
            1: self.bind_quit
        }

        StandardMenu.__init__(self, data.CENTER, "BOGEY", data.CENTER, 15, 
                              self.options, "", [], 3, self.bindings, [])

    def draw(self):
        backdrop = libt.image_load(config.IMG_PATH + "title.png")
        libt.image_blit_2x(backdrop, 0, 0, 0)
        StandardMenu.draw(self)

    def bind_new_game(self):
        """Starts a new game."""
        self.handler.new_game()
        self.handler.play()

    def bind_quit(self):
        """Exits program."""
        self.active = False
