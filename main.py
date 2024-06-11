import kivy
from kivy.uix.label import Label
from kivy.app import App

class MyApp(App):
    def build(self):
        return Label(text="Hello")


if __name__ == "__main__":
    MyApp().run()
