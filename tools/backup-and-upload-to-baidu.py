import os
import tarfile
import requests
from ..app.config import FEISHU_BOT_URL, FEISHU_BOT_SECRET
import time
import subprocess
import datetime
import logging
import re
import hmac
import hashlib
import base64

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_feishu_notification(title: str, content: str):
    """
    发送飞书通知，带签名验证
    参数:
        title: 消息标题
        content: 消息内容
    """
    if not FEISHU_BOT_URL or not FEISHU_BOT_SECRET:
        logging.error("飞书机器人URL或SECRET未配置")
        return

    # 生成时间戳和签名
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{FEISHU_BOT_SECRET}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建消息内容 - 使用富文本格式
    msg = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [[{"tag": "text", "text": content}]],
                }
            }
        },
    }

    try:
        response = requests.post(FEISHU_BOT_URL, headers=headers, json=msg)
        if response.json().get("code") == 0:
            logging.info("飞书通知发送成功")
            return response.json()
        else:
            logging.error(
                f"飞书通知发送失败，状态码: {response.status_code}，错误信息: {response.json()}"
            )
            return response.json()
    except Exception as e:
        logging.error(f"飞书通知发送异常: {e}")
        return {"error": str(e)}


def check_command_exists(command):
    """检查命令是否存在"""
    try:
        # 对于Windows和Unix系统使用不同的检查方法
        if os.name == "nt":  # Windows
            result = subprocess.run(
                f"where {command}", shell=True, capture_output=True, text=True
            )
            return result.returncode == 0
        else:  # Unix/Linux
            result = subprocess.run(
                f"which {command}", shell=True, capture_output=True, text=True
            )
            return result.returncode == 0
    except Exception:
        return False


def install_bypy():
    """安装bypy工具"""
    try:
        logger.info("正在安装bypy...")
        result = subprocess.run("pip install bypy", shell=True, check=True)
        logger.info("bypy安装成功！")
        logger.info("正在检查bypy是否可用...")

        # 用一个简单的命令测试bypy是否正常工作
        check_result = subprocess.run(
            "bypy --version", shell=True, capture_output=True, text=True
        )
        if check_result.returncode == 0:
            logger.info(f"bypy版本: {check_result.stdout.strip()}")
            logger.info("bypy已准备好使用！")
        else:
            logger.info("bypy安装成功，但可能需要重新打开终端才能使用。")
            logger.info("如果下一步出错，请关闭并重新打开终端，然后再次运行脚本。")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装失败: {e}")
        return False


