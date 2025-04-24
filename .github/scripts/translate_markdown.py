import os
import sys
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def translate_text(text):
    """使用 OpenAI API 翻译文本"""
    client = OpenAI(
      api_key=os.getenv('XAI_API_KEY'),
      base_url="https://api.x.ai/v1",
    )
    
    response = client.chat.completions.create(
        model="grok-3-beta",
        messages=[
            {
                "role": "system",
                "content": "你是一位专业的翻译专家，擅长将中文技术博客翻译为自然流畅的英文。请保持Markdown格式不变，只翻译文本内容。特别注意保留代码块、链接和特殊标记不变。"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def process_markdown(file_path):
    """处理单个Markdown文件"""
    try:
        # 规范化文件路径
        file_path = os.path.abspath(file_path)
        print(f"🛠️ 正在处理文件: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 跳过已翻译的文件
        if file_path.endswith('_en.md'):
            print(f"⏩ 跳过已翻译文件: {file_path}")
            return
        
        # 生成翻译后的文件名
        base, ext = os.path.splitext(file_path)
        translated_path = f"{base}_en{ext}"
        
        # 检查是否需要翻译
        if os.path.exists(translated_path) and \
           os.path.getmtime(translated_path) >= os.path.getmtime(file_path):
            print(f"✅ 翻译已是最新: {file_path}")
            return
        
        print(f"📖 读取文件内容: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 分割Front Matter和内容
        front_matter, content_body = split_front_matter(content)
        
        print("🌐 开始翻译内容...")
        translated_body = translate_text(content_body)
        
        # 组合翻译结果
        translated_content = front_matter + translated_body if front_matter else translated_body
        
        # 确保目录存在
        os.makedirs(os.path.dirname(translated_path), exist_ok=True)
        
        print(f"💾 保存翻译结果到: {translated_path}")
        with open(translated_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
            
        print(f"🎉 成功完成翻译: {file_path} → {translated_path}")
        
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {str(e)}", file=sys.stderr)
        raise

def split_front_matter(content):
    """分割Front Matter和内容主体"""
    front_matter_pattern = r'^---\n(.*?\n)---\n'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if match:
        return match.group(0), content[match.end():]
    return "", content

def main():
    if len(sys.argv) < 2:
        print("❌ 错误: 请提供要翻译的文件路径", file=sys.stderr)
        sys.exit(1)
        
    file_path = sys.argv[1]
    process_markdown(file_path)

if __name__ == "__main__":
    main()
