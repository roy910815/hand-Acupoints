import cv2
import win32api
import win32con
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.text import LabelBase
from yolov4 import detect_objects
from yolov8 import analysis

LabelBase.register(name='prestory', fn_regular='textFormat.ttf')
normalized_color = (141/255.0, 180/ 255.0, 137/ 255.0, 0.8)

class CameraApp(App):
    def __init__(self):
        super(CameraApp, self).__init__()
        self.saved_image = None
        self.capture = None

    def build(self):
        Window.size = (360, 640)
        self.main_layout = FloatLayout()

        self.first_image = Image(source='firstImg.png', allow_stretch=True, keep_ratio=False)
        self.main_layout.add_widget(self.first_image)

        Clock.schedule_once(self.show_main_ui, 5)

        return self.main_layout
    
    def show_main_ui(self, dt):

        self.start_image = Image(source='startImg.png', allow_stretch=True, keep_ratio=False)
        self.main_layout.remove_widget(self.first_image)
        self.main_layout.add_widget(self.start_image)

        button1 = Button(
            text='Hand detect',
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.3, 'y': 0.1},
            background_color = normalized_color,
            font_name = 'prestory',
            font_size=28,
            on_press=self.on_button1_press,
            on_release=self.on_button_release
        )
        button2 = Button(
            text='Point show',
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={'center_x': 0.7, 'y': 0.1},
            font_name = 'prestory',
            font_size=28,     
            on_press=self.on_button2_press,
            on_release=self.on_button_release,
            background_color = normalized_color
        )
        button3 = Button(
            text='Acupoint Diagram',
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'center_x': 0.5, 'y': 0.25},
            font_name = 'prestory',
            font_size=28,
            on_press=self.on_button3_press,
            on_release=self.on_button_release,
            background_color = normalized_color
        )
        
        self.main_layout.add_widget(button1)
        self.main_layout.add_widget(button2)
        self.main_layout.add_widget(button3)

        Window.bind(mouse_pos=self.on_mouse_move)

        return self.main_layout
    
    def on_mouse_move(self, window, pos):
        over_any_button = False
        for widget in self.main_layout.children:
            if isinstance(widget, Button) and widget.collide_point(*pos):
                over_any_button = True
                break
        if over_any_button:
            self.cursor_enter()
        else:
            self.cursor_leave()
    
    def cursor_enter(self):
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_HAND))

    def cursor_leave(self):
        win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_ARROW))

    def on_button1_press(self, instance):
        instance.background_color = (141/255.0, 180/ 255.0, 137/ 255.0, 0.2)
        Clock.schedule_once(lambda dt: self.show_camera_top_left(instance), 0.1)

    def on_button2_press(self, instance):
        instance.background_color = (141/255.0, 180/ 255.0, 137/ 255.0, 0.2)
        Clock.schedule_once(lambda dt: self.show_saved_image(instance), 0.1)


    def on_button3_press(self, instance):
        instance.background_color = (141/255.0, 180/ 255.0, 137/ 255.0, 0.2)
        Clock.schedule_once(lambda dt: self.show_guide_image(instance), 0.1)

    def on_button_release(self, instance):
        instance.background_color = normalized_color

    def show_camera_top_left(self, instance):
        self.show_camera((10, 10))

    def show_saved_image(self, instance):
       if self.saved_image is not None:
        saved_layout = FloatLayout()
        saved_image_widget = Image(texture=self.saved_image.texture, size_hint=(None, None))
        saved_image_widget.size = saved_image_widget.texture.size
        saved_image_widget.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        saved_layout.add_widget(saved_image_widget)
        popup = Popup(title='Acupoint Image', content=saved_layout, size_hint=(None, None), size=saved_image_widget.texture.size)
        popup.open()

    def show_camera(self, point_position):
        camera_layout = FloatLayout()

        background = Image(source='startImg.png', allow_stretch=True, keep_ratio=False, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        camera_layout.add_widget(background)

        self.camera_image = Image(size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        camera_layout.add_widget(self.camera_image)

        text_label = Label(text='Detected Hand', size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5, 'y': 0.9})
        camera_layout.add_widget(text_label)

        crop_button = Button(text='Crop and Save Hand', size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.05},
                             on_press=self.crop_and_save_hand,font_name = 'prestory',font_size=28,background_color = normalized_color)
        camera_layout.add_widget(crop_button)

        self.popup = Popup(title='Camera', content=camera_layout, size_hint=(1, 1))
        self.popup.open()

        self.start_camera(self.camera_image, point_position)

    def start_camera(self, img_widget, point_position):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Could not open camera.")
            return
        self.camera_active = True
        self.point_position = point_position
        self.img_widget = img_widget
        self.detected_hand = None
        Clock.schedule_interval(self.update, 1.0 / 90.0)

    def stop_camera(self):
        self.camera_active = False
        if self.capture and self.capture.isOpened():
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update)
        if self.img_widget:
            self.img_widget.texture = None

    def update(self, dt):
        if self.capture and self.camera_active:
            ret, frame = self.capture.read()
            if ret:
                frame, self.detected_hand = detect_objects(frame)
                buffer = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                self.img_widget.texture = texture

    def crop_and_save_hand(self, instance):
        if self.detected_hand is not None:
            x, y, w, h = self.detected_hand
            if self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    cropped_hand = frame[y:y+h, x:x+w]
                    cv2.imwrite('detected_hand.jpg', cropped_hand)
                    analysis()
                    self.saved_image = Image(source='detected_hand.jpg')
                    self.popup.dismiss()
                    self.stop_camera()
                else:
                    print("Error: Could not read frame.")
            else:
                print("Error: Camera is not opened.")
        else:
            print("No hand detected to crop and save.")

    def on_stop(self):
        self.stop_camera()

    def show_guide_image(self, instance):
        from functools import partial

        guide_layout = FloatLayout()
        guide_image = Image(source='acupointImg.png', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        guide_layout.add_widget(guide_image)

        acpt1= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.35, 'y': 0.345},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source='1.png')
        )

        acpt2= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.44, 'y': 0.378},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source="2.png")
        )

        acpt3= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.445, 'y': 0.518},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source="3.png")
        )
        
        acpt4= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.58, 'y': 0.51},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source="4.png")
        )

        acpt5= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.58, 'y': 0.47},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source="5.png")
        )

        acpt6= Button(
            size_hint=(None, None),
            size=(35, 35),
            pos_hint={'center_x': 0.7, 'y': 0.47},
            background_color= [1,0,0,0],
            on_press=partial(self.show_popup, image_source="6.png")
        )

        return_button = Button(text='Return', size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'y': 0.025}, background_color = normalized_color,font_name = 'prestory',font_size=28)
        popup = Popup(title='Click the Acupoint to check the detail inforamtion', content=guide_layout, size_hint=(1, 1))
        return_button.bind(on_press=popup.dismiss)
        guide_layout.add_widget(return_button)
        guide_layout.add_widget(acpt1)
        guide_layout.add_widget(acpt2)
        guide_layout.add_widget(acpt3)
        guide_layout.add_widget(acpt4)
        guide_layout.add_widget(acpt5)
        guide_layout.add_widget(acpt6)

        popup.open()
    
    def show_popup(self, instance, image_source):
        popup_layout = FloatLayout()
        popup_image = Image(source=image_source, size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        popup_layout.add_widget(popup_image)
        return_button = Button(text='Return', size_hint=(0.2, 0.1), size=(100, 80), pos_hint={'center_x': 0.25, 'y': 0.05},background_color=normalized_color, font_name='prestory', font_size=28)
        popup = Popup(title='Introduction to the Acupoint', content=popup_layout, size_hint=(1, 1))
        return_button.bind(on_press=lambda x: popup.dismiss())
        popup_layout.add_widget(return_button)
        popup.open()


if __name__ == '__main__':
    CameraApp().run()
