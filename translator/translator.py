from googletrans import Translator


# def translate_kor_to_eng(text, target_language="en"):
#     try:
#         translator = Translator(service_urls=["translate.google.com"])

#         result = translator.translate(text, lang_tgt=target_language)
#         return result
#     except Exception as e:
#         print(f"Error translating {text} from Korean to English: {e}")
#         return text


# def translate_eng_to_kor(text, target_language="ko"):
#     try:
#         translator = Translator(service_urls=["translate.google.com"])

#         result = translator.translate(text, lang_tgt=target_language)
#         return result
#     except Exception as e:
#         print(f"Error translating {text} from English to Korean: {e}")
#         return text


def translate_kor_to_eng(text, target_language="en"):
    translator = Translator(service_urls=["translate.google.com"])
    result = translator.translate(text, dest=target_language)

    return result.text


def translate_eng_to_kor(text, target_language="ko"):
    translator = Translator(service_urls=["translate.google.com"])
    result = translator.translate(text, dest=target_language)

    return result.text
