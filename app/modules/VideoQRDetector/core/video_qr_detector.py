import cv2
import random
import os
import numpy as np

try:
    from pyzbar import pyzbar

    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


class VideoQRDetector:
    """
    视频二维码检测器类，支持从本地文件或在线视频链接中抽取帧并检测二维码。
    """

    def __init__(self, output_dir="output_frames"):
        """
        初始化视频二维码检测器。

        Args:
            output_dir (str): 保存图片的目录
        """
        # 使用绝对路径确保目录创建成功
        self.output_dir = os.path.abspath(output_dir)
        self._ensure_output_dir()

        # 初始化 OpenCV QR 码检测器作为备用
        try:
            self.qr_detector = cv2.QRCodeDetector()
            self.opencv_qr_available = True
        except:
            self.opencv_qr_available = False

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                print(f"创建输出目录：{self.output_dir}")
            else:
                print(f"输出目录已存在：{self.output_dir}")
        except Exception as e:
            print(f"创建输出目录失败：{e}")
            # 如果无法创建指定目录，使用当前目录
            self.output_dir = os.getcwd()
            print(f"使用当前目录作为输出目录：{self.output_dir}")

    def preprocess_image_for_qr(self, image):
        """
        对图像进行预处理以提高二维码检测率。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 预处理后的图像列表
        """
        processed_images = []

        # 1. 原始图像
        processed_images.append(("original", image))

        # 2. 转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_images.append(("gray", gray))

        # 3. 直方图均衡化
        equalized = cv2.equalizeHist(gray)
        processed_images.append(("equalized", equalized))

        # 4. 对比度限制的自适应直方图均衡化 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
        processed_images.append(("clahe", clahe_img))

        # 5. 高斯模糊后锐化
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        processed_images.append(("sharpened", sharpened))

        # 6. 自适应阈值处理
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_images.append(("adaptive_thresh", adaptive_thresh))

        # 7. Otsu阈值处理
        _, otsu_thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        processed_images.append(("otsu_thresh", otsu_thresh))

        # 8. 形态学操作
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        processed_images.append(("morphology", morph))

        # 9. 不同尺寸的图像
        height, width = gray.shape
        # 放大图像
        enlarged = cv2.resize(
            gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC
        )
        processed_images.append(("enlarged", enlarged))

        # 缩小图像
        if width > 400 and height > 400:
            reduced = cv2.resize(
                gray, (width // 2, height // 2), interpolation=cv2.INTER_AREA
            )
            processed_images.append(("reduced", reduced))

        return processed_images

    def detect_qr_codes_pyzbar(self, image):
        """
        使用 pyzbar 检测二维码。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        if not PYZBAR_AVAILABLE:
            return []

        # 检测二维码
        qr_codes = pyzbar.decode(image)

        results = []
        for qr_code in qr_codes:
            # 获取二维码数据
            qr_data = qr_code.data.decode("utf-8")
            qr_type = qr_code.type

            # 获取二维码位置信息
            points = qr_code.polygon
            if len(points) == 4:
                # 转换为整数坐标
                pts = [(int(point.x), int(point.y)) for point in points]
            else:
                # 如果不是四边形，使用矩形边界
                x, y, w, h = qr_code.rect
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

            results.append(
                {"data": qr_data, "type": qr_type, "points": pts, "method": "pyzbar"}
            )

        return results

    def detect_qr_codes_opencv(self, image):
        """
        使用 OpenCV 检测二维码。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        if not self.opencv_qr_available:
            return []

        results = []

        # 如果是彩色图像，转换为灰度
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        try:
            # 检测和解码二维码
            data, points, _ = self.qr_detector.detectAndDecode(gray)

            if data:
                # 转换点坐标
                if points is not None and len(points) > 0:
                    pts = [(int(point[0]), int(point[1])) for point in points[0]]
                else:
                    pts = []

                results.append(
                    {"data": data, "type": "QRCODE", "points": pts, "method": "opencv"}
                )
        except Exception as e:
            print(f"OpenCV QR 检测出错: {e}")

        return results

    def detect_qr_codes(self, image):
        """
        检测图片中的二维码（增强版）。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        all_results = []

        # 获取预处理后的图像
        processed_images = self.preprocess_image_for_qr(image)

        print(f"正在使用 {len(processed_images)} 种预处理方法检测二维码...")

        for method_name, processed_img in processed_images:
            # 使用 pyzbar 检测
            if PYZBAR_AVAILABLE:
                pyzbar_results = self.detect_qr_codes_pyzbar(processed_img)
                for result in pyzbar_results:
                    result["preprocess_method"] = method_name
                    all_results.append(result)

            # 使用 OpenCV 检测
            if self.opencv_qr_available:
                opencv_results = self.detect_qr_codes_opencv(processed_img)
                for result in opencv_results:
                    result["preprocess_method"] = method_name
                    all_results.append(result)

        # 去重：基于二维码内容去重
        unique_results = []
        seen_data = set()

        for result in all_results:
            if result["data"] not in seen_data:
                seen_data.add(result["data"])
                unique_results.append(result)
                print(
                    f"✅ 检测到二维码 (方法: {result['method']}, 预处理: {result['preprocess_method']})"
                )
                print(f"    内容: {result['data']}")

        return unique_results

    def _get_video_name(self, video_path):
        """
        从视频路径中提取视频名称。

        Args:
            video_path (str): 视频路径或URL

        Returns:
            str: 视频名称
        """
        if video_path.startswith(("http://", "https://")):
            # 从URL中提取文件名，如果无法提取则使用默认名称
            try:
                filename = video_path.split("/")[-1]
                # 移除URL参数
                if "?" in filename:
                    filename = filename.split("?")[0]
                if "." in filename and len(filename.split(".")[0]) > 0:
                    return filename.split(".")[0]
                else:
                    return "online_video"
            except:
                return "online_video"
        else:
            # 本地文件路径
            return os.path.basename(video_path).split(".")[0]

    def extract_random_frame(self, video_path, save_image=True, mark_qr=True):
        """
        从视频中随机抽取一帧并保存为图片，同时检测二维码。

        Args:
            video_path (str): 视频文件的路径或在线视频链接
            save_image (bool): 是否保存图片
            mark_qr (bool): 是否保存标记了二维码的图片

        Returns:
            dict: 包含检测结果的字典
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"错误：无法打开视频文件 {video_path}")
            return {"success": False, "error": "无法打开视频文件"}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            print(f"错误：视频 {video_path} 不包含任何帧。")
            cap.release()
            return {"success": False, "error": "视频不包含任何帧"}

        random_frame_index = random.randint(0, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print(f"错误：未能读取视频 {video_path} 中的随机帧 {random_frame_index}。")
            return {"success": False, "error": "无法读取视频帧"}

        # 检测二维码
        qr_results = self.detect_qr_codes(frame)

        result = {
            "success": True,
            "frame_index": random_frame_index,
            "has_qr_code": len(qr_results) > 0,
            "qr_codes": qr_results,
            "total_frames": total_frames,
        }

        if save_image:
            video_name = self._get_video_name(video_path)
            output_filename = f"frame_{video_name}_{random_frame_index}.jpg"
            output_path = os.path.join(self.output_dir, output_filename)

            # 尝试保存图片并添加错误处理
            try:
                success = cv2.imwrite(output_path, frame)
                if success:
                    result["image_path"] = output_path
                    print(f"成功导出随机帧 {random_frame_index} 到：{output_path}")
                    # 验证文件是否真的存在
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        print(f"文件大小：{file_size} 字节")
                    else:
                        print(f"警告：文件保存后未找到：{output_path}")
                else:
                    print(f"错误：无法保存图片到 {output_path}")
                    result["save_error"] = "cv2.imwrite 返回 False"
            except Exception as e:
                print(f"保存图片时发生错误：{e}")
                result["save_error"] = str(e)

        if qr_results:
            print(f"\n🔍 在图片中检测到 {len(qr_results)} 个二维码：")
            for i, qr_info in enumerate(qr_results, 1):
                print(f"  二维码 {i}:")
                print(f"    类型: {qr_info['type']}")
                print(f"    内容: {qr_info['data']}")
                print(f"    位置: {qr_info['points']}")

            # 可选：在图片上标记二维码位置并保存
            if save_image and mark_qr:
                frame_with_qr = frame.copy()
                for qr_info in qr_results:
                    points = qr_info["points"]
                    # 绘制二维码边界
                    for i in range(len(points)):
                        cv2.line(
                            frame_with_qr,
                            points[i],
                            points[(i + 1) % len(points)],
                            (0, 255, 0),
                            2,
                        )

                    # 在二维码附近添加文本
                    cv2.putText(
                        frame_with_qr,
                        f"QR: {qr_info['data'][:20]}...",
                        (points[0][0], points[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                    )

                # 保存标记了二维码的图片
                video_name = self._get_video_name(video_path)
                marked_filename = f"frame_{video_name}_{random_frame_index}_marked.jpg"
                marked_path = os.path.join(self.output_dir, marked_filename)

                try:
                    success = cv2.imwrite(marked_path, frame_with_qr)
                    if success:
                        result["marked_image_path"] = marked_path
                        print(f"已保存标记二维码的图片到：{marked_path}")
                        # 验证文件是否真的存在
                        if os.path.exists(marked_path):
                            file_size = os.path.getsize(marked_path)
                            print(f"标记图片文件大小：{file_size} 字节")
                    else:
                        print(f"错误：无法保存标记图片到 {marked_path}")
                except Exception as e:
                    print(f"保存标记图片时发生错误：{e}")
        else:
            print("❌ 未在图片中检测到二维码")

        return result

    def has_qr_code(self, video_path, num_samples=3):
        """
        检查视频是否包含二维码。

        Args:
            video_path (str): 视频文件的路径或在线视频链接
            num_samples (int): 采样帧数，默认检查3帧

        Returns:
            bool: 如果在任何一帧中检测到二维码则返回True
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"错误：无法打开视频文件 {video_path}")
            return False

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            print(f"错误：视频 {video_path} 不包含任何帧。")
            cap.release()
            return False

        # 随机采样多帧进行检测
        sample_frames = random.sample(
            range(total_frames), min(num_samples, total_frames)
        )

        for frame_index in sample_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()

            if ret:
                qr_results = self.detect_qr_codes(frame)
                if qr_results:
                    cap.release()
                    print(f"✅ 在第 {frame_index} 帧检测到二维码")
                    return True

        cap.release()
        print(f"❌ 在 {len(sample_frames)} 个采样帧中未检测到二维码")
        return False


if __name__ == "__main__":
    # 创建检测器实例
    detector = VideoQRDetector()

    # 示例用法：
    # 本地视频文件
    video_file = "1.mp4"

    # 在线视频链接示例（取消注释使用）
    # video_file = "https://multimedia.nt.qq.com.cn:443/download?appid=1415&format=origin&orgfmt=t264&spec=0&client_proto=ntv2&client_appid=537290727&client_type=linux&client_ver=3.2.17-34740&client_down_type=auto&client_aio_type=aio&rkey=CAMSoAGKDKztJ3o-DuZWsqllLFaCETK5dfWJ69wEuQ1AC5EyZQ3a3zLuxXz50N35pxCqhZwNqfNJzu3cubFB59_LfSEr8DBQkkzxcJQTpbMv9Fk6GZUqTGS_OW_ijMu-PZjzYm6IX9T5tmTF6-eCUs3HiOucF7LJeccAKH4DSKS6Aqm_9tQpyXmef2LSgX-7xn7GOUjEkq0c_HiC87yKwE9QeFsi"

    # 检查视频文件是否存在（仅对本地文件）
    if not video_file.startswith(("http://", "https://")) and not os.path.exists(
        video_file
    ):
        print(f"错误：视频文件 '{video_file}' 不存在。")
    else:
        # 检查是否包含二维码
        has_qr = detector.has_qr_code(video_file)
        print(f"\n视频是否包含二维码: {has_qr}")

        # 抽取随机帧并检测二维码
        result = detector.extract_random_frame(video_file)

        if result["success"]:
            print(f"\n检测结果:")
            print(f"  总帧数: {result['total_frames']}")
            print(f"  抽取帧索引: {result['frame_index']}")
            print(f"  包含二维码: {result['has_qr_code']}")
            if result["has_qr_code"]:
                print(f"  二维码数量: {len(result['qr_codes'])}")

            # 显示保存的文件路径
            if "image_path" in result:
                print(f"  保存的图片路径: {result['image_path']}")
            if "marked_image_path" in result:
                print(f"  标记图片路径: {result['marked_image_path']}")
            if "save_error" in result:
                print(f"  保存错误: {result['save_error']}")

    print("\n完成！")
    print(f"你可以在 '{detector.output_dir}' 文件夹中找到导出的图片。")
    print("请确保安装了以下依赖：")
    print("  pip install opencv-python")
    print("  pip install pyzbar")
