# -*- coding:utf-8 -*-
from .logger import log_debug, log_info, log_warning, log_error, log_critical


class RuleStats:
    """单个校验规则的统计信息"""
    
    def __init__(self, rule_name):
        self.rule_name = rule_name
        self.total_count = 0      # 总校验次数
        self.failed_count = 0     # 失败次数
        self.failed_details = []  # 失败详情
    
    def add_result(self, success, detail=None):
        """添加校验结果"""
        self.total_count += 1
        if not success:
            self.failed_count += 1
            if detail:
                self.failed_details.append(detail)
    
    def get_failure_rate(self):
        """获取失败率"""
        return self.failed_count / self.total_count if self.total_count > 0 else 0.0
    
    def exceeds_threshold(self, threshold):
        """检查是否超过阈值"""
        if threshold is None:
            return self.failed_count > 0  # 严格模式
        elif isinstance(threshold, int):
            return self.failed_count > threshold  # 数量阈值
        elif isinstance(threshold, float):
            return self.get_failure_rate() > threshold  # 比率阈值
        else:
            raise ValueError(f"不支持的阈值类型: {type(threshold)}")


class ValidationContext:
    """校验上下文 - 管理所有规则的统计信息"""
    
    def __init__(self, failure_threshold=None):
        self.failure_threshold = failure_threshold
        self.rule_stats = {}  # {rule_name: RuleStats}
        self.is_strict_mode = (failure_threshold is None)
    
    def get_or_create_rule_stats(self, rule_name):
        """获取或创建规则统计对象"""
        if rule_name not in self.rule_stats:
            self.rule_stats[rule_name] = RuleStats(rule_name)
        return self.rule_stats[rule_name]
    
    def check_all_thresholds(self):
        """检查是否有规则超过阈值"""
        for rule_name, stats in self.rule_stats.items():
            if stats.exceeds_threshold(self.failure_threshold):
                log_warning(f"规则 '{rule_name}' 超过阈值（{self.failure_threshold}）: 失败{stats.failed_count}次，失败率{stats.get_failure_rate():.2%}")
                return False
        return True


"""
通用工具函数
"""
def get_nested_value(obj, path):
    """根据点分隔的路径获取嵌套值"""
    if not path:
        return obj

    parts = path.split('.')
    current = obj

    for part in parts:
        if not isinstance(current, dict):
            raise TypeError(f"路径 '{path}' 中的 '{part}' 需要字典类型，当前类型: {type(current)}")
        if part not in current:
            raise KeyError(f"路径 '{path}' 中的字段 '{part}' 不存在")
        current = current[part]

    return current

def is_empty_value(value):
    """判断值是否为空"""
    if value is None:
        return True, "值为 None"
    if isinstance(value, str):
        if value.strip() == '':
            return True, "值为空字符串"
        if value.strip().lower() == 'null':
            return True, "值为字符串 'null'"
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True, f"值为空{type(value).__name__}"
    return False, None


"""
极简通用数据校验 - 默认非空校验，调用简洁
"""

def check(data, *validations, failure_threshold=None):
    """
    极简数据校验函数 - 默认非空校验
    
    :param data: 要校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认，保持完全兼容性）
        - int: 每个规则最多允许N个失败 (如 failure_threshold=3)
        - float: 每个规则最多允许N%失败率 (如 failure_threshold=0.1 表示10%)
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例用法：
    # 默认非空校验 - 最简形式
    check(response, "data.product.id", "data.product.name")
    
    # 带校验器的形式
    check(response, "data.product.id > 0", "data.product.price >= 10.5")
    
    # 混合校验
    check(response, 
          "data.product.id",           # 默认非空
          "data.product.price > 0",    # 大于0
          "status_code == 200")        # 等于200
    
    # 列表批量校验 - 通配符
    check(response, "data.productList.*.id", "data.productList.*.name")
    
    # 嵌套列表校验
    check(response, "data.productList.*.purchasePlan.*.id > 0")
    """
    
    # 打印任务信息和数据概览
    log_info(f"开始执行数据校验 - 共{len(validations)}个校验规则")
    log_debug(f"待校验数据类型: {type(data).__name__}")
    log_debug(f"校验规则列表: {list(validations)}")
    
    # 严格模式：保持原有逻辑完全不变
    if failure_threshold is None:
        passed_count = 0
        failed_count = 0
        
        for i, validation in enumerate(validations):
            try:
                log_debug(f"[{i+1}/{len(validations)}] 开始校验: {validation}")
                
                result = _parse_and_validate(data, validation)
                if result:
                    passed_count += 1
                    log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
                else:
                    failed_count += 1
                    log_warning(f"[{i+1}/{len(validations)}] 校验失败: {validation} ✗")
                    
            except (KeyError, IndexError, TypeError, ValueError) as e:
                # 数据结构异常，抛出异常
                error_msg = f"数据结构异常: {validation} - {str(e)}"
                log_error(f"[{i+1}/{len(validations)}] ❌ {error_msg}")
                raise Exception(error_msg)
            except Exception as e:
                # 校验逻辑失败，记录为失败
                failed_count += 1
                log_warning(f"[{i+1}/{len(validations)}] 校验异常: {validation} - {str(e)} ✗")
        
        # 打印最终结果
        success_rate = f"{passed_count}/{len(validations)}"
        log_info(f"数据校验完成: {success_rate} 通过 (成功率: {passed_count/len(validations)*100:.1f}%)")
        
        if failed_count > 0:
            log_debug(f"失败统计: 共{failed_count}个校验失败")
        
        # 返回校验结果
        return failed_count == 0
    
    # 阈值模式：使用统计引擎
    else:
        return _execute_with_threshold(data, validations, failure_threshold)


