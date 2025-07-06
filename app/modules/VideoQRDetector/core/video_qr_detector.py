import cv2
import random
import os
import numpy as np
import asyncio
from logger import logger

try:
    from pyzbar import pyzbar

    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


class VideoQRDetector:
    """
    视频二维码检测器类，支持从在线视频链接中抽取帧并检测二维码。
    """

    def __init__(self, output_dir="output_frames"):
        """
        初始化视频二维码检测器。

        Args:
            output_dir (str): 保存图片的目录
        """
        # 使用绝对路径确保目录创建成功
        self.output_dir = os.path.abspath(output_dir)
        # 注意：__init__ 不能是异步的，所以这里先不创建目录，在第一次使用时创建

        # 初始化 OpenCV QR 码检测器作为备用
        try:
            self.qr_detector = cv2.QRCodeDetector()
            self.opencv_qr_available = True
        except:
            self.opencv_qr_available = False

    def _validate_url(self, video_url):
        """
        验证视频URL是否有效。

        Args:
            video_url (str): 视频URL

        Returns:
            bool: URL是否有效
        """
        if not isinstance(video_url, str):
            return False

        return video_url.startswith(("http://", "https://"))

    async def _ensure_output_dir(self):
        """确保输出目录存在"""
        try:
            if not os.path.exists(self.output_dir):
                # 使用 asyncio 在线程池中执行阻塞操作
                await asyncio.get_event_loop().run_in_executor(
                    None, os.makedirs, self.output_dir
                )
                logger.info(f"创建输出目录：{self.output_dir}")
            else:
                logger.info(f"输出目录已存在：{self.output_dir}")
        except Exception as e:
            logger.error(f"创建输出目录失败：{e}")
            # 如果无法创建指定目录，使用当前目录
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
            # 这对于检测暗色主题下的白色背景二维码特别有效
            inverted = cv2.bitwise_not(gray)
            processed_images.append(("inverted_for_dark_mode", inverted))

            # 11. 暗色模式 + 对比度增强
            # 反转后应用CLAHE提高对比度
            inverted_clahe = clahe.apply(inverted)
            processed_images.append(("inverted_clahe", inverted_clahe))

            # 12. 暗色模式 + 自适应阈值
            # 反转后应用自适应阈值
            inverted_adaptive = cv2.adaptiveThreshold(
                inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(("inverted_adaptive", inverted_adaptive))

            # 13. 暗色模式 + Otsu阈值
            # 反转后应用Otsu阈值
            _, inverted_otsu = cv2.threshold(
                inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            processed_images.append(("inverted_otsu", inverted_otsu))

            return processed_images

        # 在线程池中执行图像处理
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
                    {
                        "data": qr_data,
                        "type": qr_type,
                        "points": pts,
                        "method": "pyzbar",
                    }
                )

            return results

        # 在线程池中执行二维码检测
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
                        {
                            "data": data,
                            "type": "QRCODE",
                            "points": pts,
                            "method": "opencv",
                        }
                    )
            except Exception as e:
                print(f"OpenCV QR 检测出错: {e}")

            return results

        # 在线程池中执行二维码检测
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
        """
        使用指定方法和预处理检测二维码的辅助函数
        """
        if detector_type == "pyzbar":
            results = await self.detect_qr_codes_pyzbar(image)
        else:
            results = await self.detect_qr_codes_opencv(image)

        for result in results:
            result["preprocess_method"] = method_name

        return results

    def _get_video_name(self, video_url):
        """
        从视频URL中提取视频名称。

        Args:
            video_url (str): 视频URL

        Returns:
            str: 视频名称
        """
        if not self._validate_url(video_url):
            return "invalid_url"

        # 从URL中提取文件名，如果无法提取则使用默认名称
        try:
            filename = video_url.split("/")[-1]
            # 移除URL参数
            if "?" in filename:
                filename = filename.split("?")[0]
            if "." in filename and len(filename.split(".")[0]) > 0:
                return filename.split(".")[0]
            else:
                return "online_video"
        except:
            return "online_video"

    async def extract_random_frame(self, video_url, save_image=True, mark_qr=True):
        """
        从在线视频中随机抽取一帧并保存为图片，同时检测二维码。

        Args:
            video_url (str): 在线视频链接
            save_image (bool): 是否保存图片
            mark_qr (bool): 是否保存标记了二维码的图片

        Returns:
            dict: 包含检测结果的字典
        """
        # 验证URL
        if not self._validate_url(video_url):
            logger.error(f"错误：无效的视频URL {video_url}")
            return {"success": False, "error": "无效的视频URL"}

        def _extract_frame():
            cap = cv2.VideoCapture(video_url)

            if not cap.isOpened():
                logger.error(f"错误：无法打开视频URL {video_url}")
                return None, {"success": False, "error": "无法打开视频URL"}

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                logger.error(f"错误：视频 {video_url} 不包含任何帧。")
                cap.release()
                return None, {"success": False, "error": "视频不包含任何帧"}

            random_frame_index = random.randint(0, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)

            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error(
                    f"错误：未能读取视频 {video_url} 中的随机帧 {random_frame_index}。"
                )
                return None, {"success": False, "error": "无法读取视频帧"}

            return frame, {
                "success": True,
                "frame_index": random_frame_index,
                "total_frames": total_frames,
            }

        # 确保输出目录存在
        await self._ensure_output_dir()

        # 在线程池中执行视频帧提取
        frame, result = await asyncio.get_event_loop().run_in_executor(
            None, _extract_frame
        )

        if not result["success"] or frame is None:
            return result

        # 检测二维码
        qr_results = await self.detect_qr_codes(frame)

        result.update(
            {
                "has_qr_code": len(qr_results) > 0,
                "qr_codes": qr_results,
            }
        )

        if save_image and frame is not None:
            video_name = self._get_video_name(video_url)
            output_filename = f"frame_{video_name}_{result['frame_index']}.jpg"
            output_path = os.path.join(self.output_dir, output_filename)

            # 异步保存图片
            try:

                def _save_image():
                    return cv2.imwrite(output_path, frame)

                success = await asyncio.get_event_loop().run_in_executor(
                    None, _save_image
                )

                if success:
                    result["image_path"] = output_path
                    logger.info(
                        f"成功导出随机帧 {result['frame_index']} 到：{output_path}"
                    )
                    # 验证文件是否真的存在
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        logger.info(f"文件大小：{file_size} 字节")
                    else:
                        logger.warning(f"警告：文件保存后未找到：{output_path}")
                else:
                    logger.error(f"错误：无法保存图片到 {output_path}")
                    result["save_error"] = "cv2.imwrite 返回 False"
            except Exception as e:
                logger.error(f"保存图片时发生错误：{e}")
                result["save_error"] = str(e)

        if qr_results:
            logger.info(f"\n🔍 在图片中检测到 {len(qr_results)} 个二维码：")
            for i, qr_info in enumerate(qr_results, 1):
                logger.info(f"  二维码 {i}:")
                logger.info(f"    类型: {qr_info['type']}")
                logger.info(f"    内容: {qr_info['data']}")
                logger.info(f"    位置: {qr_info['points']}")

            # 可选：在图片上标记二维码位置并保存
            if save_image and mark_qr and frame is not None:

                def _create_marked_image():
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
                    return frame_with_qr

                frame_with_qr = await asyncio.get_event_loop().run_in_executor(
                    None, _create_marked_image
                )

                # 保存标记了二维码的图片
                video_name = self._get_video_name(video_url)
                marked_filename = (
                    f"frame_{video_name}_{result['frame_index']}_marked.jpg"
                )
                marked_path = os.path.join(self.output_dir, marked_filename)

                try:

                    def _save_marked_image():
                        return cv2.imwrite(marked_path, frame_with_qr)

                    success = await asyncio.get_event_loop().run_in_executor(
                        None, _save_marked_image
                    )

                    if success:
                        result["marked_image_path"] = marked_path
                        logger.info(f"已保存标记二维码的图片到：{marked_path}")
                        # 验证文件是否真的存在
                        if os.path.exists(marked_path):
                            file_size = os.path.getsize(marked_path)
                            logger.info(f"标记图片文件大小：{file_size} 字节")
                    else:
                        logger.error(f"错误：无法保存标记图片到 {marked_path}")
                except Exception as e:
                    logger.error(f"保存标记图片时发生错误：{e}")
        else:
            logger.error("❌ 未在图片中检测到二维码")

        return result

    async def has_qr_code(self, video_url, num_samples=3):
        """
        检查在线视频是否包含二维码。

        Args:
            video_url (str): 在线视频链接
            num_samples (int): 采样帧数，默认检查3帧

        Returns:
            bool: 如果在任何一帧中检测到二维码则返回True
        """
        # 验证URL
        if not self._validate_url(video_url):
            logger.error(f"错误：无效的视频URL {video_url}")
            return False

        def _sample_frames():
            cap = cv2.VideoCapture(video_url)

            if not cap.isOpened():
                logger.error(f"错误：无法打开视频URL {video_url}")
                return []

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                logger.error(f"错误：视频 {video_url} 不包含任何帧。")
                cap.release()
                return []

            # 随机采样多帧进行检测
            sample_frames = random.sample(
                range(total_frames), min(num_samples, total_frames)
            )

            frames = []
            for frame_index in sample_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ret, frame = cap.read()

                if ret:
                    frames.append((frame_index, frame))

            cap.release()
            return frames

        # 在线程池中执行视频帧采样
        frames = await asyncio.get_event_loop().run_in_executor(None, _sample_frames)

        if not frames:
            return False

        # 并发检测所有采样帧
        detection_tasks = []
        for frame_index, frame in frames:
            task = self._check_frame_for_qr(frame_index, frame)
            detection_tasks.append(task)

        results = await asyncio.gather(*detection_tasks)

        # 检查是否有任何帧包含二维码
        for frame_index, has_qr in results:
            if has_qr:
                logger.info(f"✅ 在第 {frame_index} 帧检测到二维码")
                return True

        logger.error(f"❌ 在 {len(frames)} 个采样帧中未检测到二维码")
        return False

    async def _check_frame_for_qr(self, frame_index, frame):
        """
        检查单个帧是否包含二维码的辅助函数
        """
        qr_results = await self.detect_qr_codes(frame)
        return frame_index, len(qr_results) > 0


