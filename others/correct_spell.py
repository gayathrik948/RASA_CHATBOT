# from textblob import TextBlob
#
# # python - m textblob.download_corpora
# message = "What are the regalatios applicabel for Background check"
# res = TextBlob(message)
# print(res.correct())
# # def fibonacci(n):
# #     a, b = 0, 1
# #     for i in range(n):
# #         yield a
# #         a, b = b, a + b
# #
#
# import re
#
# # text = "for the completion of course take 75 days, and they teach python"
# text = "for the completion of course take 120 days, and they teach python"
# pattern = r"(\d+)(?=\s+days)"
# match = re.search(pattern, text)
#
# if match:
#     num_days = match.group(1)
#     print(num_days)
# else:
#     print("No match found.")
#
#
# #
# # for fib in fibonacci(20):
# #     print(fib)
#
# def is_timely_filing_present(para_text: str):
#     """
#
#     :param para_text:
#     :return:
#     """
#     num_days = None
#     para_text = remove_special_characters(para_text)
#         if "timely filling" in para_text.lower()":
#             pattern = r"(\d+)(?=\s+days)"
#             match = re.search(pattern, para_text)
#             if match:
#                 num_days = match.group(1)
#
#     return num_days