def _execute_with_threshold(data, validations, failure_threshold):
    """统一的阈值模式执行引擎"""
    context = ValidationContext(failure_threshold)
    
    for i, validation in enumerate(validations):
        rule_name = f"rule_{i+1}: {validation}"
        stats = context.get_or_create_rule_stats(rule_name)
        
        try:
            _parse_and_validate_with_stats(data, validation, stats)
        except (KeyError, IndexError, TypeError, AttributeError, ValueError) as e:
            # 数据结构异常，抛出异常
            error_msg = f"数据结构异常: {validation} - {str(e)}"
            log_error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            # 其他校验异常，记录为失败
            stats.add_result(False, f"校验异常: {str(e)}")
    
    # 检查所有规则阈值
    final_result = context.check_all_thresholds()
    _log_validation_summary(context, final_result)
    return final_result


def _parse_and_validate_with_stats(data, rule, rule_stats):
    """带统计功能的校验解析"""
    if isinstance(rule, str):
        return _parse_string_rule_with_stats(data, rule, rule_stats)
    elif isinstance(rule, dict):
        return _parse_dict_rule_with_stats(data, rule, rule_stats)
    else:
        raise ValueError(f"不支持的校验规则格式: {type(rule)}")


def _parse_string_rule_with_stats(data, rule, rule_stats):
    """解析字符串格式的校验规则 - 统计版本"""
    # 支持的操作符映射 (注意：按长度排序，避免匹配冲突)
    operators = [
        ("#<=", "length_le"), ("#>=", "length_ge"), ("#!=", "length_ne"), ("#=", "length_eq"), ("#<", "length_lt"), ("#>", "length_gt"), ("!=", "ne"),
        ("==", "eq"), ("<=", "le"), (">=", "ge"), ("<", "lt"), (">", "gt"),
        ("~=", "regex"), ("^=", "startswith"), ("$=", "endswith"), ("*=", "contains"), ("=*", "contained_by"),
        ("@=", "type_match")
    ]
    
    # 尝试匹配操作符
    for op, validator in operators:
        if op in rule:
            parts = rule.split(op, 1)
            if len(parts) == 2:
                field_path = parts[0].strip()
                expect_value = parts[1].strip()
                
                # 解析期望值
                expect_value = _parse_expect_value(expect_value)
                
                # 执行校验
                return _validate_field_path_with_stats(data, field_path, validator, expect_value, rule_stats)
    
    # 没有操作符，默认为非空校验
    field_path = rule.strip()
    return _validate_field_path_with_stats(data, field_path, "not_empty", True, rule_stats)


def _parse_dict_rule_with_stats(data, rule, rule_stats):
    """解析字典格式的校验规则 - 统计版本"""
    field_path = rule.get('field')
    validator = rule.get('validator', 'not_empty')
    expect_value = rule.get('expect')
    
    if not field_path:
        raise ValueError("字典格式校验规则必须包含'field'键")
    
    return _validate_field_path_with_stats(data, field_path, validator, expect_value, rule_stats)


