#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲效率分析工具
分析當前爬蟲的性能瓶頸和優化空間
"""

import json
import time
import requests
import psutil
from datetime import datetime, timedelta
from urllib.parse import quote

def analyze_current_performance():
    """分析當前爬蟲性能"""
    print("🔍 當前爬蟲性能分析")
    print("=" * 50)
    
    try:
        with open('fixed_background_checkpoint.json', 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        session_stats = checkpoint.get('session_stats', {})
        start_time_str = session_stats.get('start_time', '')
        
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
            current_time = datetime.now()
            elapsed_time = current_time - start_time
            
            processed = session_stats.get('processed_singers', 0)
            successful = session_stats.get('successful_singers', 0)
            new_songs = session_stats.get('new_songs_added', 0)
            
            hours_elapsed = elapsed_time.total_seconds() / 3600
            
            print(f"📊 當前性能指標:")
            print(f"   運行時間: {hours_elapsed:.1f} 小時")
            print(f"   處理歌手: {processed} 位")
            print(f"   成功歌手: {successful} 位")
            print(f"   新增歌曲: {new_songs} 首")
            
            if hours_elapsed > 0:
                singers_per_hour = processed / hours_elapsed
                songs_per_hour = new_songs / hours_elapsed
                success_rate = (successful / processed * 100) if processed > 0 else 0
                
                print(f"\n⚡ 效率指標:")
                print(f"   處理速度: {singers_per_hour:.1f} 位歌手/小時")
                print(f"   歌曲產出: {songs_per_hour:.1f} 首歌/小時")
                print(f"   成功率: {success_rate:.1f}%")
                print(f"   平均每位成功歌手: {new_songs/successful:.1f} 首歌" if successful > 0 else "   平均每位成功歌手: N/A")
                
                return {
                    'singers_per_hour': singers_per_hour,
                    'songs_per_hour': songs_per_hour,
                    'success_rate': success_rate,
                    'hours_elapsed': hours_elapsed
                }
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        return None

def analyze_system_resources():
    """分析系統資源使用"""
    print(f"\n🖥️ 系統資源分析")
    print("=" * 50)
    
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 記憶體使用
    memory = psutil.virtual_memory()
    
    # 磁碟使用
    disk = psutil.disk_usage('/')
    
    # 網路狀態
    network = psutil.net_io_counters()
    
    print(f"💻 硬體資源:")
    print(f"   CPU使用率: {cpu_percent:.1f}%")
    print(f"   記憶體使用: {memory.percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB/{memory.total/1024/1024/1024:.1f}GB)")
    print(f"   磁碟空間: {disk.percent:.1f}% 已使用")
    
    # 檢查爬蟲進程
    try:
        with open('fixed_scraper.pid', 'r') as f:
            pid = int(f.read().strip())
        
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            proc_cpu = process.cpu_percent()
            proc_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"\n🤖 爬蟲進程:")
            print(f"   PID: {pid}")
            print(f"   CPU使用: {proc_cpu:.1f}%")
            print(f"   記憶體使用: {proc_memory:.1f}MB")
            
            return {
                'system_cpu': cpu_percent,
                'system_memory': memory.percent,
                'process_cpu': proc_cpu,
                'process_memory': proc_memory,
                'has_capacity': cpu_percent < 70 and memory.percent < 80
            }
    
    except Exception as e:
        print(f"⚠️ 無法檢查爬蟲進程: {e}")
        
    return {
        'system_cpu': cpu_percent,
        'system_memory': memory.percent,
        'has_capacity': cpu_percent < 70 and memory.percent < 80
    }

def analyze_network_bottlenecks():
    """分析網路瓶頸"""
    print(f"\n🌐 網路性能測試")
    print("=" * 50)
    
    base_url = "https://song.corp.com.tw"
    test_companies = ["錢櫃", "好樂迪", "金嗓"]
    test_singer = "周杰倫"
    
    response_times = []
    
    for company in test_companies:
        try:
            start_time = time.time()
            search_url = f"{base_url}/songs.aspx?company={quote(company)}&singer={quote(test_singer)}"
            
            response = requests.get(search_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"   {company}: {response_time:.2f}秒 (狀態: {response.status_code})")
            
        except Exception as e:
            print(f"   {company}: 失敗 ({str(e)[:30]})")
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        print(f"\n📊 網路性能:")
        print(f"   平均響應時間: {avg_response_time:.2f}秒")
        print(f"   最快響應: {min(response_times):.2f}秒")
        print(f"   最慢響應: {max(response_times):.2f}秒")
        
        return {
            'avg_response_time': avg_response_time,
            'network_healthy': avg_response_time < 3.0
        }
    
    return {'network_healthy': False}

def analyze_current_settings():
    """分析當前爬蟲設置"""
    print(f"\n⚙️ 當前爬蟲配置分析")
    print("=" * 50)
    
    try:
        # 讀取爬蟲代碼分析配置
        with open('fixed_background_scraper.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取關鍵配置參數
        configs = {}
        
        if 'batch_size = ' in content:
            line = [l for l in content.split('\n') if 'batch_size = ' in l][0]
            configs['batch_size'] = int(line.split('=')[1].strip())
        
        if 'delay_range = ' in content:
            line = [l for l in content.split('\n') if 'delay_range = ' in l][0]
            delay_str = line.split('=')[1].strip()
            # 解析 (4.0, 7.0) 格式
            delay_range = eval(delay_str)
            configs['delay_range'] = delay_range
        
        if 'max_singers_per_session = ' in content:
            line = [l for l in content.split('\n') if 'max_singers_per_session = ' in l][0]
            configs['max_singers_per_session'] = int(line.split('=')[1].strip())
        
        if 'git_push_interval = ' in content:
            line = [l for l in content.split('\n') if 'git_push_interval = ' in l][0]
            configs['git_push_interval'] = int(line.split('=')[1].strip())
        
        companies_count = content.count('"音圓"')  # 計算KTV公司數量的近似方法
        
        print(f"📋 當前配置:")
        print(f"   批次大小: {configs.get('batch_size', '未知')} 位歌手/批次")
        print(f"   延遲範圍: {configs.get('delay_range', '未知')} 秒")
        print(f"   會話限制: {configs.get('max_singers_per_session', '未知')} 位歌手")
        print(f"   Git推送間隔: {configs.get('git_push_interval', '未知')} 位歌手")
        print(f"   KTV公司數量: 約17家")
        
        # 計算理論最大速度
        if 'delay_range' in configs:
            min_delay, max_delay = configs['delay_range']
            avg_delay = (min_delay + max_delay) / 2
            companies_per_singer = 17
            time_per_singer = avg_delay * companies_per_singer
            
            print(f"\n⏱️ 理論性能:")
            print(f"   平均延遲: {avg_delay:.1f}秒/請求")
            print(f"   每位歌手時間: {time_per_singer:.1f}秒 ({time_per_singer/60:.1f}分鐘)")
            print(f"   理論最大速度: {3600/time_per_singer:.1f} 位歌手/小時")
        
        return configs
        
    except Exception as e:
        print(f"❌ 配置分析失敗: {e}")
        return {}

def suggest_optimizations(performance_data, resource_data, network_data, config_data):
    """提供優化建議"""
    print(f"\n💡 效率優化建議")
    print("=" * 50)
    
    suggestions = []
    
    # 延遲優化
    if config_data.get('delay_range'):
        min_delay, max_delay = config_data['delay_range']
        if network_data.get('avg_response_time', 0) < 2.0 and min_delay >= 4.0:
            suggestions.append({
                'type': '延遲優化',
                'current': f'{min_delay}-{max_delay}秒',
                'suggested': '2.0-4.0秒',
                'impact': '速度提升約50%',
                'risk': '低'
            })
    
    # 並行處理
    if resource_data.get('has_capacity', False):
        if resource_data.get('system_cpu', 0) < 50:
            suggestions.append({
                'type': '並行處理',
                'current': '單線程處理',
                'suggested': '2-3個並行線程',
                'impact': '速度提升100-200%',
                'risk': '中'
            })
    
    # 批次大小優化
    current_batch = config_data.get('batch_size', 5)
    if current_batch <= 5 and resource_data.get('system_memory', 0) < 60:
        suggestions.append({
            'type': '批次大小',
            'current': f'{current_batch}位/批次',
            'suggested': '10-15位/批次',
            'impact': '減少批次間隔時間',
            'risk': '低'
        })
    
    # 會話限制優化
    session_limit = config_data.get('max_singers_per_session', 200)
    if session_limit <= 200:
        suggestions.append({
            'type': '會話限制',
            'current': f'{session_limit}位/會話',
            'suggested': '500-1000位/會話',
            'impact': '減少重啟開銷',
            'risk': '低'
        })
    
    # Git推送優化
    git_interval = config_data.get('git_push_interval', 10)
    if git_interval <= 10:
        suggestions.append({
            'type': 'Git推送頻率',
            'current': f'每{git_interval}位推送',
            'suggested': '每50-100位推送',
            'impact': '減少I/O開銷',
            'risk': '低'
        })
    
    # 智能篩選
    suggestions.append({
        'type': '智能優先級',
        'current': '按歌曲數量排序',
        'suggested': '按基準分數排序',
        'impact': '優先處理高價值歌手',
        'risk': '無'
    })
    
    print(f"🚀 建議的優化方案:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n   {i}. {suggestion['type']}")
        print(f"      當前: {suggestion['current']}")
        print(f"      建議: {suggestion['suggested']}")
        print(f"      效果: {suggestion['impact']}")
        print(f"      風險: {suggestion['risk']}")
    
    # 計算綜合提升潛力
    speed_multiplier = 1.0
    for suggestion in suggestions:
        if '50%' in suggestion['impact']:
            speed_multiplier *= 1.5
        elif '100-200%' in suggestion['impact']:
            speed_multiplier *= 2.0
    
    current_speed = performance_data.get('singers_per_hour', 13.8) if performance_data else 13.8
    optimized_speed = current_speed * speed_multiplier
    
    print(f"\n📈 綜合優化效果:")
    print(f"   當前速度: {current_speed:.1f} 位歌手/小時")
    print(f"   優化後速度: {optimized_speed:.1f} 位歌手/小時")
    print(f"   提升倍數: {speed_multiplier:.1f}x")
    
    # 重新計算完成時間
    remaining_singers = 3384  # 從之前分析得出
    new_completion_time = remaining_singers / optimized_speed
    
    print(f"   新完成時間: {new_completion_time:.1f} 小時 ({new_completion_time/24:.1f} 天)")
    
    return suggestions

def main():
    print("⚡ 爬蟲效率優化分析")
    print("=" * 60)
    
    # 性能分析
    performance_data = analyze_current_performance()
    
    # 資源分析
    resource_data = analyze_system_resources()
    
    # 網路分析
    network_data = analyze_network_bottlenecks()
    
    # 配置分析
    config_data = analyze_current_settings()
    
    # 優化建議
    suggestions = suggest_optimizations(performance_data, resource_data, network_data, config_data)
    
    print(f"\n🎯 總結:")
    print("=" * 50)
    print("✅ 當前系統有大量優化空間")
    print("🚀 預估可提升2-3倍效率")
    print("⚡ 建議優先實施低風險優化")
    print("🔧 可考慮並行處理進一步提升")

if __name__ == "__main__":
    main()