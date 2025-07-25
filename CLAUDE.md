# FOMO Industry Matching - Claude 记忆文档

## 项目概述
- **项目名称**: 行业智能识别系统
- **核心功能**: 基于多层次语义分析的全自动新闻行业识别
- **性能**: F1分数 96.4%，支持4个行业（半导体、游戏、AI、金融科技）

## 已知问题与解决方案

### 1. 中文编码显示问题
**问题**: 在 Claude Code 的 Bash 工具中，中文字符显示为乱码符号（♦♣♥）

**解决方案**: 
```python
def safe_print(text):
    """安全打印函数，处理编码问题"""
    try:
        if isinstance(text, str):
            # 尝试以GBK编码输出（Windows默认）
            try:
                print(text.encode('gbk', errors='replace').decode('gbk'))
            except:
                # 如果GBK失败，回退到安全显示
                print(text.encode('ascii', errors='replace').decode('ascii'))
        else:
            print(text)
    except Exception:
        print(repr(text))

# 在脚本开头添加
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
```

**注意**: 这个问题只出现在 Claude Code 的 Bash 工具中，用户本地终端显示正常。

### 2. YAML 配置文件格式问题
**问题**: 数字型关键词被解析为整数导致 `.lower()` 方法调用失败

**解决方案**: 在 YAML 文件中给所有数字型关键词加引号
```yaml
# 错误写法
- 3nm
- GPT-4

# 正确写法  
- "3nm"
- "GPT-4"
```

## 系统架构要点

### 核心算法
```python
# 改进的评分算法
match_quality = min(len(matched_keywords) / 10.0, 1.0)  # 10个关键词即满分
frequency_score = min(total_frequency / 15.0, 1.0)     # 总频次15即满分
high_value_boost = min(high_value_matches * 0.3, 0.6)  # 每个高价值词+0.3
base_score = (match_quality * 0.4 + frequency_score * 0.6) + high_value_boost
```

### 配置结构
- **主配置**: `industry_configs/main_config.yaml` - 权重和阈值
- **行业配置**: 4层结构 (L1核心词40% + L2技术术语30% + L3应用场景20% + L4相关实体10%)
- **置信度阈值**: high_confidence: 0.3, low_confidence: 0.15

## 测试验证
- **综合测试**: `comprehensive_test.py` - 14个测试用例
- **基础测试**: `simple_test.py` - 基本功能验证
- **配置测试**: `database/config_loader.py` - 配置加载验证

## 部署准备
- **下一步**: GitHub Actions 工作流部署
- **环境变量**: SUPABASE_URL, SUPABASE_KEY
- **依赖**: requirements.txt (包含 PyYAML)