import kivy
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout


class MainWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

class MyApp(App):
    def build(self):
        return Label(text="Hello")


if __name__ == "__main__":
    MyApp().run()
