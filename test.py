from googletrans import Translator


def translate_text(text, target_language="en"):
    translator = Translator(service_urls=["translate.google.com"])
    result = translator.translate(text, dest=target_language)

    return result.text


def translate_kor_to_eng(text, target_language="en"):
    translator = Translator(service_urls=["translate.google.com"])
    result = translator.translate(text, dest=target_language)

    return result.text


def translate_eng_to_kor(text, target_language="en"):
    translator = Translator(service_urls=["translate.google.com"])
    result = translator.translate(text, dest=target_language)

    return result.text


print(translate_text("안녕"))
