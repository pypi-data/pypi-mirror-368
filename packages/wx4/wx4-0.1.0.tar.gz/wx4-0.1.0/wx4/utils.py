import os.path
import re
import random
import time

from loguru import Logger
import pyperclip
import pyautogui
import uiautomation as uia
from PIL import Image, UnidentifiedImageError


def get_logger():
    logger.remove()
    if os.getenv("Logs") is None:
        raise RuntimeError("Error to get log path")
    else:
        if not os.path.exists(str(os.getenv("Logs"))):
            raise RuntimeError(
                f"Log file doesn't exists, Config file path:{os.getenv('Logs')}"
            )
        else:
            logger.add(str(os.getenv("Logs")))
    return logger

logger: Logger = get_logger()


def voice_msg_processor(msg_content) -> None | dict:
    """处理音频消息
    Args:
        msg_content(str):消息的内容
    """
    msg = msg_content
    pattern = r'"语言(\d+)"秒(.*)'
    match = re.search(pattern, msg)
    if match:
        if (match.group(1) is None) or (match.group(2) is None):
            return None
        else:
            return {"time": match.group(1), "msg": int(match.group(2))}
    else:
        return None


def SetClipboardText(text: str):
    pyperclip.copy(text)


class MSG:
    """
    wx的消息
    """

    def __init__(
        self, index: int, sender: str, content: str, auto_process_voice_msg: bool = True
    ) -> None:
        self.sender = sender
        self.content = content
        self.index = index
        if not auto_process_voice_msg:
            return
        voice_msg = voice_msg_processor(self.content)
        if voice_msg is not None:  # 避免重复调用
            self.time: int = int(voice_msg["time"])
            self.content: str = str(voice_msg["content"])

    def __str__(self):
        return f"MSG(index={self.index}, sender={self.sender}, content={self.content})"

    def __repr__(self):
        return f"MSG(index={self.index}, sender={self.sender}, content={self.content})"


def merge_lists(a: list, b: list) -> list:
    """
    合并两个列表,去除重复部分
    Args:
        a(list):第一个列表
        b(list):第二个列表
    Example:
        ```
        merge_lists([1,2,3,4,5],[3,4,5,6,7,8])
        ```
        Return [1,2,3,4,5,6,7,8]
    """

    def find_overlap(a: list, b: list) -> int:
        max_len = min(len(a), len(b))
        # Check for end of a and start of b overlap
        max_overlap = 0
        for overlap in range(max_len, -1, -1):
            if overlap == 0:
                break
            if a[-overlap:] == b[:overlap]:
                max_overlap = overlap
                break
        return max_overlap

    overlap = find_overlap(a, b)
    if overlap > 0:
        merged = a + b[overlap:]
    else:
        overlap_start = find_overlap(b, a)
        if overlap_start > 0:
            merged = b + a[overlap_start:]
        else:
            merged = a + b
    return merged


def capture_control_image(control: uia.Control):
    """
    根据控件对象截取屏幕上的控件图像。
    """
    rect = control.BoundingRectangle
    left = rect.left
    top = rect.top
    right = rect.right
    bottom = rect.bottom
    width = right - left
    height = bottom - top
    screenshot: Image.Image = pyautogui.screenshot(region=(left, top, width, height))
    return screenshot


def is_fully_visible(control: uia.Control):
    """
    判断控件是否完全可见
    :param control: uiautomation控件对象
    :return: True如果控件完全可见，False否则
    """
    # 首先检查控件是否在屏幕上
    if control.IsOffscreen:
        return False

    # 获取控件的边界矩形
    try:
        rect = control.BoundingRectangle
        if not rect:
            return False

        # 使用Rect对象的属性而不是下标访问
        left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom

        # 检查控件是否有有效的尺寸
        if right <= left or bottom <= top:
            return False

        # 获取桌面窗口（用于比较屏幕尺寸）
        desktop = uia.GetRootControl()
        desktop_rect = desktop.BoundingRectangle

        # 检查控件是否完全在桌面可见区域内
        return (
            left >= desktop_rect.left
            and top >= desktop_rect.top
            and right <= desktop_rect.right
            and bottom <= desktop_rect.bottom
        )
    except Exception as e:
        logger.error(f"检查可见性时出错: {e}")
        return False


def image_contains_color(image_path, tolerance=0) -> bool:
    """
    检查图片中是否包含(149, 236, 105)。

    :param image_path: 图片路径
    :param tolerance: 颜色容差
    :return: 如果图片中包含目标颜色，返回True，否则返回False
    """
    try:
        image = Image.open(image_path)
    except UnidentifiedImageError as e:
        logger.error(e)
        return False
    image = image.convert("RGB")
    width, height = image.size
    count: int = 0
    for x in range(width):
        for y in range(height):
            pixel_color = image.getpixel((x, y))
            diff = sum(
                abs(a - b) for a, b in zip(pixel_color, (149, 236, 105))
            )  # 计算当前颜色与目标颜色之间的差值

            if diff <= tolerance:  # 如果差值小于容差，则认为颜色匹配
                count += 1
            if count > 50:
                return True
    return False


def GetSender(control) -> str:
    save_path = f"wxdata\\cache\\{str(control.GetRuntimeId())}.png"
    if (
        (control.Name != "图片")  # 不是图片
        and (str(control.AutomationId) != "")  # 不是时间
        and (is_fully_visible(control))  # 控件完全可见
        and (control.Name != "文件")  # 不是文件
    ):
        if not os.path.exists(save_path):
            screenshot = capture_control_image(control)
            screenshot.save(save_path)
        if image_contains_color(save_path):
            sender = "Self"
        else:
            sender = "Other"
    elif str(control.AutomationId) == "":
        sender = "SYS"
    else:
        sender = ""
    return sender


def wheel_control(
    control: uia.Control, times: int = 5, wheel_range: list[int] = [300, 400]
) -> None:
    """滚轮控制
    Args:
        control(uiautomation.Control):要滚动的控件
        times(int):滚动的分的次数
        wheel_range(list):随机范围，例如[300, 400]
    """
    if times <= 0:  # 避免除零错误
        logger.warning("times 参数必须大于 0")
        return
    time_list = [random.random() for _ in range(times)]
    control.SetFocus()
    for i in range(times):
        pyautogui.scroll(
            clicks=random.randint(
                int(wheel_range[0] / times), int(wheel_range[1] / times)
            )
        )
        time.sleep(time_list[i] / 20)


if __name__ == "__main__":
    print(merge_lists([1, 2], [1, 2]))