def upload_file_to_baidu(local_file_path, remote_path="/"):
    """
    上传文件到百度网盘
    :param local_file_path: 本地文件路径
    :param remote_path: 百度网盘上的目标路径，默认为根目录
    :return: 上传结果和状态码(True/False)
    """
    # 检查bypy是否安装
    if not check_command_exists("bypy"):
        logger.info("未检测到bypy命令。")
        install_choice = input("是否安装bypy? (y/n): ").lower()
        if install_choice == "y":
            if not install_bypy():
                return "错误：bypy安装失败，无法继续上传", False
        else:
            return "错误：未安装bypy，无法继续上传", False

    if not os.path.exists(local_file_path):
        return f"错误：文件 {local_file_path} 不存在", False

    # 检查bypy是否已授权，添加超时机制
    logger.info("检查百度网盘授权状态...")
    try:
        # 使用超时机制避免命令无限等待
        auth_check = subprocess.run(
            "bypy info",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 设置30秒超时
        )
        logger.info(f"授权检查输出: {auth_check.stdout}")
        logger.info(f"授权检查错误: {auth_check.stderr}")

        if "授权" in auth_check.stderr or "authorize" in auth_check.stderr.lower():
            logger.info("bypy需要授权，正在启动授权流程...")
            logger.info("请手动运行以下命令并按照提示完成授权:")
            logger.info("bypy info")
            proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
            if proceed.lower() != "y":
                return "用户取消了操作", False
        else:
            logger.info("bypy已授权，可以继续上传操作")

    except subprocess.TimeoutExpired:
        logger.info("授权检查超时。这可能意味着:")
        logger.info("1. bypy正在等待授权")
        logger.info("2. 网络连接问题")
        logger.info("请手动运行'bypy info'命令完成授权")
        proceed = input("授权完成后，输入'y'继续，输入其他退出: ")
        if proceed.lower() != "y":
            return "用户取消了操作", False

    # 执行上传命令
    command = f"bypy upload {local_file_path} {remote_path}"
    try:
        logger.info(f"开始上传: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10分钟超时
        )

        output = result.stdout
        logger.info(f"上传命令输出: {output}")

        # 检查常见错误
        # 1. 检查是否有明确的错误码
        if "Error" in output or "error" in output.lower() or "错误" in output:
            error_match = re.search(r"Error\s+(\d+)", output)
            if error_match:
                error_code = error_match.group(1)
                return f"上传失败：遇到错误代码 {error_code}，请检查百度网盘状态", False
            else:
                return f"上传失败：{output}", False

        # 2. 特别检查文件名包含非法字符的错误
        if (
            "非法字符" in output
            or "illegal character" in output.lower()
            or "冒号" in output
        ):
            return (
                f"上传失败：文件名包含非法字符 (可能是冒号)，请修改文件名后重试",
                False,
            )

        # 3. 检查成功标志 - 扩展成功判断条件
        success_indicators = [
            "上传文件完成",
            "Upload completed",
            "upload total size",
            "100%",
            "completed: 1",
        ]

        for indicator in success_indicators:
            if indicator in output:
                return f"上传成功：\n{output}", True

        # 4. 检查默认成功标志
        if result.returncode == 0 and not (
            "Error" in output or "error" in output.lower()
        ):
            # 如果返回码是0，并且没有错误关键字，通常也认为是成功的
            return f"上传可能成功，请检查百度网盘确认：\n{output}", True

        # 如果没有匹配任何条件，返回不确定结果
        return f"上传结果不确定，请检查百度网盘：\n{output}", False

    except subprocess.TimeoutExpired:
        return "上传操作超时，请检查网络连接或文件大小", False
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr
        logger.error(f"上传失败，错误输出: {stderr_output}")

        # 检查授权问题
        if "授权" in stderr_output or "authorize" in stderr_output.lower():
            logger.info("需要进行百度网盘授权，请手动运行以下命令:")
            logger.info("bypy info")
            logger.info("并按照提示完成授权")
            proceed = input("授权完成后，输入'y'重试上传，输入其他退出: ")
            if proceed.lower() == "y":
                try:
                    # 重试上传
                    retry_result = subprocess.run(
                        command,
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=600,
                    )

                    retry_output = retry_result.stdout
                    logger.info(f"重试上传命令输出: {retry_output}")

                    # 使用相同的成功判断逻辑
                    if (
                        "Error" in retry_output
                        or "error" in retry_output.lower()
                        or "错误" in retry_output
                    ):
                        error_match = re.search(r"Error\s+(\d+)", retry_output)
                        if error_match:
                            error_code = error_match.group(1)
                            return f"重试上传失败：遇到错误代码 {error_code}", False
                        else:
                            return f"重试上传失败：{retry_output}", False

                    # 检查成功标志
                    success_indicators = [
                        "上传文件完成",
                        "Upload completed",
                        "upload total size",
                        "100%",
                        "completed: 1",
                    ]

                    for indicator in success_indicators:
                        if indicator in retry_output:
                            return f"授权成功，上传完成：\n{retry_output}", True

                    # 默认成功判断
                    if retry_result.returncode == 0 and not (
                        "Error" in retry_output or "error" in retry_output.lower()
                    ):
                        return (
                            f"授权成功，上传可能成功，请检查百度网盘确认：\n{retry_output}",
                            True,
                        )

                    # 未知结果
                    return (
                        f"重试上传结果不确定，请检查百度网盘：\n{retry_output}",
                        False,
                    )

                except subprocess.CalledProcessError as retry_e:
                    return f"重试上传失败：{retry_e.stderr}", False
                except subprocess.TimeoutExpired:
                    return "重试上传操作超时", False
            else:
                return "用户取消了操作", False

        # 检查文件名错误
        if (
            "非法字符" in stderr_output
            or "illegal character" in stderr_output.lower()
            or "冒号" in stderr_output
        ):
            return (
                f"上传失败：文件名包含非法字符 (可能是冒号)，请修改文件名后重试",
                False,
            )

        # 其他错误
        return f"上传失败：{stderr_output}", False


