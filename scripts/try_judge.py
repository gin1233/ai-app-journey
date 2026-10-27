"""验证裁判模型能不能调通。

用法（在项目根目录下）：
    python -m scripts.try_judge
"""

from openai import OpenAI

from app.config import get_config


def main() -> None:
    api_key = get_config("JUDGE_API_KEY")
    base_url = get_config("JUDGE_BASE_URL")
    model = get_config("JUDGE_MODEL")

    print(f"base_url : {base_url}")
    print(f"model    : {model}")
    print(f"api_key  : {'已配置' if api_key else '❌ 空'}")
    print()

    if not api_key:
        print("❌ .env 里没有 JUDGE_API_KEY")
        return

    client = OpenAI(api_key=api_key, base_url=base_url or None)

    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你是哪个公司开发的模型？只回答公司名。"}],
        )
        print("✅ 调用成功：", r.choices[0].message.content)
    except Exception as e:
        print(f"❌ 失败：{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
