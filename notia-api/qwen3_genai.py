import openvino_genai as ov_genai
import sys

model_dir = r'C:\Users\zangq\Repo\model\OpenVINO\Qwen3-1.7B-int4-ov'
print(f"Loading model from {model_dir}\n")


pipe = ov_genai.LLMPipeline(str(model_dir), 'CPU')

generation_config = ov_genai.GenerationConfig()
generation_config.max_new_tokens = 32768


def streamer(subword):
    print(subword, end="", flush=True)
    sys.stdout.flush()
    # Return flag corresponds whether generation should be stopped.
    # False means continue generation.
    return False


input_prompt = '''
你好
'''
print(f"Input text: {input_prompt}")
result = pipe.generate(input_prompt, generation_config, streamer)