def delete_old_backups(remote_dir: str, days_to_keep: int = 7):
    """
    删除百度网盘指定目录下超过指定天数的备份文件。
    文件名格式需为 backup_data_and_logs_YYYY-MM-DD.tar.gz
    """
    logger.info(
        f"开始检查并删除百度网盘 {remote_dir} 目录下超过 {days_to_keep} 天的备份文件..."
    )

    # 检查bypy命令是否存在
    if not check_command_exists("bypy"):
        logger.error("未检测到bypy命令，无法执行删除操作。")
        return [], ["bypy命令未找到"]  # deleted_files, errors

    # 步骤 1: 列出远程目录中的文件
    list_command = f"bypy list {remote_dir}"
    try:
        # 增加超时以防bypy卡住
        list_result = subprocess.run(
            list_command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,  # Check manually because bypy list can return non-zero for empty dir on some versions
            timeout=120,  # 2 minutes timeout for listing
        )

        if list_result.returncode != 0:
            # bypy list 可能会因目录为空或其他问题返回非零值。
            # 检查 stderr 中是否有关键错误，如授权问题。
            if (
                "授权" in list_result.stderr
                or "authorize" in list_result.stderr.lower()
                or "Please visit" in list_result.stderr
                or "请访问" in list_result.stderr
            ):
                logger.error(
                    f"bypy需要授权，无法列出文件。请手动运行 'bypy info' 完成授权。错误: {list_result.stderr}"
                )
                return [], [f"bypy需要授权: {list_result.stderr}"]
            # 如果不是授权错误，但仍然非零，可能是空目录或其他非致命问题。
            # 如果 stderr 有内容，记录它。
            if list_result.stderr.strip():
                logger.warning(
                    f"bypy list 命令返回码 {list_result.returncode}，错误信息: {list_result.stderr.strip()}"
                )
            # 如果 stdout 也为空，则可能是空目录或出现问题。
            if not list_result.stdout.strip():
                logger.info(
                    f"bypy list 命令未返回任何文件列表或出错。标准输出为空。错误流: {list_result.stderr.strip()}"
                )
                # 如果 stdout 为空，则视为空目录，未找到文件
                return [], []

        logger.debug(f"bypy list 输出: \n{list_result.stdout}")

    except subprocess.TimeoutExpired:
        logger.error(f"列出百度网盘 '{remote_dir}' 文件超时。")
        return [], [f"列出 '{remote_dir}' 文件超时"]
    except (
        subprocess.CalledProcessError
    ) as e:  # 使用 check=False 时理论上不会发生，但作为良好实践保留
        logger.error(f"列出百度网盘 '{remote_dir}' 文件失败: {e.stderr}")
        return [], [f"列出 '{remote_dir}' 文件失败: {e.stderr}"]
    except Exception as e:  # 捕获列出过程中的任何其他意外错误
        logger.error(f"列出百度网盘 '{remote_dir}' 文件时发生未知错误: {e}")
        return [], [f"列出 '{remote_dir}' 文件时发生未知错误: {str(e)}"]

    files_to_delete = []
    # 用于查找类似 'backup_data_and_logs_2023-01-15.tar.gz' 的备份文件的正则表达式
    backup_file_pattern = re.compile(
        r"(backup_data_and_logs_(\d{4}-\d{2}-\d{2})\.tar\.gz)"
    )
    today = datetime.date.today()

    # 处理列表输出的每一行
    for line in list_result.stdout.splitlines():
        line_stripped = line.strip()
        # 搜索模式。bypy list 的输出中，文件名通常位于相关行部分的开头。
        match = backup_file_pattern.search(line_stripped)
        if match:
            filename = match.group(
                1
            )  # 完整文件名，例如 backup_data_and_logs_2023-01-15.tar.gz
            date_str = match.group(2)  # 日期部分，例如 2023-01-15
            try:
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                age = (today - file_date).days
                if age > days_to_keep:
                    files_to_delete.append(filename)
                    logger.info(
                        f"标记文件 {filename} (日期: {date_str}, 年龄: {age} 天) 为待删除。"
                    )
            except ValueError:
                logger.warning(
                    f"文件名 {filename} 中的日期格式 '{date_str}' 无效，跳过。"
                )

    if not files_to_delete:
        logger.info(
            f"在 {remote_dir} 目录没有找到符合删除条件的旧备份文件 (超过 {days_to_keep} 天)。"
        )
        return [], []

    logger.info(
        f"找到以下 {len(files_to_delete)} 个超过 {days_to_keep} 天的备份文件，将尝试删除: {files_to_delete}"
    )

    deleted_files_summary = []
    errors_summary = []

    for filename_to_delete in files_to_delete:
        # 构建完整的远程路径，确保如果 remote_dir 以 / 结尾时不会出现双斜杠
        full_remote_path = f"{remote_dir.rstrip('/')}/{filename_to_delete}"

        delete_command = f'bypy delete "{full_remote_path}"'  # bypy delete "remote_path" - 路径加引号更安全
        try:
            logger.info(f"正在删除百度网盘文件: {full_remote_path}...")
            delete_op_result = subprocess.run(
                delete_command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,  # 手动检查返回码
                timeout=180,  # 3 分钟删除超时
            )

            if delete_op_result.returncode == 0:
                # bypy delete 成功时通常很安静，或向 stdout 输出最少信息
                logger.info(
                    f"成功删除文件 {filename_to_delete}. 标准输出: {delete_op_result.stdout.strip()}"
                )
                deleted_files_summary.append(filename_to_delete)
            else:
                # 删除失败
                error_message = (
                    delete_op_result.stderr.strip()
                    or delete_op_result.stdout.strip()
                    or "未知错误"
                )
                logger.error(
                    f"删除文件 {filename_to_delete} 失败. 返回码: {delete_op_result.returncode}. 错误: {error_message}"
                )
                errors_summary.append(
                    f"删除 {filename_to_delete} 失败: {error_message}"
                )

        except subprocess.TimeoutExpired:
            logger.error(f"删除文件 {filename_to_delete} 超时。")
            errors_summary.append(f"删除 {filename_to_delete} 超时")
        except Exception as e:  # 捕获删除过程中的任何其他意外错误
            logger.error(f"删除文件 {filename_to_delete} 时发生未知错误: {e}")
            errors_summary.append(f"删除 {filename_to_delete} 时发生未知错误: {str(e)}")

    if deleted_files_summary:
        logger.info(f"成功删除 {len(deleted_files_summary)} 个旧备份文件。")
    if errors_summary:
        logger.error(f"删除旧备份文件过程中发生 {len(errors_summary)} 个错误。")

    return deleted_files_summary, errors_summary


