"""
命令行工具模块，提供命令行接口
"""

import argparse
import os
import sys
import pandas as pd
import logging

# 导入项目组件
from ..core.modeler import AutoWaterQualityModeler
from ..utils.logger import setup_logging
from ..core.exceptions import (
    AutoWaterQualityError, 
    FileOperationError, 
    DataValidationError
)

def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """
    解析命令行参数
    
    Args:
        args: 命令行参数，如果为None则使用sys.argv
        
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="AutoWaterQualityModeler - 自动水质建模工具")
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 建模命令
    model_parser = subparsers.add_parser('model', help='创建水质模型')
    model_parser.add_argument('--spectrum', '-s', required=True, help='光谱数据CSV文件路径')
    model_parser.add_argument('--metric', '-m', required=True, help='实测值CSV文件路径')
    model_parser.add_argument('--output', '-o', help='输出模型文件路径')
    model_parser.add_argument('--data-type', '-d', default='aerospot', 
                             choices=['warning_device', 'shore_data', 'smart_water', 'aerospot'],
                             help='数据类型')
    model_parser.add_argument('--config', '-c', help='特征配置文件路径')
    model_parser.add_argument('--min-wavelength', type=int, default=400, help='最小波长')
    model_parser.add_argument('--max-wavelength', type=int, default=900, help='最大波长')
    model_parser.add_argument('--smooth-window', type=int, default=11, help='平滑窗口大小')
    model_parser.add_argument('--smooth-order', type=int, default=3, help='平滑多项式阶数')
    
    # 预测命令
    predict_parser = subparsers.add_parser('predict', help='使用水质模型进行预测')
    predict_parser.add_argument('--spectrum', '-s', required=True, help='光谱数据CSV文件路径')
    predict_parser.add_argument('--model', '-m', required=True, help='模型文件路径')
    predict_parser.add_argument('--output', '-o', required=True, help='输出预测结果CSV文件路径')
    predict_parser.add_argument('--min-wavelength', type=int, default=400, help='最小波长')
    predict_parser.add_argument('--max-wavelength', type=int, default=900, help='最大波长')
    predict_parser.add_argument('--smooth-window', type=int, default=11, help='平滑窗口大小')
    predict_parser.add_argument('--smooth-order', type=int, default=3, help='平滑多项式阶数')
    
    # 格式转换
    format_parser = subparsers.add_parser('format', help='格式转换工具')
    format_parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    format_parser.add_argument('--output', '-o', required=True, help='输出文件路径')
    format_parser.add_argument('--format', '-f', required=True, 
                              choices=['json', 'csv', 'excel'],
                              help='输出格式')
    
    # 日志选项
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='日志级别')
    parser.add_argument('--log-file', help='日志文件路径')
    
    # 解析参数
    parsed_args = parser.parse_args(args)
    
    # 检查是否提供了命令
    if not parsed_args.command:
        parser.print_help()
        sys.exit(1)
        
    return parsed_args

def run_model_command(args: argparse.Namespace) -> None:
    """
    执行建模命令
    
    Args:
        args: 命令行参数
    """
    try:
        # 验证输入文件存在性
        if not os.path.exists(args.spectrum):
            raise FileOperationError(
                f"光谱数据文件不存在: {args.spectrum}",
                {"file_path": args.spectrum}
            )
        if not os.path.exists(args.metric):
            raise FileOperationError(
                f"实测数据文件不存在: {args.metric}",
                {"file_path": args.metric}
            )
            
        # 加载数据
        try:
            spectrum_data = pd.read_csv(args.spectrum, index_col=0)
        except Exception as e:
            raise FileOperationError(
                f"读取光谱数据文件失败: {args.spectrum}",
                {"file_path": args.spectrum, "error": str(e)}
            )
            
        try:
            metric_data = pd.read_csv(args.metric, index_col=0)
        except Exception as e:
            raise FileOperationError(
                f"读取实测数据文件失败: {args.metric}",
                {"file_path": args.metric, "error": str(e)}
            )
        
        # 验证数据格式
        if spectrum_data.empty:
            raise DataValidationError("光谱数据为空")
        if metric_data.empty:
            raise DataValidationError("实测数据为空")
            
        # 创建建模器
        modeler = AutoWaterQualityModeler(
            config_path=args.config,
            min_wavelength=args.min_wavelength,
            max_wavelength=args.max_wavelength,
            smooth_window=args.smooth_window,
            smooth_order=args.smooth_order
        )
        
        # 建模
        result = modeler.fit(
            spectrum_data=spectrum_data,
            metric_data=metric_data,
            data_type=args.data_type
        )
        
        # 保存模型
        output_path = args.output or f"model_{args.data_type}.json"
        model_path = modeler.save_model(result.models, output_path)
        
        # 保存预测结果
        if not result.predictions.empty:
            pred_path = os.path.splitext(model_path)[0] + '_predictions.csv'
            result.predictions.to_csv(pred_path)
            logging.info(f"预测结果已保存到: {pred_path}")
            
        if result.has_all_predictions():
            all_pred_path = os.path.splitext(model_path)[0] + '_all_predictions.csv'
            result.all_predictions.to_csv(all_pred_path)
            logging.info(f"所有样本的预测结果已保存到: {all_pred_path}")
            
        logging.info(f"建模完成，模型已保存到: {model_path}")
        
    except AutoWaterQualityError as e:
        # 处理项目特定的异常
        logging.error(f"建模失败: {e.message}")
        if e.details:
            logging.debug(f"错误详情: {e.details}")
        sys.exit(1)
    except Exception as e:
        # 处理未预期的异常
        logging.error(f"建模过程中发生意外错误: {e}", exc_info=True)
        sys.exit(1)

def run_predict_command(args: argparse.Namespace) -> None:
    """
    执行预测命令
    
    Args:
        args: 命令行参数
    """
    try:
        # 加载数据
        spectrum_data = pd.read_csv(args.spectrum, index_col=0)
        
        # 创建建模器
        modeler = AutoWaterQualityModeler(
            min_wavelength=args.min_wavelength,
            max_wavelength=args.max_wavelength,
            smooth_window=args.smooth_window,
            smooth_order=args.smooth_order
        )
        
        # 加载模型
        model_dict = modeler.load_model(args.model)
        
        if not model_dict:
            logging.error(f"加载模型失败: {args.model}")
            sys.exit(1)
            
        # 预测
        predictions = modeler.predict(spectrum_data, model_dict)
        
        # 保存预测结果
        predictions.to_csv(args.output)
        
        logging.info(f"预测完成，结果已保存到: {args.output}")
        
    except Exception as e:
        logging.error(f"预测失败: {e}", exc_info=True)
        sys.exit(1)

def run_format_command(args: argparse.Namespace) -> None:
    """
    执行格式转换命令
    
    Args:
        args: 命令行参数
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(args.input):
            logging.error(f"输入文件不存在: {args.input}")
            sys.exit(1)
            
        # 根据文件扩展名确定输入格式
        input_ext = os.path.splitext(args.input)[1].lower()
        
        # 加载数据
        if input_ext == '.csv':
            data = pd.read_csv(args.input)
        elif input_ext in ['.xls', '.xlsx']:
            data = pd.read_excel(args.input)
        elif input_ext == '.json':
            data = pd.read_json(args.input)
        else:
            logging.error(f"不支持的输入文件格式: {input_ext}")
            sys.exit(1)
            
        # 保存为指定格式
        if args.format == 'csv':
            data.to_csv(args.output, index=False)
        elif args.format == 'excel':
            data.to_excel(args.output, index=False)
        elif args.format == 'json':
            data.to_json(args.output, orient='records')
        
        logging.info(f"格式转换完成，结果已保存到: {args.output}")
        
    except Exception as e:
        logging.error(f"格式转换失败: {e}", exc_info=True)
        sys.exit(1)

def main(args: list[str] | None = None) -> None:
    """
    主入口函数
    
    Args:
        args: 命令行参数，如果为None则使用sys.argv
    """
    # 解析参数
    parsed_args = parse_args(args)
    
    # 设置日志
    log_level = getattr(logging, parsed_args.log_level)
    setup_logging(log_level=log_level, log_name=parsed_args.log_file)
    
    # 执行命令
    if parsed_args.command == 'model':
        run_model_command(parsed_args)
    elif parsed_args.command == 'predict':
        run_predict_command(parsed_args)
    elif parsed_args.command == 'format':
        run_format_command(parsed_args)
    else:
        logging.error(f"未知命令: {parsed_args.command}")
        sys.exit(1)

if __name__ == '__main__':
    main() 