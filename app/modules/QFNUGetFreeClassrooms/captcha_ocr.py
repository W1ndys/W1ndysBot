import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)


def get_ocr_res(cap_pic_bytes):  # 识别验证码
    res = ocr.classification(cap_pic_bytes)
    return res


if __name__ == "__main__":
    get_ocr_res("123")
