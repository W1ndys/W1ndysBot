import base64

lines = []
print("请输入多行文本，输入空行结束：")
while True:
    line = input()
    if line == '':
        break
    lines.append(line)

# 拼接所有行，去除所有空白字符（包括空格、制表符、换行）
text = ''.join(lines).replace(' ', '').replace('\t', '')

# base64编码
encoded = base64.b64encode(text.encode('utf-8'))
print("Base64编码结果：")
print(f"添加违禁样本 {encoded.decode('utf-8')}")