def backup_data_and_logs():
    """备份数据和日志"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建app目录的路径 (上一级目录的app子目录)
    app_dir = os.path.abspath(os.path.join(script_dir, "..", "app"))

    try:
        # 进入app目录
        logger.info(f"尝试进入目录: {app_dir}")
        os.chdir(app_dir)
    except Exception as e:
        logger.error(f"目录 {app_dir} 不存在或无法访问: {e}")
        return False

    # 检查data和logs目录是否存在
    if not os.path.exists("data") or not os.path.exists("logs"):
        logger.error("data 或 logs 目录不存在")
        return False

    # 获取当前日期，只使用年月日，不使用冒号和时分秒
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # 如果需要包含时间但不使用冒号，可以用下面的格式
    # current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_name = f"backup_data_and_logs_{current_date}.tar.gz"

    try:
        # 打包data和logs目录
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add("data")
            tar.add("logs")
        logger.info(f"打包成功: {archive_name}")

        # 获取文件完整路径
        archive_path = os.path.abspath(archive_name)
        return archive_path
    except Exception as e:
        logger.error(f"打包失败: {str(e)}")
        return False


def main():
    # 步骤1: 备份数据和日志
    archive_path = backup_data_and_logs()
    if not archive_path:
        send_feishu_notification("W1ndysBot备份失败", "备份数据和日志失败")
        return

    # 步骤2: 上传到百度网盘
    remote_dir = "/W1ndysBot/"
    file_name = os.path.basename(archive_path)
    remote_file_path = f"{remote_dir}{file_name}"  # 构造完整的远程文件路径用于上传

    result_message, success = upload_file_to_baidu(
        archive_path, remote_file_path
    )  # 传递完整远程文件路径

    # 检查百度网盘上是否有该文件 (通过列出目录来验证)
    # 此验证步骤在 upload_file_to_baidu 内部的成功判断之外，作为额外的确认
    if success:  # 仅当 upload_file_to_baidu 报告某种形式的成功时才进行验证
        verify_command = f"bypy list {remote_dir}"
        try:
            verify_result = subprocess.run(
                verify_command, shell=True, capture_output=True, text=True, timeout=30
            )

            # 如果文件名出现在列表中，则确认上传成功
            if file_name in verify_result.stdout:
                # success 保持 True
                result_message = (
                    f"文件已成功上传到百度网盘并已验证存在\n{result_message}"
                )
                logger.info(f"已验证文件 {file_name} 存在于百度网盘")
            # else:
            # 如果 upload_file_to_baidu 认为成功，但验证未找到文件，这里可以考虑是否更改 success 状态
            # 当前逻辑：验证失败不改变 success 状态，仅记录警告
            # logger.warning(f"上传后验证失败：文件 {file_name} 未在 {remote_dir} 找到。")
        except Exception as e:
            logger.warning(f"验证文件是否上传成功时出错: {e}")
            # 继续处理，不改变原有的成功标志

    # 步骤 2.5: 删除7天前的旧备份
    deleted_files_report = ""
    if success:  # 只有在当前备份成功上传后才尝试删除旧备份
        logger.info("当前备份上传成功，开始清理旧备份...")
        # 默认删除7天前的备份
        deleted_files, delete_errors = delete_old_backups(remote_dir, days_to_keep=7)

        if deleted_files:
            deleted_files_report += (
                f"\n已成功删除以下 {len(deleted_files)} 个旧备份文件:\n"
                + "\n".join(deleted_files)
            )
        if delete_errors:
            deleted_files_report += (
                f"\n删除旧备份文件时遇到 {len(delete_errors)} 个错误:\n"
                + "\n".join(delete_errors)
            )
        if not deleted_files and not delete_errors:
            # 如果没有文件被删除，也没有错误，可以添加一条信息
            deleted_files_report += (
                "\n没有找到需要删除的旧备份文件，或清理过程中未发生错误。"
            )
        elif not deleted_files and delete_errors:
            # 如果没有文件被删除，但有错误（例如列出文件失败）
            deleted_files_report += "\n未删除任何旧备份文件，清理过程中发生错误。"

    # 步骤3: 发送飞书通知
    if success:
        feishu_title = f"W1ndysBot备份数据上传百度网盘成功"
        feishu_content = f"文件名: {file_name}\n备份上传状态: {result_message}"
        feishu_content += deleted_files_report  # 添加旧备份删除信息

        send_feishu_notification(
            feishu_title,
            feishu_content,
        )
        # 删除本地文件
        try:
            os.remove(archive_path)
            logger.info(f"本地文件 {archive_path} 已删除")
        except Exception as e:
            logger.error(f"删除本地文件失败: {e}")
    else:
        send_feishu_notification(
            "W1ndysBot备份数据上传百度网盘失败",
            f"文件名: {file_name}\n失败原因: {result_message}",
        )
        logger.error(f"上传失败，保留本地文件: {archive_path}")


if __name__ == "__main__":
    main()
