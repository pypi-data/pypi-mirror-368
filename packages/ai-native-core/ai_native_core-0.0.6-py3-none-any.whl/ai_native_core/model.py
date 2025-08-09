import os

from langchain.chat_models import init_chat_model

chat_model_default_base_url = os.getenv('CHAT_MODEL_DEFAULT_BASE_URL')
chat_model_default_api_key = os.getenv('CHAT_MODEL_DEFAULT_API_KEY')

last_model = init_chat_model(
    model="Qwen3-30B-A3B-FP8",  # default model
    model_provider="openai",  # 使用配置文件中的值
    base_url=chat_model_default_base_url,  # 使用配置文件中的值
    api_key=chat_model_default_api_key,
    temperature=0.7,
    top_p=0.8,
    max_tokens=512,
    presence_penalty=1.5,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
    configurable_fields=(  # 可以动态配置传入的参数
        "model",
        "model_provider",
        "temperature",
        "max_tokens",
        "api_key",
        "base_url",
        "extra_body"
    ),
    config_prefix="last",
    tags=["last_model"],
)

# 主模型（knowledge_rerank_model）调用失败时，自动切换到备用模型，保证模型的可用性
knowledge_rerank_model = init_chat_model(
    model="Qwen3-30B-A3B-FP8",
    model_provider="openai",  # 使用配置文件中的值
    base_url=chat_model_default_base_url,  # 使用配置文件中的值
    api_key=chat_model_default_api_key,
    temperature=0.7,
    top_p=0.8,
    max_tokens=512,
    presence_penalty=1.5,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
    configurable_fields=(  # 可以动态配置传入的参数
        "model",
        "model_provider",
        "temperature",
        "max_tokens",
        "api_key",
        "base_url",
        "extra_body"
    ),
    config_prefix="knowledge_rerank",
    tags=["knowledge_rerank_model"],
    disable_streaming=False
).with_fallbacks(
    [last_model],  # fallback to last_model if knowledge_rerank_model fails
)

agent_model = knowledge_rerank_model