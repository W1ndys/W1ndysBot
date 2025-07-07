import cv2
import random
import os
import numpy as np
import asyncio
import platform
import aiohttp
from logger import logger

try:
    from pyzbar import pyzbar

    PYZBAR_AVAILABLE = True
except ImportError as e:
    PYZBAR_AVAILABLE = False
    PYZBAR_ERROR = str(e)


class QRDetector:
    """
    通用二维码检测器类，支持检测图片和视频中的二维码。
    """

    def __init__(self, output_dir="output_frames"):
        """
        初始化二维码检测器。

        Args:
            output_dir (str): 保存图片的目录
        """
        # 使用绝对路径确保目录创建成功
        self.output_dir = os.path.abspath(output_dir)

        # 初始化 OpenCV QR 码检测器作为备用
        try:
            self.qr_detector = cv2.QRCodeDetector()
            self.opencv_qr_available = True
        except:
            self.opencv_qr_available = False

        # 检查依赖并给出友好提示
        self._check_dependencies()

    def _check_dependencies(self):
        """检查依赖并给出安装建议"""
        if not PYZBAR_AVAILABLE:
            logger.warning("⚠️  pyzbar 不可用，二维码检测功能受限")
            logger.warning(f"   错误信息: {PYZBAR_ERROR}")

            if platform.system() == "Linux":
                logger.warning("🔧 Linux 系统解决方案:")
                logger.warning("   sudo apt-get update")
                logger.warning("   sudo apt-get install libzbar0 libzbar-dev")
                logger.warning("   pip install pyzbar")
            elif platform.system() == "Windows":
                logger.warning("🔧 Windows 系统解决方案:")
                logger.warning("   pip install pyzbar")
            elif platform.system() == "Darwin":  # macOS
                logger.warning("🔧 macOS 系统解决方案:")
                logger.warning("   brew install zbar")
                logger.warning("   pip install pyzbar")

        if not self.opencv_qr_available:
            logger.warning("⚠️  OpenCV QR 检测器不可用")
            logger.warning("🔧 解决方案:")
            logger.warning("   pip install opencv-python")

        if not PYZBAR_AVAILABLE and not self.opencv_qr_available:
            logger.error("❌ 没有可用的二维码检测器！")
            logger.error("   请安装 pyzbar 或确保 OpenCV 正常工作")

    def _validate_url(self, url):
        """
        验证URL是否有效。

        Args:
            url (str): URL地址

        Returns:
            bool: URL是否有效
        """
        if not isinstance(url, str):
            return False
        return url.startswith(("http://", "https://"))

    async def _ensure_output_dir(self):
        """确保输出目录存在"""
        try:
            if not os.path.exists(self.output_dir):
                await asyncio.get_event_loop().run_in_executor(
                    None, os.makedirs, self.output_dir
                )
                logger.info(f"创建输出目录：{self.output_dir}")
            else:
                logger.info(f"输出目录已存在：{self.output_dir}")
        except Exception as e:
            logger.error(f"创建输出目录失败：{e}")
            self.output_dir = os.getcwd()
            logger.info(f"使用当前目录作为输出目录：{self.output_dir}")

    async def preprocess_image_for_qr(self, image):
        """
        对图像进行预处理以提高二维码检测率。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 预处理后的图像列表
        """

        def _process_image():
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

            # 10. 暗色模式处理：反转图像颜色
            inverted = cv2.bitwise_not(gray)
            processed_images.append(("inverted_for_dark_mode", inverted))

            # 11. 暗色模式 + 对比度增强
            inverted_clahe = clahe.apply(inverted)
            processed_images.append(("inverted_clahe", inverted_clahe))

            # 12. 暗色模式 + 自适应阈值
            inverted_adaptive = cv2.adaptiveThreshold(
                inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(("inverted_adaptive", inverted_adaptive))

            # 13. 暗色模式 + Otsu阈值
            _, inverted_otsu = cv2.threshold(
                inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            processed_images.append(("inverted_otsu", inverted_otsu))

            return processed_images

        return await asyncio.get_event_loop().run_in_executor(None, _process_image)

    async def detect_qr_codes_pyzbar(self, image):
        """
        使用 pyzbar 检测二维码。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        if not PYZBAR_AVAILABLE:
            return []

        def _detect():
            qr_codes = pyzbar.decode(image)
            results = []
            for qr_code in qr_codes:
                qr_data = qr_code.data.decode("utf-8")
                qr_type = qr_code.type

                points = qr_code.polygon
                if len(points) == 4:
                    pts = [(int(point.x), int(point.y)) for point in points]
                else:
                    x, y, w, h = qr_code.rect
                    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

                results.append(
                    {
                        "data": qr_data,
                        "type": qr_type,
                        "points": pts,
                        "method": "pyzbar",
                    }
                )
            return results

        return await asyncio.get_event_loop().run_in_executor(None, _detect)

    async def detect_qr_codes_opencv(self, image):
        """
        使用 OpenCV 检测二维码。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        if not self.opencv_qr_available:
            return []

        def _detect():
            results = []
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            try:
                data, points, _ = self.qr_detector.detectAndDecode(gray)
                if data:
                    if points is not None and len(points) > 0:
                        pts = [(int(point[0]), int(point[1])) for point in points[0]]
                    else:
                        pts = []

                    results.append(
                        {
                            "data": data,
                            "type": "QRCODE",
                            "points": pts,
                            "method": "opencv",
                        }
                    )
            except Exception as e:
                logger.error(f"OpenCV QR 检测出错: {e}")

            return results

        return await asyncio.get_event_loop().run_in_executor(None, _detect)

    async def detect_qr_codes(self, image):
        """
        检测图片中的二维码（增强版）。

        Args:
            image: OpenCV图像对象

        Returns:
            list: 检测到的二维码信息列表
        """
        all_results = []

        # 获取预处理后的图像
        processed_images = await self.preprocess_image_for_qr(image)

        logger.info(f"正在使用 {len(processed_images)} 种预处理方法检测二维码...")

        # 并发检测所有预处理后的图像
        detection_tasks = []

        for method_name, processed_img in processed_images:
            # 使用 pyzbar 检测
            if PYZBAR_AVAILABLE:
                task = self._detect_with_method(processed_img, method_name, "pyzbar")
                detection_tasks.append(task)

            # 使用 OpenCV 检测
            if self.opencv_qr_available:
                task = self._detect_with_method(processed_img, method_name, "opencv")
                detection_tasks.append(task)

        # 等待所有检测任务完成
        if detection_tasks:
            results_list = await asyncio.gather(*detection_tasks)
            for results in results_list:
                all_results.extend(results)

        # 去重：基于二维码内容去重
        unique_results = []
        seen_data = set()

        for result in all_results:
            if result["data"] not in seen_data:
                seen_data.add(result["data"])
                unique_results.append(result)
                logger.info(
                    f"✅ 检测到二维码 (方法: {result['method']}, 预处理: {result['preprocess_method']})"
                )
                logger.info(f"    内容: {result['data']}")

        return unique_results

    async def _detect_with_method(self, image, method_name, detector_type):
        """使用指定方法和预处理检测二维码的辅助函数"""
        if detector_type == "pyzbar":
            results = await self.detect_qr_codes_pyzbar(image)
        else:
            results = await self.detect_qr_codes_opencv(image)

        for result in results:
            result["preprocess_method"] = method_name

        return results

    async def detect_image_from_url(self, image_url):
        """
        从URL下载图片并检测二维码。

        Args:
            image_url (str): 图片URL

        Returns:
            dict: 检测结果
        """
        if not self._validate_url(image_url):
            return {"success": False, "error": "无效的图片URL"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        # 将字节数据转换为numpy数组
                        nparr = np.frombuffer(image_data, np.uint8)
                        # 解码为OpenCV图像
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                        if image is not None:
                            qr_results = await self.detect_qr_codes(image)
                            return {
                                "success": True,
                                "has_qr_code": len(qr_results) > 0,
                                "qr_codes": qr_results,
                                "media_type": "image",
                            }
                        else:
                            return {"success": False, "error": "无法解码图片"}
                    else:
                        return {
                            "success": False,
                            "error": f"下载图片失败: {response.status}",
                        }
        except Exception as e:
            return {"success": False, "error": f"图片处理失败: {str(e)}"}

    async def detect_video_from_url(self, video_url, max_retries=3):
        """
        从视频URL检测二维码。

        Args:
            video_url (str): 视频URL
            max_retries (int): 最大重试次数

        Returns:
            dict: 检测结果
        """
        if not self._validate_url(video_url):
            return {"success": False, "error": "无效的视频URL"}

        # 获取视频信息
        video_info = await self._get_video_info(video_url)
        if not video_info["success"]:
            return video_info

        # 尝试多次检测
        for attempt in range(max_retries):
            logger.info(f"🎯 第 {attempt + 1} 次尝试检测视频二维码...")

            frame_result = await self._extract_single_frame(video_url, video_info)
            if not frame_result["success"]:
                continue

            frame = frame_result["frame"]
            qr_results = await self.detect_qr_codes(frame)

            if qr_results:
                logger.info(
                    f"✅ 第 {attempt + 1} 次尝试成功检测到 {len(qr_results)} 个二维码！"
                )
                return {
                    "success": True,
                    "has_qr_code": True,
                    "qr_codes": qr_results,
                    "media_type": "video",
                    "attempt": attempt + 1,
                    "frame_index": frame_result["frame_index"],
                }

        return {
            "success": True,
            "has_qr_code": False,
            "qr_codes": [],
            "media_type": "video",
            "message": f"经过 {max_retries} 次尝试，均未检测到二维码",
        }

    async def _get_video_info(self, video_url):
        """获取视频基本信息"""

        def _get_info():
            cap = cv2.VideoCapture(video_url)
            if not cap.isOpened():
                return {"success": False, "error": "无法打开视频URL"}

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            if total_frames == 0:
                return {"success": False, "error": "视频不包含任何帧"}

            return {
                "success": True,
                "total_frames": total_frames,
                "video_info": {"fps": fps, "width": width, "height": height},
            }

        return await asyncio.get_event_loop().run_in_executor(None, _get_info)

    async def _extract_single_frame(self, video_url, video_info):
        """抽取单个随机帧"""

        def _extract():
            cap = cv2.VideoCapture(video_url)
            if not cap.isOpened():
                return {"success": False, "error": "无法打开视频URL"}

            total_frames = video_info["total_frames"]
            random_frame_index = random.randint(0, total_frames - 1)

            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
            ret, frame = cap.read()
            cap.release()

            if not ret:
                return {"success": False, "error": f"无法读取帧 {random_frame_index}"}

            return {"success": True, "frame": frame, "frame_index": random_frame_index}

        return await asyncio.get_event_loop().run_in_executor(None, _extract)


async def main():
    """异步主函数示例"""
    # 创建检测器实例
    detector = QRDetector()

    # 在线视频链接示例
    video_url = "https://multimedia.nt.qq.com.cn:443/download?appid=1415&format=origin&orgfmt=t264&spec=0&client_proto=ntv2&client_appid=537290727&client_type=linux&client_ver=3.2.17-34740&client_down_type=auto&client_aio_type=aio&rkey=CAMSoAGKDKztJ3o-DuZWsqllLFaCETK5dfWJ69wEuQ1AC5EyZQ3a3zLuxXz50N35pxCqhZwNqfNJzu3cubFB59_LfSEr8DBQkkzxcJQTpbMv9Fk6GZUqTGS_OW_ijMu-PZjzYm6IX9T5tmTF6-eCUs3HiOucF7LJeccAKH4DSKS6Aqm_9tQpyXmef2LSgX-7xn7GOUjEkq0c_HiC87yKwE9QeFsi"

    # 验证URL格式
    if not detector._validate_url(video_url):
        logger.error(f"错误：无效的视频URL格式")
        return

    # 检查是否包含二维码
    result = await detector.detect_video_from_url(video_url)

    if result["success"]:
        logger.info(f"\n检测结果:")
        logger.info(f"  总帧数: {result['total_frames']}")
        logger.info(f"  抽取帧索引: {result['frame_index']}")
        logger.info(f"  包含二维码: {result['has_qr_code']}")
        if result["has_qr_code"]:
            logger.info(f"  二维码数量: {len(result['qr_codes'])}")

        # 显示保存的文件路径
        if "image_path" in result:
            logger.info(f"  保存的图片路径: {result['image_path']}")
        if "marked_image_path" in result:
            logger.info(f"  标记图片路径: {result['marked_image_path']}")
        if "save_error" in result:
            logger.info(f"  保存错误: {result['save_error']}")

    logger.info("\n完成！")
    logger.info(f"你可以在 '{detector.output_dir}' 文件夹中找到导出的图片。")
    logger.info("请确保安装了以下依赖：")
    logger.info("  pip install opencv-python")
    logger.info("  pip install pyzbar")


if __name__ == "__main__":
    asyncio.run(main())
