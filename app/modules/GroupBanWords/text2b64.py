import base64

print("违禁词Base64编码工具")
print("输入多行文本，输入空行完成当前编码")
print("输入'quit'或'exit'退出程序")
print("-" * 40)

while True:
    lines = []
    print("\n请输入文本内容（输入空行结束当前输入）：")

    while True:
        line = input()
        if line == "":
            break
        # 检查退出命令
        if line.lower() in ["quit", "exit"]:
            print("程序已退出")
            exit()
        lines.append(line)

    if not lines:  # 如果没有输入任何内容，继续下一轮
        continue

    # 拼接所有行，去除所有空白字符（包括空格、制表符、换行）
    text = "".join(lines).replace(" ", "").replace("\t", "")

    # base64编码
    encoded = base64.b64encode(text.encode("utf-8"))

    print(f"添加违禁样本 {encoded.decode('utf-8')}")
    print("-" * 40)
