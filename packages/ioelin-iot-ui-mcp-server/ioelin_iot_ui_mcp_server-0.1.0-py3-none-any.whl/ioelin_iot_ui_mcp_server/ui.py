import tkinter as tk
from PIL import Image, ImageTk

rotating_images = {}
static_images = {}


class RotatingImage:
    def __init__(self, canvas, image_path, x, y, speed=1, size=(30, 30), always_on_top=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = 0
        self.running = False
        self.after_id = None
        self.always_on_top = always_on_top
        # 加载并调整图片大小
        self.original_img = Image.open(image_path).convert("RGBA")
        self.original_img = self.original_img.resize(size, Image.LANCZOS)

        # 创建初始旋转图片
        self._create_rotated_image()

    def _create_rotated_image(self):
        rotated = self.original_img.rotate(-self.angle, Image.BICUBIC, expand=True)
        self.tk_img = ImageTk.PhotoImage(rotated)
        if not hasattr(self, 'image_id'):
            self.image_id = self.canvas.create_image(self.x, self.y, image=self.tk_img)
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_img)

    def _rotate(self):
        if not self.running:
            return
        self.angle = (self.angle + self.speed) % 360
        self._create_rotated_image()
        if self.always_on_top:
            self.canvas.tag_raise(self.image_id)
        self.canvas.tag_raise(self.image_id)  # 确保在最上层
        self.after_id = self.canvas.after(20, self._rotate)

    def start(self):
        if not self.running:
            self.running = True
            self._rotate()

    def stop(self):
        self.running = False
        if self.after_id:
            self.canvas.after_cancel(self.after_id)
            self.after_id = None

    def delete(self):
        """彻底删除旋转图片"""
        self.stop()
        if hasattr(self, 'image_id'):
            self.canvas.delete(self.image_id)
        self.tk_img = None
        self.original_img = None


class RotatingImageApp:
    def __init__(self, background_path="back.png"):
        self.root = tk.Tk()
        self.root.title("图片旋转器")
        self.root.configure(bg="#555")
        self.top_layer_items = set()  # 使用集合存储需要保持最上层的项目ID
        self._top_layer_lock = False  # 防止递归调用导致的卡死
        # 窗口最大化
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)

        # 加载背景图
        self.background = Image.open(background_path).convert("RGBA")
        self.background = self.background.resize((950, 950), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.background)

        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=950,
            height=950,
            bg="#555",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 放置背景图
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.bg_y = (screen_height - 950) // 2 + 450
        self.canvas.create_image(
            screen_width // 2,
            self.bg_y,
            image=self.bg_photo,
            anchor="center"
        )

        self.rotating_images = []  # 存储RotatingImage对象
        self.overlay_items = []  # 存储叠加图片的画布ID和引用

    def _safe_maintain_top_layers(self):
        """安全维护最上层项目"""
        if not self._top_layer_lock:
            self._top_layer_lock = True
            for item_id in list(self.top_layer_items):  # 使用副本遍历
                try:
                    self.canvas.tag_raise(item_id)
                except tk.TclError:  # 如果项目已被删除
                    self.top_layer_items.discard(item_id)
            self._top_layer_lock = False
            self.root.after(200, self._safe_maintain_top_layers)  # 改为200ms检查一次

    def add_static_image(self, image_path, x, y, size=(30, 30)):
        """专门添加静态图片（不旋转且保持在最上层）"""
        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            item_id = self.canvas.create_image(x, y, image=photo)
            self.top_layer_items.add(item_id)
            self.canvas.tag_raise(item_id)

            # 保持引用
            if not hasattr(self, '_static_images'):
                self._static_images = []
            self._static_images.append(photo)
            return item_id
        except Exception as e:
            print(f"添加静态图片失败: {e}")
            return None

    def remove_static_image(self, item_id):
        """删除静态图片"""
        try:
            self.canvas.delete(item_id)
            self.top_layer_items.discard(item_id)
        except Exception as e:
            print(f"删除静态图片失败: {e}")

    def add_overlay_image(self, image_path, x_offset=0, y_offset=0):
        """叠加静态图片"""
        try:
            overlay = Image.open(image_path).convert("RGBA")
            overlay = overlay.resize((950, 950), Image.LANCZOS)
            overlay_photo = ImageTk.PhotoImage(overlay)

            screen_width = self.root.winfo_screenwidth()
            x = screen_width // 2 + x_offset
            y = self.bg_y + y_offset

            item_id = self.canvas.create_image(x, y, image=overlay_photo, anchor="center")

            # 存储所有必要数据
            self.overlay_items.append({
                'id': item_id,
                'photo': overlay_photo,
                'image': overlay
            })
            return item_id
        except Exception as e:
            print(f"加载叠加图片失败: {e}")
            return None

    def remove_overlay_image(self, item_id=None):
        """删除叠加图片"""
        if not self.overlay_items:
            return False

        try:
            if item_id is None:
                target = self.overlay_items.pop()
            else:
                target = next((item for item in self.overlay_items if item['id'] == item_id), None)
                if not target:
                    return False
                self.overlay_items.remove(target)

            self.canvas.delete(target['id'])
            target['photo'] = None
            target['image'] = None
            return True
        except Exception as e:
            print(f"删除叠加图片失败: {e}")
            return False

    def add_rotating_image(self, image_path, x=None, y=None, speed=2, size=(30, 30), always_on_top=False):
        """添加旋转图片"""
        try:
            if x is None:
                x = self.canvas.winfo_width() // 2
            if y is None:
                y = self.canvas.winfo_height() // 2

            new_img = RotatingImage(
                canvas=self.canvas,
                image_path=image_path,
                x=x,
                y=y,
                speed=speed,
                size=size,
                always_on_top = always_on_top
            )

            if always_on_top:
                self.top_layer_items.append(new_img.image_id)
                self.canvas.tag_raise(new_img.image_id)

            self.rotating_images.append(new_img)
            return new_img
        except Exception as e:
            print(f"添加旋转图片失败: {e}")
            return None

    def remove_rotating_image(self, rotating_image):
        """删除旋转图片"""
        if rotating_image in self.rotating_images:
            rotating_image.delete()
            self.rotating_images.remove(rotating_image)
            return True
        return False

    def clear_all(self):
        """清除所有图片"""
        for img in list(self.rotating_images):
            self.remove_rotating_image(img)
        for item in list(self.overlay_items):
            self.remove_overlay_image(item['id'])

    def run(self):
        self.root.mainloop()


# def start_app():
#     app = RotatingImageApp(background_path="static/back.png")
#     # 安全启动层级维护（延迟500ms开始）
#     app.root.after(500, app._safe_maintain_top_layers)
#
#
#     app.run()
#
# if __name__ == "__main__":
#     start_app()


