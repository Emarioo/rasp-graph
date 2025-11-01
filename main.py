###############
#    UI code
###############

from kivy.config import Config
# Uncapping FPS fixes delay when dragging element with mouse or finger.
# It uses more CPU and GPU resources so we don't do that.
# Config.set('graphics', 'maxfps', '0')  # 0 = uncapped
# Config.set('graphics', 'vsync', '0')  # disable vsync, doesn't seem to affect anything on my laptop

# TODO: Use fullscreen on RELEASE
# Config.set('graphics', 'fullscreen', 1)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, Line, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import Graph, LinePlot
from kivy.properties import ListProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
import random

from backend import *
from driver import *

last_touch = None

class TimeSelector(BoxLayout):
    def __init__(self, func, text, default_value, slider_min, slider_max, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        self.func = func
        self.text = text
        self.slider_min = slider_min
        self.slider_max = slider_max
        self.current_value = default_value
        self.display_btn = Button(
            text=self.format_text(default_value),
            font_size=32,
            size_hint=(1, None),
            height=80
        )
        self.display_btn.bind(on_press=self.open_slider_popup)
        self.add_widget(self.display_btn)

        print("create")

    def format_text(self, val):
        at = self.text.find("XX")
        if at == -1:
            return self.text
        return self.text[:at] + str(val) + self.text[at+2:]

    def open_slider_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.slider_label = Label(text=self.format_text(self.current_value), font_size=24)
        slider_min = self.slider_min() if callable(self.slider_min) else self.slider_min
        slider_max = self.slider_max() if callable(self.slider_max) else self.slider_max
        slider = Slider(min=slider_min, max=slider_max, value=self.current_value, step=0.25)
        slider.bind(value=self.update_slider_label)

        confirm = Button(text="OK", size_hint_y=None, height=50)
        popup = Popup(title="Set value", content=layout, size_hint=(0.8, 0.5))
        
        confirm.bind(on_release=lambda *args: self.apply_slider_value(slider.value, popup))

        layout.add_widget(self.slider_label)
        layout.add_widget(slider)
        layout.add_widget(confirm)

        popup.open()

    def round(self, value):
        slider_min = self.slider_min() if callable(self.slider_min) else self.slider_min
        slider_max = self.slider_max() if callable(self.slider_max) else self.slider_max
        v = slider_min + 1/(slider_max-slider_min)*value*value
        if v < 1.0:
            return round(v*4)/4 # because of 0.25 stepping
        return round(v)

    def update_slider_label(self, slider, value):
        slider_min = self.slider_min() if callable(self.slider_min) else self.slider_min
        if slider_min < 1.0:
            value = self.round(value) # because of 0.25 stepping
        self.slider_label.text = self.format_text(value)

    def apply_slider_value(self, value, popup):
        slider_min = self.slider_min() if callable(self.slider_min) else self.slider_min
        if slider_min < 1.0:
            value = self.round(value) # because of 0.25 stepping
        self.current_value = float(value)
        self.display_btn.text = self.format_text(value)
        popup.dismiss()
        self.func(value)

class ColorBox(Widget):
    color = ListProperty([1, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.rect_color = Color(*self.color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect, color=self.update_color)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_color(self, *args):
        self.rect_color.rgba = self.color

class LegendItem(BoxLayout):
    text = StringProperty("")
    color = ListProperty([1, 0, 0, 1])
    background_color = ListProperty([0, 0, 0, 1])  # for adaptive background

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=30, spacing=5, **kwargs)

        # Color box with fixed size
        self.color_box = ColorBox(size_hint=(None, 1), width=30, color=self.color)
        self.add_widget(self.color_box)

        # Adaptive text color based on background brightness
        def get_text_color(bg):
            # simple luminance check
            lum = 0.299*bg[0] + 0.587*bg[1] + 0.114*bg[2]
            return [0, 0, 0, 1] if lum > 0.5 else [1, 1, 1, 1]

        text_color = get_text_color(self.background_color)
        self.label = Label(text=self.text, color=text_color, valign='middle', halign='left')
        self.label.bind(size=lambda instance, val: setattr(instance, 'text_size', val))
        self.add_widget(self.label)

# Page 1: Graph (placeholder with movable rectangles)
class GraphScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        w, h = Window.size

        self.graph = Graph(
            xlabel='Time (s)',
            ylabel='Value (C, %)',
            x_ticks_minor=5,
            x_ticks_major=10,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=50,
            ymin=0,
            ymax=40
        )

        # TODO: Reset zoom ability.

        # Temperature plot (red)
        self.temp_plot = LinePlot(line_width=2, color=[1, 0, 0, 1])
        # Humidity plot (blue)
        self.humid_plot = LinePlot(line_width=2, color=[0, 0, 1, 1])

        self.update_graph(0.016)

        # Add plots to the graph
        self.graph.add_plot(self.temp_plot)
        self.graph.add_plot(self.humid_plot)

        legend_layout = BoxLayout(size_hint_y=None, height=30)
        legend_layout.add_widget(LegendItem(color=[1,0,0,1], text="Temperature"))
        legend_layout.add_widget(LegendItem(color=[0,0,1,1], text="Humidity"))

        root_layout = BoxLayout(orientation='vertical')
        root_layout.add_widget(self.graph)
        root_layout.add_widget(legend_layout)

        root_layout.canvas.before.clear()
        with root_layout.canvas.before:
            # Color(0.11, 0.11, 0.11, 1)
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(pos=(0,0), size=(w,h))

        self.add_widget(root_layout)

        Clock.schedule_interval(self.update_graph, 1)  # every 1 second

    def update_graph(self, dt):
        new_temp = read_temperature()
        new_humid = read_humidity()
        add_temp(new_temp)
        add_humid(new_humid)
        # print(temp_data)
        self.temp_plot.points = slice_temperature_points(0, self.graph.xmax, 1.0)
        self.humid_plot.points = slice_humidity_points(0, self.graph.xmax, 1.0)

    def on_touch_down(self, touch):
        global last_touch
        last_touch = (touch.x,touch.y)

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        global last_touch
        # print(touch)
        # Swipe detection
        if last_touch and touch.x - last_touch[0] < -50:
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'settings'
        else:
            return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # print("release1")
        return super().on_touch_up(touch)


# Page 2: Settings
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start = None
        w, h = Window.size

        root_layout = BoxLayout(orientation='vertical')
        # self.add_widget(Label(text="Settings", pos_hint={'top': 1}, size_hint=(1, 0.1), font_size='24sp'))

        # min max diagram range

        # time, max value for alarm
        def set_ymin(val):
            graph_screen = self.manager.get_screen('graph')
            graph_screen.graph.ymin = val
            get_config().ymin = val
            save_config()
            
        def set_ymax(val):
            graph_screen = self.manager.get_screen('graph')
            graph_screen.graph.ymax = val
            get_config().ymax = val
            save_config()

        def get_slider_min():
            graph_screen = self.manager.get_screen('graph')
            return graph_screen.graph.ymin

        def get_slider_max():
            graph_screen = self.manager.get_screen('graph')
            return graph_screen.graph.ymax

        root_layout.add_widget(TimeSelector(set_ymin, "Diagram XX y-min", get_config().ymin, 0, get_slider_max))
        root_layout.add_widget(TimeSelector(set_ymax, "Diagram XX y-max", get_config().ymax, get_slider_min, 100))

        def set_warn_period(val):
            get_config().warn_period = val
            save_config()

        def set_warn_level(val):
            get_config().warn_level = val
            save_config()

        root_layout.add_widget(TimeSelector(set_warn_period, "warn humidity period, XX min", config.warn_period, 1, 120))
        root_layout.add_widget(TimeSelector(set_warn_level, "warn humidity level, XX %", config.warn_level, 10, 60))

        def set_rate(val):
            print("Change rate", val)
            get_config().rate = val
            save_config()

        root_layout.add_widget(TimeSelector(set_rate, "Read rate, XX seconds per data point", config.rate, 0.25, 60))

        root_layout.canvas.before.clear()
        with root_layout.canvas.before:
            # Color(0.11, 0.11, 0.11, 1)
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(pos=(0,0), size=(w,h))

        self.add_widget(root_layout)

    def on_touch_down(self, touch):
        global last_touch
        last_touch = (touch.x, touch.y)

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        global last_touch
        if last_touch and touch.x - last_touch[0] > 50:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'graph'

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        # print("release2")
        return super().on_touch_up(touch)

# App with screen manager
class TheApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(GraphScreen(name='graph'))
        sm.add_widget(SettingsScreen(name='settings'))

        Window.bind(on_key_down=self.on_key_down)
        return sm
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC
            self.stop()

    def on_stop(self):
        save_data()

if __name__ == '__main__':
    load_config()
    load_data()

    # save every minute data points, we could do less frequent
    Clock.schedule_interval(lambda dt: save_data(), 60)

    TheApp().run()