async def main():
    """异步主函数示例"""
    # 创建检测器实例
    detector = VideoQRDetector()

    # 在线视频链接示例
    video_url = "https://multimedia.nt.qq.com.cn:443/download?appid=1415&format=origin&orgfmt=t264&spec=0&client_proto=ntv2&client_appid=537290727&client_type=linux&client_ver=3.2.17-34740&client_down_type=auto&client_aio_type=aio&rkey=CAMSoAGKDKztJ3o-DuZWsqllLFaCETK5dfWJ69wEuQ1AC5EyZQ3a3zLuxXz50N35pxCqhZwNqfNJzu3cubFB59_LfSEr8DBQkkzxcJQTpbMv9Fk6GZUqTGS_OW_ijMu-PZjzYm6IX9T5tmTF6-eCUs3HiOucF7LJeccAKH4DSKS6Aqm_9tQpyXmef2LSgX-7xn7GOUjEkq0c_HiC87yKwE9QeFsi"

    # 验证URL格式
    if not detector._validate_url(video_url):
        logger.error(f"错误：无效的视频URL格式")
        return

    # 检查是否包含二维码
    has_qr = await detector.has_qr_code(video_url)
    logger.info(f"\n视频是否包含二维码: {has_qr}")

    # 抽取随机帧并检测二维码
    result = await detector.extract_random_frame(video_url)

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