def _validate_field_path_with_stats(data, field_path, validator, expect_value, rule_stats):
    """支持统计的字段路径校验"""
    values = _get_values_by_path(data, field_path)
    log_debug(f"字段路径 '{field_path}' 匹配到 {len(values)} 个值")
    
    # 特殊处理：条件校验
    if validator == "conditional_check":
        return _execute_conditional_with_stats(data, expect_value['condition'], expect_value['then'], rule_stats)
    
    for value, path in values:
        result = _execute_validator(validator, value, expect_value, path)
        detail = f"校验字段 '{path}': {type(value).__name__} = {repr(value)} | 校验器: {validator} | 期望值: {repr(expect_value)}"
        rule_stats.add_result(result, detail)
        
        if result:
            log_debug(f"{detail} | 检验结果: ✓")
        else:
            log_warning(f"{detail} | 检验结果: ✗")
    
    return True  # 统计模式总是返回True


def _execute_conditional_with_stats(data, condition_rule, then_rules, rule_stats):
    """带统计的条件校验处理（条件校验存在两种语义，当前使用的是第一种语义）
    1. 如果整体条件检查失败，就跳过所有then检查
        - 对每个数据项进行条件校验
        - 如果所有数据项都满足条件，就检查then规则
        - 如果任一数据项不满足条件，就跳过then规则
    2. 对于满足条件的项目，就检查then规则是否满足
        - 对每个数据项分别检查条件
        - 如果条件满足，就检查then规则
        - 如果条件不满足，就跳过该项
        - 任何满足条件但then规则失败的项都应该导致整体失败
    """
    # 执行条件检查 (条件检查不计入统计)
    condition_result = _parse_and_validate(data, condition_rule)
    
    if condition_result:
        log_debug(f"条件成立，执行then校验: {then_rules}")
        if isinstance(then_rules, list):
            for then_rule in then_rules:
                _parse_and_validate_with_stats(data, then_rule, rule_stats)
        else:
            _parse_and_validate_with_stats(data, then_rules, rule_stats)
    else:
        log_warning(f"条件不成立，跳过then校验: {condition_rule}")
        # 条件不成立，不计入失败统计
    
    return True


def _log_validation_summary(context, final_result=None):
    """输出校验结果摘要"""
    total_rules = len(context.rule_stats)
    exceeded_rules = [stats for stats in context.rule_stats.values() 
                     if stats.exceeds_threshold(context.failure_threshold)]
    
    if isinstance(context.failure_threshold, int):
        threshold_desc = f"数量阈值{context.failure_threshold}"
    elif isinstance(context.failure_threshold, float):
        threshold_desc = f"比率阈值{context.failure_threshold:.1%}"
    else:
        threshold_desc = "严格模式"
    
    log_info(f"数据校验完成: 总规则{total_rules}个，超过阈值{len(exceeded_rules)}个 | 阈值设置: {threshold_desc}")
    
    if exceeded_rules:
        for stats in exceeded_rules:
            log_warning(f"规则超阈值详情: {stats.rule_name} - 失败{stats.failed_count}/{stats.total_count} (失败率{stats.get_failure_rate():.1%})")


def _parse_and_validate(data, rule):
    """解析校验规则并执行校验"""
    if isinstance(rule, str):
        return _parse_string_rule(data, rule)
    elif isinstance(rule, dict):
        return _parse_dict_rule(data, rule)
    else:
        raise ValueError(f"不支持的校验规则格式: {type(rule)}")


def _parse_string_rule(data, rule):
    """解析字符串格式的校验规则"""
    # 支持的操作符映射 (注意：按长度排序，避免匹配冲突)
    operators = [
        ("#<=", "length_le"), ("#>=", "length_ge"), ("#!=", "length_ne"), ("#=", "length_eq"), ("#<", "length_lt"), ("#>", "length_gt"), ("!=", "ne"),
        ("==", "eq"), ("<=", "le"), (">=", "ge"), ("<", "lt"), (">", "gt"),
        ("~=", "regex"), ("^=", "startswith"), ("$=", "endswith"), ("*=", "contains"), ("=*", "contained_by"),
        ("@=", "type_match")
    ]
    
    # 尝试匹配操作符
    for op, validator in operators:
        if op in rule:
            parts = rule.split(op, 1)
            if len(parts) == 2:
                field_path = parts[0].strip()
                expect_value = parts[1].strip()
                
                # 解析期望值
                expect_value = _parse_expect_value(expect_value)
                
                # 执行校验
                return _validate_field_path(data, field_path, validator, expect_value)
    
    # 没有操作符，默认为非空校验
    field_path = rule.strip()
    return _validate_field_path(data, field_path, "not_empty", True)


