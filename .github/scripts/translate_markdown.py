#!/usr/bin/env python3
"""
Hugo Markdown 翻译脚本
功能：
1. 自动翻译中文 Markdown 文件为英文
2. 保留所有 Markdown 格式和 Front Matter
3. 生成对应的 *_en.md 文件
"""

import os
import sys
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TranslationError(Exception):
    """自定义翻译异常类"""

    pass


def init_client():
    """初始化 XAI 客户端"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY 未在环境变量中设置")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )


def translate_text(client, text, max_retries=3):
    """使用 XAI Grok API 翻译文本"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位专业的翻译专家，请将以下中文技术内容翻译为英文。要求：
1. 保持所有 Markdown 格式、代码块、链接和特殊标记不变
2. 技术术语保持准确
3. 语言自然流畅符合英文表达习惯
4. 保留所有换行和空格格式""",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            return response.choices[0].message.content

        except Exception as e:
            if attempt == max_retries - 1:
                raise TranslationError(f"翻译失败，已达最大重试次数：{str(e)}")
            wait_time = (attempt + 1) * 5
            print(
                f"⚠️ 翻译出错，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})"
            )
            time.sleep(wait_time)


def process_front_matter(front_matter):
    """处理 Front Matter 中的多语言字段"""
    if not front_matter:
        return ""

    replacements = [
        ("lang: zh", "lang: en"),
        ("language: zh", "language: en"),
        ("language: zh-CN", "language: en-US"),
        ("title: ", "title_en: "),
        ("description: ", "description_en: "),
    ]

    for old, new in replacements:
        front_matter = front_matter.replace(old, new)

    return front_matter


def split_front_matter(content):
    """分割 Front Matter 和内容主体"""
    front_matter_pattern = r"^---\n(.*?\n)---\n"
    match = re.match(front_matter_pattern, content, re.DOTALL)

    if match:
        return match.group(0), content[match.end() :]
    return "", content


def validate_file_path(file_path):
    """验证并规范化文件路径"""
    # 转换为绝对路径
    file_path = os.path.abspath(os.path.expanduser(file_path))

    # 基础验证
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"路径不是文件：{file_path}")
    if not file_path.lower().endswith(".md"):
        raise ValueError(f"非 Markdown 文件：{file_path}")

    return file_path


def process_markdown(file_path):
    """处理单个 Markdown 文件"""
    try:
        # 验证并规范化路径
        file_path = validate_file_path(file_path)
        print(f"\n🔍 开始处理：{file_path}")

        # 检查是否已翻译文件
        if file_path.lower().endswith("_en.md"):
            print("⏩ 跳过已翻译文件")
            return None

        # 准备输出路径
        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        base, ext = os.path.splitext(basename)
        translated_path = os.path.join(dirname, f"{base}_en{ext}")

        # 检查翻译是否最新
        if os.path.exists(translated_path):
            if os.path.getmtime(translated_path) >= os.path.getmtime(file_path):
                print("✅ 翻译已是最新")
                return None

        # 初始化客户端
        client = init_client()

        # 读取内容
        print("📖 读取文件内容...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 处理 Front Matter
        front_matter, content_body = split_front_matter(content)
        processed_front_matter = process_front_matter(front_matter)

        # 翻译正文
        print("🌐 开始翻译内容...")
        start_time = time.time()
        translated_body = translate_text(client, content_body)
        elapsed = time.time() - start_time
        print(f"🔄 翻译完成 (耗时：{elapsed:.2f}s)")

        # 组合内容
        translated_content = (
            (processed_front_matter + translated_body)
            if processed_front_matter
            else translated_body
        )

        # 确保目录存在
        os.makedirs(dirname, exist_ok=True)

        # 写入文件
        print(f"💾 保存到：{translated_path}")
        with open(translated_path, "w", encoding="utf-8") as f:
            f.write(translated_content)

        print(f"🎉 翻译完成：{translated_path}")
        return translated_path

    except Exception as e:
        print(f"\n❌ 处理失败：{type(e).__name__}: {str(e)}", file=sys.stderr)
        raise


def main():
    if len(sys.argv) < 2:
        print("❌ 错误：请提供要翻译的文件路径", file=sys.stderr)
        print(f"用法：{sys.argv[0]} <markdown 文件路径>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        result = process_markdown(file_path)
        if result and "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print(f"translated_file={result}", file=fh)
        sys.exit(0)
    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    main()
