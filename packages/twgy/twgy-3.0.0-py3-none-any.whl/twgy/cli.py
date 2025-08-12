#!/usr/bin/env python3
"""
TWGY Command Line Interface
提供命令行接口供用戶快速使用TWGY功能
"""

import argparse
import sys
import json
import time
from typing import List, Optional
from pathlib import Path

from . import PhoneticReranker, RerankerConfig, get_version, get_system_info


def create_parser() -> argparse.ArgumentParser:
    """創建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog='twgy',
        description='TWGY - Taiwan Mandarin Phonetic Similarity Processor',
        epilog='Examples:\n'
               '  twgy 知道                    # 找出與"知道"相似的詞\n'
               '  twgy 知道 -n 5               # 返回前5個相似詞\n'
               '  twgy --batch words.txt       # 批量處理文件中的詞彙\n'
               '  twgy --info                  # 顯示系統信息\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--version', action='version', version=f'TWGY {get_version()}')
    
    # 主要功能
    parser.add_argument(
        'word', nargs='?', help='要查詢的詞彙'
    )
    
    parser.add_argument(
        '-n', '--num-candidates', 
        type=int, default=10, 
        help='返回的候選詞數量 (預設: 10)'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float, default=0.6,
        help='相似度閾值 (預設: 0.6)'
    )
    
    # 批量處理
    parser.add_argument(
        '--batch', metavar='FILE',
        help='批量處理文件，每行一個詞彙'
    )
    
    # 輸出格式
    parser.add_argument(
        '--json', action='store_true',
        help='以JSON格式輸出結果'
    )
    
    parser.add_argument(
        '--detailed', action='store_true',
        help='顯示詳細信息（處理時間、層級統計等）'
    )
    
    # 系統功能
    parser.add_argument(
        '--info', action='store_true',
        help='顯示系統信息'
    )
    
    parser.add_argument(
        '--test', action='store_true',
        help='運行系統自測'
    )
    
    # 配置選項
    parser.add_argument(
        '--config', metavar='FILE',
        help='指定配置文件路徑'
    )
    
    parser.add_argument(
        '--no-dimsim', action='store_true',
        help='禁用DimSim重排序'
    )
    
    return parser


def load_config(config_path: Optional[str]) -> RerankerConfig:
    """載入配置"""
    config = RerankerConfig()
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # 更新配置
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
        except Exception as e:
            print(f"警告: 無法載入配置文件 {config_path}: {e}", file=sys.stderr)
    
    return config


def format_result(result, detailed: bool = False, json_output: bool = False):
    """格式化輸出結果"""
    if result.error:
        output = {
            "error": result.error,
            "query": result.query
        }
    else:
        output = {
            "query": result.query,
            "candidates": result.candidates,
            "count": len(result.candidates)
        }
        
        if detailed:
            output.update({
                "processing_time_ms": round(result.processing_time_ms, 2),
                "pipeline": {
                    "l1_candidates": result.l1_candidates_count,
                    "l2_candidates": result.l2_candidates_count,
                    "l3_candidates": result.l3_candidates_count,
                    "dimsim_candidates": result.dimsim_candidates_count
                },
                "timing": {
                    "l1_time_ms": round(result.l1_time_ms, 2),
                    "l2_time_ms": round(result.l2_time_ms, 2),
                    "l3_time_ms": round(result.l3_time_ms, 2),
                    "dimsim_time_ms": round(result.dimsim_time_ms, 2)
                },
                "complexity_level": result.complexity_level,
                "confidence_score": round(result.confidence_score, 3)
            })
    
    if json_output:
        return json.dumps(output, ensure_ascii=False, indent=2)
    else:
        return format_text_output(output, detailed)


def format_text_output(output: dict, detailed: bool) -> str:
    """格式化文本輸出"""
    lines = []
    
    if "error" in output:
        lines.append(f"錯誤: {output['error']}")
        return '\n'.join(lines)
    
    lines.append(f"查詢: {output['query']}")
    lines.append(f"找到 {output['count']} 個相似詞:")
    
    for i, candidate in enumerate(output['candidates'], 1):
        lines.append(f"  {i:2d}. {candidate}")
    
    if detailed and 'processing_time_ms' in output:
        lines.append("")
        lines.append("詳細信息:")
        lines.append(f"  處理時間: {output['processing_time_ms']}ms")
        lines.append(f"  複雜度: {output['complexity_level']}")
        lines.append(f"  信心分數: {output['confidence_score']}")
        
        pipeline = output['pipeline']
        lines.append(f"  管道流程: {pipeline['l1_candidates']} → {pipeline['l2_candidates']} → {pipeline['l3_candidates']}")
        
        if pipeline.get('dimsim_candidates', 0) > 0:
            lines.append(f"  DimSim重排: {pipeline['dimsim_candidates']} 候選詞")
    
    return '\n'.join(lines)


def run_batch_processing(file_path: str, reranker: PhoneticReranker, 
                        num_candidates: int, detailed: bool, json_output: bool):
    """運行批量處理"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"錯誤: 找不到文件 {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"錯誤: 無法讀取文件 {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"批量處理 {len(words)} 個詞彙...")
    start_time = time.time()
    
    results = reranker.batch_rerank(words, num_candidates)
    
    total_time = time.time() - start_time
    successful_results = [r for r in results if not r.error]
    
    if json_output:
        # JSON批量輸出
        batch_output = {
            "batch_info": {
                "total_words": len(words),
                "successful": len(successful_results),
                "failed": len(results) - len(successful_results),
                "total_time_ms": round(total_time * 1000, 2),
                "avg_time_ms": round((total_time * 1000) / len(results), 2) if results else 0
            },
            "results": [json.loads(format_result(r, detailed, True)) for r in results]
        }
        print(json.dumps(batch_output, ensure_ascii=False, indent=2))
    else:
        # 文本批量輸出
        print(f"\n批量處理完成:")
        print(f"  總詞彙數: {len(words)}")
        print(f"  成功處理: {len(successful_results)}")
        print(f"  處理失敗: {len(results) - len(successful_results)}")
        print(f"  總時間: {total_time:.2f}s")
        print(f"  平均時間: {(total_time / len(results)):.3f}s" if results else "N/A")
        print("-" * 50)
        
        for result in results:
            print(format_result(result, detailed, False))
            print("-" * 30)


def run_system_test(reranker: PhoneticReranker) -> bool:
    """運行系統自測"""
    print("運行TWGY系統自測...")
    
    test_cases = [
        "知道", "資道", "吃飯", "安全", "來了",
        "電腦", "手機", "這樣", "收集"
    ]
    
    all_passed = True
    
    for i, test_word in enumerate(test_cases, 1):
        print(f"測試 {i}/{len(test_cases)}: {test_word}", end=" ... ")
        
        try:
            result = reranker.rerank(test_word, 5)
            
            if result.error:
                print(f"❌ 失敗: {result.error}")
                all_passed = False
            elif len(result.candidates) == 0:
                print("❌ 失敗: 無候選結果")
                all_passed = False
            elif result.processing_time_ms > 1000:  # 1秒超時
                print(f"⚠️  警告: 處理時間過長 ({result.processing_time_ms:.1f}ms)")
            else:
                print(f"✅ 通過 ({len(result.candidates)} 候選詞, {result.processing_time_ms:.1f}ms)")
                
        except Exception as e:
            print(f"❌ 異常: {e}")
            all_passed = False
    
    print(f"\n系統測試 {'✅ 全部通過' if all_passed else '❌ 存在問題'}")
    return all_passed


def main():
    """主程序入口"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 顯示系統信息
    if args.info:
        info = get_system_info()
        if args.json:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print("TWGY 系統信息:")
            print(f"  版本: {info['twgy_version']}")
            print(f"  Python: {info['python_version'].split()[0]}")
            print(f"  平台: {info['platform']}")
            if 'dictionary_size' in info:
                print(f"  詞典大小: {info['dictionary_size']:,}")
                print(f"  初始化: {'成功' if info['initialized'] else '失敗'}")
            if 'initialization_error' in info:
                print(f"  初始化錯誤: {info['initialization_error']}")
        return
    
    # 載入配置
    config = load_config(args.config)
    
    # 配置選項
    if args.no_dimsim:
        config.enable_dimsim = False
    
    try:
        # 初始化重排器
        reranker = PhoneticReranker(config)
        
        # 運行系統測試
        if args.test:
            success = run_system_test(reranker)
            sys.exit(0 if success else 1)
        
        # 批量處理
        if args.batch:
            run_batch_processing(args.batch, reranker, args.num_candidates, 
                               args.detailed, args.json)
            return
        
        # 單詞查詢
        if args.word:
            result = reranker.rerank(args.word, args.num_candidates)
            print(format_result(result, args.detailed, args.json))
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n用戶中斷", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()