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
                "content": "你是一位专业的翻译专家，擅长将中文技术博客翻译为自然流畅的英文。请保持Markdown格式不变，只翻译文本内容。"
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
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 跳过已翻译的文件
    if file_path.endswith('_en.md'):
        print(f"Skipping already translated file: {file_path}")
        return
    
    # 生成翻译后的文件名
    base, ext = os.path.splitext(file_path)
    translated_path = f"{base}_en{ext}"
    
    # 如果翻译文件已存在且比源文件新，则跳过
    if os.path.exists(translated_path) and os.path.getmtime(translated_path) >= os.path.getmtime(file_path):
        print(f"Translation up-to-date for: {file_path}")
        return
    
    print(f"Translating: {file_path}")
    
    try:
        translated_content = translate_text(content)
        
        # 写入翻译后的文件
        with open(translated_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        
        print(f"Successfully translated to: {translated_path}")
    except Exception as e:
        print(f"Error translating {file_path}: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("No files to process")
        return
    
    # 获取所有变更的文件
    changed_files = sys.argv[1].split()
    
    for file_path in changed_files:
        if file_path.endswith('.md') and not file_path.endswith('_en.md'):
            process_markdown(file_path)

if __name__ == "__main__":
    main()
