#!/usr/bin/env python3
"""
生成完整中文音频的脚本
使用 IndexTTS 分段生成音频，然后用 FFmpeg 合并
"""

import sys
import os
import re
import subprocess
from pathlib import Path
import time

# 设置 HuggingFace 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 添加 indextts 到路径
sys.path.insert(0, '/mnt/c/Users/Administrator/Desktop/all-in/indextts')

from indextts.infer_v2 import IndexTTS2

# 配置参数
CONFIG = {
    'chinese_text_file': '/mnt/c/Users/Administrator/Desktop/all-in/temp_transcript_zh.txt',
    'reference_audio': '/mnt/c/Users/Administrator/Downloads/de353095889897a34f1d1d5d32920a2a.mp3',
    'output_dir': '/mnt/c/Users/Administrator/Desktop/all-in/audio_segments',
    'final_output': '/mnt/c/Users/Administrator/Desktop/all-in/output_chinese_full.wav',
    'batch_size': 100,  # 每批合并的音频数量
    'max_chars_per_segment': 200,  # 每段最多字符数（避免单段太长）
}

def print_progress(current, total, prefix=''):
    """打印进度条"""
    percent = 100 * (current / float(total))
    bar_length = 50
    filled = int(bar_length * current // total)
    bar = '█' * filled + '-' * (bar_length - filled)
    print(f'\r{prefix} |{bar}| {percent:.1f}% ({current}/{total})', end='', flush=True)
    if current == total:
        print()

def split_text_into_segments(text, max_chars=200):
    """
    将文本分割成合适的段落
    优先按照句号、问号、感叹号分割
    """
    # 按照中文句子结束符分割
    sentences = re.split(r'([。！？\n]+)', text)

    segments = []
    current_segment = ""

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ""

        if not sentence.strip():
            continue

        # 如果当前段落加上新句子超过最大长度，保存当前段落
        if len(current_segment) + len(sentence) + len(punctuation) > max_chars and current_segment:
            segments.append(current_segment.strip())
            current_segment = sentence + punctuation
        else:
            current_segment += sentence + punctuation

    # 添加最后一个段落
    if current_segment.strip():
        segments.append(current_segment.strip())

    return segments

def initialize_tts():
    """初始化 IndexTTS 模型"""
    print("\n" + "="*70)
    print("初始化 IndexTTS 模型...")
    print("="*70)

    tts = IndexTTS2(
        cfg_path="/mnt/c/Users/Administrator/Desktop/all-in/indextts/checkpoints/config.yaml",
        model_dir="/mnt/c/Users/Administrator/Desktop/all-in/indextts/checkpoints",
        use_fp16=True,
        use_cuda_kernel=False,
        use_deepspeed=False
    )

    print("✓ 模型初始化完成\n")
    return tts

def generate_audio_segments(tts, segments, reference_audio, output_dir):
    """
    为每个文本段落生成音频
    """
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "="*70)
    print(f"开始生成 {len(segments)} 个音频段落...")
    print("="*70 + "\n")

    audio_files = []
    failed_segments = []

    for i, segment in enumerate(segments):
        output_file = os.path.join(output_dir, f"segment_{i:04d}.wav")

        try:
            print_progress(i, len(segments), prefix='生成进度')

            # 生成音频
            tts.infer(
                spk_audio_prompt=reference_audio,
                text=segment,
                output_path=output_file,
                verbose=False  # 关闭详细输出
            )

            audio_files.append(output_file)

        except Exception as e:
            print(f"\n✗ 段落 {i} 生成失败: {e}")
            failed_segments.append((i, segment, str(e)))
            audio_files.append(None)

    print_progress(len(segments), len(segments), prefix='生成进度')

    if failed_segments:
        print(f"\n⚠ 警告: {len(failed_segments)} 个段落生成失败")
        for idx, seg, err in failed_segments:
            print(f"  - 段落 {idx}: {seg[:50]}... | 错误: {err}")

    print(f"\n✓ 成功生成 {len([f for f in audio_files if f])} / {len(segments)} 个音频段落\n")

    return audio_files

def merge_audio_files_batch(audio_files, output_file, batch_size=100):
    """
    使用 FFmpeg 合并音频文件（分批处理）
    策略来自参考项目: adelay + amix
    """
    # 过滤掉失败的文件
    valid_files = [f for f in audio_files if f and os.path.exists(f)]

    if not valid_files:
        print("✗ 没有有效的音频文件可以合并")
        return False

    print("\n" + "="*70)
    print(f"使用 FFmpeg 合并 {len(valid_files)} 个音频段落...")
    print("="*70 + "\n")

    # 如果文件数量少于批量大小，直接合并
    if len(valid_files) <= batch_size:
        return merge_audio_single_batch(valid_files, output_file)

    # 否则分批合并
    temp_batches = []
    for i in range(0, len(valid_files), batch_size):
        batch_files = valid_files[i:i+batch_size]
        batch_output = f"/tmp/batch_{i//batch_size}.wav"

        print(f"处理批次 {i//batch_size + 1}/{(len(valid_files)-1)//batch_size + 1}...")

        if merge_audio_single_batch(batch_files, batch_output):
            temp_batches.append(batch_output)
        else:
            print(f"✗ 批次 {i//batch_size + 1} 合并失败")
            return False

    # 合并所有批次
    print(f"\n合并 {len(temp_batches)} 个批次文件...")
    result = merge_audio_single_batch(temp_batches, output_file)

    # 清理临时文件
    for temp_file in temp_batches:
        try:
            os.remove(temp_file)
        except:
            pass

    return result

