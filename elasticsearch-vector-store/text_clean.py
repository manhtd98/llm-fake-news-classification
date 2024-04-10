import unicodedata
import regex as re
import json


def text_processing_document(s: str) -> str:
    # with open("rules_base.json", "r") as f:
    #     rules = json.load(f)
    text_clean = " ".join(s.split()).strip()
    # for key in rules:
    #     text_clean.replace(key['keyword'], key['word'])
    #     text_clean.replace(key['keyword'].lower(), key['word'].lower())
    return text_clean


def text_processing(s: str) -> str:
    return " ".join(s.split()).strip().lower()


def bang_nguyen_am():
    bang_nguyen_am = [
        ["a", "à", "á", "ả", "ã", "ạ", "a"],
        ["ă", "ằ", "ắ", "ẳ", "ẵ", "ặ", "aw"],
        ["â", "ầ", "ấ", "ẩ", "ẫ", "ậ", "aa"],
        ["e", "è", "é", "ẻ", "ẽ", "ẹ", "e"],
        ["ê", "ề", "ế", "ể", "ễ", "ệ", "ee"],
        ["i", "ì", "í", "ỉ", "ĩ", "ị", "i"],
        ["o", "ò", "ó", "ỏ", "õ", "ọ", "o"],
        ["ô", "ồ", "ố", "ổ", "ỗ", "ộ", "oo"],
        ["ơ", "ờ", "ớ", "ở", "ỡ", "ợ", "ow"],
        ["u", "ù", "ú", "ủ", "ũ", "ụ", "u"],
        ["ư", "ừ", "ứ", "ử", "ữ", "ự", "uw"],
        ["y", "ỳ", "ý", "ỷ", "ỹ", "ỵ", "y"],
    ]

    bang_ky_tu_dau = ["", "f", "s", "r", "x", "j"]
    nguyen_am_to_ids = {}

    for i in range(len(bang_nguyen_am)):
        for j in range(len(bang_nguyen_am[i]) - 1):
            nguyen_am_to_ids[bang_nguyen_am[i][j]] = (i, j)
    return nguyen_am_to_ids


def chuan_hoa_unicode(text):
    text = unicodedata.normalize("NFC", text)
    return text


def chuan_hoa_dau_tu_tieng_viet(word, nguyen_am_to_ids):
    if not is_valid_vietnam_word(word):
        return word

    chars = list(word)
    dau_cau = 0
    nguyen_am_index = []
    qu_or_gi = False
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x == -1:
            continue
        elif x == 9:  # check qu
            if index != 0 and chars[index - 1] == "q":
                chars[index] = "u"
                qu_or_gi = True
        elif x == 5:  # check gi
            if index != 0 and chars[index - 1] == "g":
                chars[index] = "i"
                qu_or_gi = True
        if y != 0:
            dau_cau = y
            chars[index] = bang_nguyen_am[x][0]
        if not qu_or_gi or index != 1:
            nguyen_am_index.append(index)
    if len(nguyen_am_index) < 2:
        if qu_or_gi:
            if len(chars) == 2:
                x, y = nguyen_am_to_ids.get(chars[1])
                chars[1] = bang_nguyen_am[x][dau_cau]
            else:
                x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                if x != -1:
                    chars[2] = bang_nguyen_am[x][dau_cau]
                else:
                    chars[1] = (
                        bang_nguyen_am[5][dau_cau]
                        if chars[1] == "i"
                        else bang_nguyen_am[9][dau_cau]
                    )
            return "".join(chars)
        return word

    for index in nguyen_am_index:
        x, y = nguyen_am_to_ids[chars[index]]
        if x == 4 or x == 8:  # ê, ơ
            chars[index] = bang_nguyen_am[x][dau_cau]
            return "".join(chars)

    if len(nguyen_am_index) == 2:
        if nguyen_am_index[-1] == len(chars) - 1:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
        else:
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    else:
        x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
        chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
    return "".join(chars)


def is_valid_vietnam_word(word, nguyen_am_to_ids):
    chars = list(word)
    nguyen_am_index = -1
    for index, char in enumerate(chars):
        x, y = nguyen_am_to_ids.get(char, (-1, -1))
        if x != -1:
            if nguyen_am_index == -1:
                nguyen_am_index = index
            else:
                if index - nguyen_am_index != 1:
                    return False
                nguyen_am_index = index
    return True


def chuan_hoa_dau_cau_tieng_viet(sentence):
    """
    The function `chuan_hoa_dau_cau_tieng_viet` takes a Vietnamese sentence as input, capitalizes the
    first letter of each sentence, and normalizes the accent marks on Vietnamese words within the
    sentence.
    @param sentence - The function `chuan_hoa_dau_cau_tieng_viet` seems to be designed to standardize
    the capitalization and accent marks of Vietnamese sentences. However, it seems that the function is
    missing the definition for `chuan_hoa_dau_tu_tieng_viet`, which
    @returns The function `chuan_hoa_dau_cau_tieng_viet` takes a sentence as input, capitalizes the
    first letter of each sentence, and then normalizes the accent marks in Vietnamese words. The
    function returns the modified sentence with the accent marks normalized.
    """
    sentence = ". ".join([i.strip().capitalize() for i in sentence.split(".")])
    words = sentence.split()
    for index, word in enumerate(words):
        cw = re.sub(r"(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)", r"\1/\2/\3", word).split("/")
        # print(cw)
        if len(cw) == 3:
            cw[1] = chuan_hoa_dau_tu_tieng_viet(cw[1])
        words[index] = "".join(cw)
    return " ".join(words)


def chuan_hoa_cau(text):
    """
    The function `chuan_hoa_cau` in Python is designed to normalize Vietnamese text by removing special
    characters and extra spaces.
    @param text - It looks like the function `chuan_hoa_cau` is designed to normalize Vietnamese text by
    removing special characters and extra spaces. To use this function, you can pass a string of
    Vietnamese text as the `text` parameter. The function will then clean up the text and return the
    normalized version
    @returns The function `chuan_hoa_cau` returns the input text after removing any characters that are
    not Vietnamese diacritics, punctuation marks, or whitespace, and then normalizing the whitespace by
    replacing multiple spaces with a single space and stripping any leading or trailing spaces.
    """
    text = re.sub(
        r"[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ%?.,;/-/)/(//:_]",
        " ",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tien_xu_li(text):
    text = chuan_hoa_unicode(text)
    text = chuan_hoa_dau_cau_tieng_viet(text)
    text = chuan_hoa_cau(text)

    return text


if __name__ == "__main__":
    res = tien_xu_li(
        "QUY ĐỔI GIỜ CHUẨN ĐỐI VỚI ĐÀO TẠO ĐẠI HỌC (BAO GỒM CẢ CÁC LỚP CHỈ HUY THAM MƯU KỸ THUẬT, CHỈ HUY QUẢN LÝ KỸ THUẬT, NGẮN HẠN). Đối với CÁC GIỜ GIẢNG THEO CHƯƠNG TRÌNH ĐÀO TẠO CHÍNH KHÓA như sau:Huấn luyện thực hành chiến thuật, diễn tập có bắn đạn thật, kiểm tra bắn đạn thật, ném lựu đạn thật, đánh thuốc nổ thật, vận hành trang thiết bị, phương tiện quân sự (xe tăng, thiết giáp, pháo tự hành, xe chuyên dụng, trạm ra đa) có đơn vị tính là 1 tiết tương ứng với 2 giờ chuẩn"
    )
    print(res)