def _parse_dict_rule(data, rule):
    """解析字典格式的校验规则"""
    field_path = rule.get('field')
    validator = rule.get('validator', 'not_empty')
    expect_value = rule.get('expect')
    
    if not field_path:
        raise ValueError("字典格式校验规则必须包含'field'键")
    
    return _validate_field_path(data, field_path, validator, expect_value)


def _parse_expect_value(value_str):
    """解析期望值字符串为合适的类型"""
    value_str = value_str.strip()
    
    # 去掉引号
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # 数字
    if value_str.isdigit():
        return int(value_str)
    
    # 浮点数
    try:
        if '.' in value_str:
            return float(value_str)
    except ValueError:
        pass
    
    # 布尔值
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'
    
    # null
    if value_str.lower() in ['null', 'none']:
        return None
    
    # 默认返回字符串
    return value_str


def _validate_field_path(data, field_path, validator, expect_value):
    """校验字段路径
    
    :return: True表示所有字段都校验通过，False表示存在校验失败
    """
    # 特殊处理：条件校验
    if validator == "conditional_check":
        return _execute_conditional(data, expect_value['condition'], expect_value['then'])

    values = _get_values_by_path(data, field_path)
    log_debug(f"字段路径 '{field_path}' 匹配到 {len(values)} 个值")
    
    for value, path in values:
        result = _execute_validator(validator, value, expect_value, path)
        if not result:
            log_warning(f"校验字段 '{path}': {type(value).__name__} = {repr(value)} | 校验器: {validator} | 期望值: {repr(expect_value)} | 检验结果: ✗")
            return False # 发现校验失败，直接中断后续校验规则返回False
        else:
            log_debug(f"校验字段 '{path}': {type(value).__name__} = {repr(value)} | 校验器: {validator} | 期望值: {repr(expect_value)} | 检验结果: ✓")
    return True


def _execute_conditional(data, condition_rule, then_rules):
    """条件校验处理逻辑（条件校验存在两种语义，当前使用的是第一种语义）
    1. 如果整体条件检查失败，就跳过所有then检查
        - 对每个数据项进行条件校验
        - 如果所有数据项都满足条件，就检查then规则
        - 如果任一数据项不满足条件，就跳过then规则
    2. 对于满足条件的项目，就检查then规则是否满足
        - 对每个数据项分别检查条件
        - 如果条件满足，就检查then规则
        - 如果条件不满足，就跳过该项
        - 任何满足条件但then规则失败的项都应该导致整体失败
    """
    condition_result = _parse_and_validate(data, condition_rule)
    if condition_result:
        log_debug(f"条件成立, 继续执行then校验: when({condition_rule}) then({then_rules})")
        # then_rules支持包含多个字符串校验规则的列表，或者单个字典格式的校验规则
        if isinstance(then_rules, list):
            for then_rule in then_rules:
                if not _parse_and_validate(data, then_rule):
                    return False # 发现校验失败，直接中断后续校验规则返回False
            return True
        else:
            return _parse_and_validate(data, then_rules)
    else:
        log_warning(f"条件不成立, 跳过then校验, 直接返回通过: when({condition_rule}) then({then_rules})")

    return True

def _get_values_by_path(obj, path):
    """根据路径获取值，支持通配符*"""
    if not path:
        return [(obj, "")]
    
    parts = path.split('.')
    current_objects = [(obj, "")]
    
    for part in parts:
        next_objects = []
        for current_obj, current_path in current_objects:
            new_path = f"{current_path}.{part}" if current_path else part
            
            if part == '*':
                if isinstance(current_obj, list):
                    for i, item in enumerate(current_obj):
                        next_objects.append((item, f"{current_path}[{i}]" if current_path else f"[{i}]"))
                elif isinstance(current_obj, dict):
                    for key, value in current_obj.items():
                        next_objects.append((value, f"{current_path}.{key}" if current_path else key))
                else:
                    raise TypeError(f"通配符'*'只能用于列表或字典，路径: {current_path}, 类型: {type(current_obj)}")
            else:
                if isinstance(current_obj, dict):
                    if part not in current_obj:
                        raise KeyError(f"字段不存在: {new_path}")
                    next_objects.append((current_obj[part], new_path))
                elif isinstance(current_obj, list):
                    if not part.isdigit():
                        raise ValueError(f"列表索引必须是数字: {part}")
                    index = int(part)
                    if index < 0 or index >= len(current_obj):
                        raise IndexError(f"索引超出范围: {new_path}")
                    next_objects.append((current_obj[index], f"{current_path}[{index}]" if current_path else f"[{index}]"))
                else:
                    raise TypeError(f"无法在{type(current_obj)}上访问字段: {part}")
        current_objects = next_objects
    
    return current_objects


