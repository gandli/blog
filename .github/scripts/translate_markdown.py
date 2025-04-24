import os
import sys
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TranslationError(Exception):
    """自定义翻译异常类"""
    pass

def init_client():
    """初始化XAI客户端"""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key:
        raise ValueError("XAI_API_KEY 未在环境变量中设置")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )

def translate_text(client, text, max_retries=3):
    """使用XAI Grok API翻译文本"""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一位专业的翻译专家，请将以下中文技术内容翻译为英文。要求：
1. 保持所有Markdown格式、代码块、链接和特殊标记不变
2. 技术术语保持准确
3. 语言自然流畅符合英文表达习惯
4. 保留所有换行和空格格式"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise TranslationError(f"翻译失败，已达最大重试次数: {str(e)}")
            wait_time = (attempt + 1) * 5
            print(f"⚠️ 翻译出错，{wait_time}秒后重试... (尝试 {attempt + 1}/{max_retries})")
            time.sleep(wait_time)

def process_front_matter(front_matter):
    """处理Front Matter中的多语言字段"""
    if front_matter:
        front_matter = front_matter.replace('lang: zh', 'lang: en')
        front_matter = front_matter.replace('language: zh', 'language: en')
        front_matter = front_matter.replace('language: zh-CN', 'language: en-US')
    return front_matter

def split_front_matter(content):
    """分割Front Matter和内容主体"""
    front_matter_pattern = r'^---\n(.*?\n)---\n'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if match:
        return match.group(0), content[match.end():]
    return "", content

def process_markdown(file_path):
    """处理单个Markdown文件"""
    try:
        file_path = os.path.normpath(file_path)
        print(f"\n🔍 开始处理: {repr(file_path)}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if file_path.endswith('_en.md'):
            print("⏩ 跳过已翻译文件")
            return None
        
        base, ext = os.path.splitext(file_path)
        translated_path = f"{base}_en{ext}"
        
        if os.path.exists(translated_path):
            if os.path.getmtime(translated_path) >= os.path.getmtime(file_path):
                print("✅ 翻译已是最新")
                return None

        client = init_client()
        
        print("📖 读取文件内容...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        front_matter, content_body = split_front_matter(content)
        processed_front_matter = process_front_matter(front_matter)
        
        print("🌐 开始翻译内容...")
        start_time = time.time()
        translated_body = translate_text(client, content_body)
        print(f"🔄 翻译完成 (耗时: {time.time() - start_time:.2f}s)")
        
        translated_content = (processed_front_matter + translated_body) if processed_front_matter else translated_body
        
        os.makedirs(os.path.dirname(translated_path), exist_ok=True)
        
        print("💾 保存翻译文件...")
        with open(translated_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        print(f"🎉 翻译完成: {translated_path}")
        return translated_path
        
    except Exception as e:
        print(f"\n❌ 处理失败: {str(e)}", file=sys.stderr)
        raise

def main():
    if len(sys.argv) < 2:
        print("❌ 错误: 请提供要翻译的文件路径", file=sys.stderr)
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        result = process_markdown(file_path)
        if result and 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print(f"translated_file={result}", file=fh)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()
