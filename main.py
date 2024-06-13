from kivymd.app import MDApp
from AppGUI import MainWindow

class MyApp(MDApp):
    def build(self):
        return MainWindow()


if __name__ == "__main__":
    MyApp().run()