def _check_type_match(check_value, expect_value):
    """检查值的类型是否匹配期望类型
    
    :param check_value: 要检查的值
    :param expect_value: 期望的类型，可以是类型对象或类型名称字符串
    :return: True表示类型匹配，False表示类型不匹配
    """
    def get_type(name):
        """根据名称获取类型对象"""
        if isinstance(name, type):
            return name
        elif isinstance(name, str):
            # 支持常见的类型名称
            type_mapping = {
                'int': int,
                'float': float,
                'str': str,
                'string': str,
                'bool': bool,
                'boolean': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'nonetype': type(None),
                'none': type(None),
                'null': type(None)
            }
            
            # 先检查自定义映射
            if name.lower() in type_mapping:
                return type_mapping[name.lower()]
            
            # 尝试从内置类型获取
            try:
                return eval(name)
            except:
                raise ValueError(f"不支持的类型名称: {name}")
        else:
            raise ValueError(f"期望值必须是类型对象或类型名称字符串，当前类型: {type(expect_value)}")
    
    try:
        expected_type = get_type(expect_value)
        return isinstance(check_value, expected_type)
    except Exception as e:
        raise TypeError(f"类型匹配检查失败: {str(e)}")


def _safe_numeric_compare(check_value, expect_value):
    """安全的数值比较，支持字符串数字自动转换
    
    :param check_value: 要检查的值
    :param expect_value: 期望值
    :return: (转换后的check_value, 转换后的expect_value)
    :raises: ValueError: 当值无法转换为数字时
    """
    def to_number(value):
        """将值转换为数字"""
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # 去除首尾空格
            value = value.strip()
            # 尝试转换为整数
            try:
                return int(value)
            except ValueError:
                pass
            # 尝试转换为浮点数
            try:
                return float(value)
            except ValueError:
                pass
        # 无法转换，返回原值
        return value
    
    # 转换两个值
    converted_check = to_number(check_value)
    converted_expect = to_number(expect_value)
    
    # 如果任一值无法转换为数字，回退到原始比较
    if (not isinstance(converted_check, (int, float)) or not isinstance(converted_expect, (int, float))):
        return check_value, expect_value
    
    return converted_check, converted_expect


def _execute_validator(validator, check_value, expect_value, field_path):
    """执行具体的校验
    
    :return: True表示校验通过，False表示校验失败
    :raises: ValueError: 当校验器不支持时
    :raises: TypeError: 当数据类型不匹配时
    """
    try:
        if validator == "not_empty":
            is_empty, _ = is_empty_value(check_value)
            return not is_empty
        
        elif validator == "eq":
            return check_value == expect_value
        
        elif validator == "ne":
            return check_value != expect_value
        
        elif validator == "gt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val > expect_val
        
        elif validator == "ge":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val >= expect_val
        
        elif validator == "lt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val < expect_val
        
        elif validator == "le":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val <= expect_val
        
        elif validator == "contains":
            return expect_value in check_value
        
        elif validator == "contained_by":
            return check_value in expect_value
        
        elif validator == "startswith":
            return str(check_value).startswith(str(expect_value))
        
        elif validator == "endswith":
            return str(check_value).endswith(str(expect_value))
        
        elif validator == "regex":
            import re
            try:
                return bool(re.match(str(expect_value), str(check_value)))
            except re.error:
                return False
        
        elif validator == "type_match":
            return _check_type_match(check_value, expect_value)
        
        elif validator == "custom_number_check":
            return isinstance(check_value, (int, float))
        
        elif validator == "in_values":
            return check_value in expect_value
        
        elif validator == "not_in_values":
            return check_value not in expect_value
        
        elif validator == "length_eq":
            return len(check_value) == expect_value
        
        elif validator == "length_ne":
            return len(check_value) != expect_value
        
        elif validator == "length_gt":
            return len(check_value) > expect_value
        
        elif validator == "length_ge":
            return len(check_value) >= expect_value

        elif validator == "length_lt":
            return len(check_value) < expect_value
        
        elif validator == "length_le":
            return len(check_value) <= expect_value

        elif validator == "length_between":
            min_len, max_len = expect_value
            return min_len <= len(check_value) <= max_len
        
        else:
            raise ValueError(f"不支持的校验器: {validator}")
    
    except Exception as e:
        log_error(f"执行校验时出现异常：校验字段 '{field_path}': {type(check_value).__name__} = {repr(check_value)} | 校验器: {validator} | 期望值: {repr(expect_value)} | 异常信息: {str(e)}")
        raise