def merge_audio_single_batch(audio_files, output_file):
    """
    合并单批音频文件
    """
    # 创建静音背景轨道
    # 首先计算总时长
    total_duration = 0
    for audio_file in audio_files:
        try:
            # 使用 ffprobe 获取音频时长
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries',
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 audio_file],
                capture_output=True,
                text=True,
                check=True
            )
            duration = float(result.stdout.strip())
            total_duration += duration
        except Exception as e:
            print(f"✗ 无法获取文件时长: {audio_file} | 错误: {e}")
            return False

    # 添加一些缓冲时间
    total_duration += 10

    # 构建 FFmpeg 命令
    # 输入文件列表
    inputs = []
    for f in audio_files:
        inputs.extend(['-i', f])

    # 构建 filter_complex
    # 策略: 为每个音频添加延迟，然后混音
    filter_lines = []
    current_delay = 0

    for i in range(len(audio_files)):
        if i == 0:
            # 第一个不需要延迟
            filter_lines.append(f'[{i}:a]')
        else:
            # 计算延迟（毫秒）
            # 需要累加前面所有音频的时长
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries',
                     'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                     audio_files[i-1]],
                    capture_output=True,
                    text=True,
                    check=True
                )
                duration = float(result.stdout.strip())
                current_delay += int(duration * 1000)  # 转换为毫秒

                filter_lines.append(f'[{i}:a]adelay={current_delay}|{current_delay}[delayed{i}];')
                filter_lines.append(f'[delayed{i}]')
            except:
                filter_lines.append(f'[{i}:a]')

    # 混音
    mix_inputs = ''.join(filter_lines)
    filter_complex = f'{mix_inputs}amix=inputs={len(audio_files)}:duration=longest:normalize=0[out]'

    # 执行 FFmpeg
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-ar', '24000',  # IndexTTS 的采样率
        '-ac', '1',      # 单声道
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ 合并完成: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ FFmpeg 合并失败: {e.stderr.decode()}")
        return False

def main():
    """主函数"""
    print("\n" + "="*70)
    print("完整音频生成流程")
    print("="*70)

    # 1. 读取中文翻译文本
    print("\n[步骤 1/5] 读取中文翻译文本...")
    with open(CONFIG['chinese_text_file'], 'r', encoding='utf-8') as f:
        chinese_text = f.read()
    print(f"✓ 读取完成: {len(chinese_text)} 字符")

    # 2. 分割文本
    print("\n[步骤 2/5] 分割文本为段落...")
    segments = split_text_into_segments(chinese_text, CONFIG['max_chars_per_segment'])
    print(f"✓ 分割完成: {len(segments)} 个段落")
    print(f"  平均每段: {sum(len(s) for s in segments) / len(segments):.1f} 字符")

    # 3. 初始化 TTS
    print("\n[步骤 3/5] 初始化 TTS 模型...")
    tts = initialize_tts()

    # 4. 生成音频段落
    print(f"\n[步骤 4/5] 生成音频段落...")
    print(f"  参考音频: {CONFIG['reference_audio']}")
    print(f"  输出目录: {CONFIG['output_dir']}")

    start_time = time.time()
    audio_files = generate_audio_segments(
        tts,
        segments,
        CONFIG['reference_audio'],
        CONFIG['output_dir']
    )
    generation_time = time.time() - start_time

    print(f"\n⏱ 生成耗时: {generation_time/60:.1f} 分钟")

    # 5. 合并音频
    print(f"\n[步骤 5/5] 合并音频文件...")
    success = merge_audio_files_batch(
        audio_files,
        CONFIG['final_output'],
        CONFIG['batch_size']
    )

    if success:
        print("\n" + "="*70)
        print("✓ 全部完成!")
        print("="*70)
        print(f"\n最终输出文件: {CONFIG['final_output']}")

        # 显示文件信息
        try:
            size_mb = os.path.getsize(CONFIG['final_output']) / (1024 * 1024)
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries',
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 CONFIG['final_output']],
                capture_output=True,
                text=True,
                check=True
            )
            duration = float(result.stdout.strip())
            print(f"文件大小: {size_mb:.1f} MB")
            print(f"音频时长: {duration/60:.1f} 分钟")
        except:
            pass
    else:
        print("\n✗ 音频合并失败")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
