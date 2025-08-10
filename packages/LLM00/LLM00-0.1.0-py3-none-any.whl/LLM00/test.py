
# シンプルなLLMインターフェース [LLM00]
# 【動作確認 / 使用例】

import sys
import ezpip
LLM00 = ezpip.load_develop("LLM00", "../", develop_flag = True)

print(LLM00("ずばり簡潔に、タコの足は何本？"))	# AIへの問いかけ [LLM00]