def check_not_empty(data, *field_paths, failure_threshold=None):
    """专门的非空校验 - 最常用场景"""
    return check(data, *field_paths, failure_threshold=failure_threshold)


def check_when(data, condition, *then, failure_threshold=None):
    """
    条件校验 - 当条件满足时执行then校验（支持批量校验）
    
    :param data: 要校验的数据
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示校验通过，False表示校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 单个then校验 - 当status为active时，price必须大于0
    check_when(data, "status == 'active'", "price > 0")
    
    # 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
    check_when(data, "type == 'premium'", "features", "price > 100")
    
    # 批量校验 - 当status为active时，多个字段都必须校验通过
    check_when(data, "status == 'active'", 
               "price > 0", 
               "name", 
               "description",
               "category != 'test'")
    
    # 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
    check_when(data, "products.*.status == 'active'", 
               "products.*.price > 0", 
               "products.*.name")
    
    # 混合条件校验 - 当用户为VIP时，多个权限字段都必须校验
    check_when(data, "user.level == 'vip'", 
               "user.permissions.download == true",
               "user.permissions.upload == true", 
               "user.quota > 1000")
    
    注意：
    1. 当条件满足时，所有then校验都必须通过才算成功
    2. 当条件不满足时，跳过所有then校验（返回True）
    """
    
    # 参数验证
    if not then:
        raise ValueError("至少需要提供一个then校验规则")
    
    # 构建条件校验规则
    conditional_rule = {
        'field': 'conditional',
        'validator': 'conditional_check',
        'expect': {
            'condition': condition,
            'then': list(then)
        }
    }
    return check(data, conditional_rule, failure_threshold=failure_threshold)


def check_list(data_list, *field_names, failure_threshold=None, **validators):
    """
    列表数据批量校验 - 简化版
    
    :param data_list: 数据列表
    :param field_names: 字段名（默认非空校验，同时支持符号表达式校验和字典格式参数校验）
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :param validators: 带校验器的字段 field_name="validator expression"}
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 默认非空校验
    check_list(productList, "id", "name", "price")
    
    # 带校验器
    check_list(productList, "name", id="> 0", price=">= 0")
    或
    check_list(productList, "name", "id > 0", "price >= 0")
    
    # 混合使用
    check_list(productList, "name", "description", id="> 0", status="== 'active'")
    或
    check_list(productList, "name", "description", "id > 0", "status == 'active'")
    """
    
    total_fields = len(field_names) + len(validators)
    log_info(f"列表数据批量校验 - 列表长度: {len(data_list) if isinstance(data_list, list) else '未知'}, 字段数: {total_fields}")
    log_debug(f"非空校验字段: {list(field_names)}")
    log_debug(f"带校验器字段: {dict(validators)}")
    
    if not isinstance(data_list, list):
        raise TypeError(f"data_list必须是列表，当前类型: {type(data_list)}")
    
    # 构建校验规则
    rules = []
    
    # 默认非空校验的字段
    for field in field_names:
        rules.append(f"*.{field}")
    
    # 带校验器的字段
    for field, validator_expr in validators.items():
        rules.append(f"*.{field} {validator_expr}")
    
    # 执行校验
    return check(data_list, *rules, failure_threshold=failure_threshold)


def check_nested(data, list_path, nested_field, *field_validations, failure_threshold=None):
    """
    嵌套列表数据批量校验 - 简化版
    
    :param data: 要校验的数据
    :param list_path: 主列表路径
    :param nested_field: 嵌套字段名
    :param field_validations: 字段校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 默认非空校验
    check_nested(response, "data.productList", "purchasePlan", "id", "name")
    
    # 带校验器
    check_nested(response, "data.productList", "purchasePlan", "id > 0", "amount >= 100")
    """
    
    log_info(f"嵌套列表数据批量校验 - 路径: {list_path}.*.{nested_field}, 字段数: {len(field_validations)}")
    log_debug(f"主列表路径: {list_path}")
    log_debug(f"嵌套字段名: {nested_field}")
    log_debug(f"字段校验规则: {list(field_validations)}")
    
    main_list_value = get_nested_value(data, list_path)
    if isinstance(main_list_value, list) and len(main_list_value) > 0:
        nested_field_value = main_list_value[0][nested_field]
    else:
        raise ValueError(f"主列表路径 {list_path} 的值不是列表或为空列表")

    # 构建校验规则
    rules = []
    for validation in field_validations:
        if isinstance(nested_field_value, list):
            # 嵌套字段值为列表
            rules.append(f"{list_path}.*.{nested_field}.*.{validation}")
        elif isinstance(nested_field_value, dict):
            # 嵌套字段值为字典
            rules.append(f"{list_path}.*.{nested_field}.{validation}")
        else:
            raise ValueError(f"嵌套字段 {nested_field} 的值不是列表或字典")

    return check(data, *rules, failure_threshold=failure_threshold)


class DataChecker:
    """链式调用的数据校验器"""
    
    def __init__(self, data):
        self.data = data
        self.rules = []
    
    def field(self, path, validator=None, expect=None):
        """添加字段校验"""
        if validator is None:
            # 默认非空
            self.rules.append(path)
        elif expect is None:
            # 字符串表达式
            self.rules.append(f"{path} {validator}")
        else:
            # 分离的校验器和期望值
            self.rules.append(f"{path} {validator} {expect}")
        return self
    
    def not_empty(self, *paths):
        """批量非空校验"""
        self.rules.extend(paths)
        return self
    
    # 等值比较校验
    def equals(self, path, value):
        """等于校验"""
        self.rules.append(f"{path} == {repr(value)}")
        return self
    
    def not_equals(self, path, value):
        """不等于校验"""
        self.rules.append(f"{path} != {repr(value)}")
        return self
    
    # 数值比较校验
    def greater_than(self, path, value):
        """大于校验"""
        self.rules.append(f"{path} > {value}")
        return self
    
    def greater_equal(self, path, value):
        """大于等于校验"""
        self.rules.append(f"{path} >= {value}")
        return self
    
    def less_than(self, path, value):
        """小于校验"""
        self.rules.append(f"{path} < {value}")
        return self
    
    def less_equal(self, path, value):
        """小于等于校验"""
        self.rules.append(f"{path} <= {value}")
        return self
    
    # 数值范围校验
    def between(self, path, min_value, max_value, inclusive=True):
        """数值区间校验"""
        if inclusive:
            self.rules.append(f"{path} >= {min_value}")
            self.rules.append(f"{path} <= {max_value}")
        else:
            self.rules.append(f"{path} > {min_value}")
            self.rules.append(f"{path} < {max_value}")
        return self
    
    # 字符串校验
    def starts_with(self, path, prefix):
        """以指定字符串开头"""
        self.rules.append(f"{path} ^= {repr(prefix)}")
        return self
    
    def ends_with(self, path, suffix):
        """以指定字符串结尾"""
        self.rules.append(f"{path} $= {repr(suffix)}")
        return self
    
    def contains(self, path, substring):
        """包含指定字符串"""
        self.rules.append(f"{path} *= {repr(substring)}")
        return self
    
    def contained_by(self, path, container):
        """被指定字符串包含"""
        self.rules.append(f"{path} =* {repr(container)}")
        return self
    
    def matches_regex(self, path, pattern):
        """正则表达式匹配"""
        self.rules.append(f"{path} ~= {repr(pattern)}")
        return self
    
    # 类型校验
    def is_type(self, path, expected_type):
        """类型校验"""
        if isinstance(expected_type, type):
            type_name = expected_type.__name__
        else:
            type_name = str(expected_type)
        self.rules.append(f"{path} @= {repr(type_name)}")
        return self
    
    def is_string(self, path):
        """字符串类型校验"""
        return self.is_type(path, 'str')
    
    def is_number(self, path):
        """数字类型校验（int或float）"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'custom_number_check',
            'expect': None
        })
        return self
    
    def is_integer(self, path):
        """整数类型校验"""
        return self.is_type(path, 'int')
    
    def is_float(self, path):
        """浮点数类型校验"""
        return self.is_type(path, 'float')
    
    def is_boolean(self, path):
        """布尔类型校验"""
        return self.is_type(path, 'bool')
    
    def is_list(self, path):
        """列表类型校验"""
        return self.is_type(path, 'list')
    
    def is_dict(self, path):
        """字典类型校验"""
        return self.is_type(path, 'dict')
    
    def is_none(self, path):
        """None类型校验"""
        return self.is_type(path, 'none')
    
    # 集合校验
    def in_values(self, path, values):
        """值在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'in_values',
            'expect': values
        })
        return self
    
    def not_in_values(self, path, values):
        """值不在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'not_in_values',
            'expect': values
        })
        return self
    
    # 长度校验
    def length_equals(self, path, length):
        """长度等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_eq',
            'expect': length
        })
        return self
    
    def length_not_equals(self, path, length):
        """长度不等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ne',
            'expect': length
        })
        return self
    
    def length_greater_than(self, path, length):
        """长度大于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_gt',
            'expect': length
        })
        return self
    
    def length_less_than(self, path, length):
        """长度小于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_lt',
            'expect': length
        })
        return self

    def length_greater_equal(self, path, length):
        """长度大于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ge',
            'expect': length
        })
        return self
    
    def length_less_equal(self, path, length):
        """长度小于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_le',
            'expect': length
        })
        return self

    def length_between(self, path, min_length, max_length, inclusive=True):
        """长度在指定范围内"""
        if inclusive:
            self.rules.append({
                'field': path,
                'validator': 'length_ge',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_le',
                'expect': max_length
            })
        else:
            self.rules.append({
                'field': path,
                'validator': 'length_gt',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_lt',
                'expect': max_length
            })
        return self
    
    # 特殊校验
    def is_email(self, path):
        """邮箱格式校验"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': email_pattern
        })
        return self
    
    def is_phone(self, path):
        """手机号格式校验（中国大陆）"""
        phone_pattern = r'^1[3-9]\d{9}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': phone_pattern
        })
        return self
    
    def is_url(self, path):
        """URL格式校验"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': url_pattern
        })
        return self
    
    def is_positive(self, path):
        """正数校验"""
        return self.greater_than(path, 0)
    
    def is_negative(self, path):
        """负数校验"""
        return self.less_than(path, 0)
    
    def is_non_negative(self, path):
        """非负数校验"""
        return self.greater_equal(path, 0)
    
    # 批量操作
    def all_fields_not_empty(self, *paths):
        """批量非空校验（别名）"""
        return self.not_empty(*paths)
    
    def all_fields_positive(self, *paths):
        """批量正数校验"""
        for path in paths:
            self.is_positive(path)
        return self
    
    def all_fields_type(self, field_type, *paths):
        """批量类型校验"""
        for path in paths:
            self.is_type(path, field_type)
        return self
    
    # 条件校验
    def when(self, condition, *then):
        """
        条件校验：当条件满足时，执行then校验（支持批量校验）
        
        :param condition: 条件表达式，支持所有校验器语法
        :param then: then表达式，支持所有校验器语法，可传入多个校验规则
        :return: self（支持链式调用）
        
        示例：
        # 单个then校验 - 当status为active时，price必须大于0
        .when("status == 'active'", "price > 0")
        
        # 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
        .when("type == 'premium'", "features", "price > 100")
        
        # 批量校验 - 当status为active时，多个字段都必须校验通过
        .when("status == 'active'", 
              "price > 0", 
              "name", 
              "description",
              "category != 'test'")
        
        # 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
        .when("products.*.status == 'active'", 
              "products.*.price > 0", 
              "products.*.name")
        
        # 链式调用示例
        checker(data).when("user.level == 'vip'", 
                          "user.permissions.download == true",
                          "user.permissions.upload == true", 
                          "user.quota > 1000") \
                     .when("user.status == 'active'", 
                          "user.last_login", 
                          "user.email") \
                     .validate()
        
        注意：
        1. 当条件满足时，所有then校验都必须通过才算成功
        2. 当条件不满足时，跳过所有then校验（返回True）
        3. 支持链式调用，可以添加多个条件校验
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建条件校验规则
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self
    
    def validate(self, failure_threshold=None):
        """执行校验
        
        :param failure_threshold: 失败阈值
            - None: 严格模式，一个失败全部失败（默认）
            - int: 每个规则最多允许N个失败
            - float: 每个规则最多允许N%失败率
        :return: True表示所有校验通过，False表示存在校验失败
        :raises: Exception: 当参数错误或数据结构异常时抛出异常
        """
        return check(self.data, *self.rules, failure_threshold=failure_threshold)


def checker(data):
    """创建数据校验器"""
    return DataChecker(data)