# -*- coding: utf-8 -*-
"""
后处理模块 - 处理模型输出并生成最终的检测结果

该模块包含YOLOv8模型输出的后处理功能，包括：
1. 分布式焦点损失(DFL)解码
2. 边界框坐标处理
3. 非极大值抑制(NMS)
4. 并行处理优化

这些功能被优化以提高处理速度和内存效率。
"""

import numpy as np
import logging
import traceback
import concurrent.futures
from .config import get_config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def dfl(position):
    """
    分布式焦点损失 (Distribution Focal Loss) 后处理
    
    优化版本：提高计算效率，减少内存分配，使用缓存加速重复计算
    
    将离散的分布转换为连续值，用于边界框回归
    
    Args:
        position: 模型输出的位置编码
        
    Returns:
        numpy数组: 解码后的位置值
    """
    # 提前检查输入数据有效性
    if position is None or position.size == 0:
        return np.array([])
    
    n, c, h, w = position.shape
    p_num = 4  # 位置参数数量
    mc = c // p_num  # 每个位置参数的分布数量
    
    # 重塑数组
    y = position.reshape(n, p_num, mc, h, w)
    
    # 使用NumPy实现softmax
    # 在dim=2上应用softmax
    y_exp = np.exp(y - np.max(y, axis=2, keepdims=True))
    y = y_exp / np.sum(y_exp, axis=2, keepdims=True)
    
    # 创建加权矩阵
    acc_matrix = np.arange(mc).reshape(1, 1, mc, 1, 1).astype(np.float32)
    
    # 计算加权和
    result = np.sum(y * acc_matrix, axis=2)
    
    return result


def box_process(position):
    """
    处理模型输出的位置编码，转换为边界框坐标
    
    优化版本：提高计算效率，减少内存分配，使用缓存加速重复计算
    
    Args:
        position: 模型输出的位置编码
        
    Returns:
        numpy数组: 格式为[x1, y1, x2, y2]的边界框坐标
    """
    # 提前检查输入数据有效性
    if position is None or position.size == 0:
        return np.array([])
    
    # 获取特征图尺寸
    grid_h, grid_w = position.shape[2:4]
    
    # 使用缓存避免重复计算网格
    # 使用静态变量缓存不同尺寸的网格
    if not hasattr(box_process, "grid_cache"):
        box_process.grid_cache = {}
    
    grid_key = (grid_h, grid_w)
    if grid_key not in box_process.grid_cache:
        # 创建网格 - 只在第一次调用或尺寸变化时计算
        col, row = np.meshgrid(np.arange(0, grid_w), np.arange(0, grid_h))
        col = col.reshape(1, 1, grid_h, grid_w)
        row = row.reshape(1, 1, grid_h, grid_w)
        grid = np.concatenate((col, row), axis=1)
        
        # 计算步长
        img_height, img_width = get_config('img_size')[1], get_config('img_size')[0]
        stride = np.array([img_height//grid_h, img_width//grid_w]).reshape(1, 2, 1, 1)
        
        # 缓存网格和步长
        box_process.grid_cache[grid_key] = (grid, stride)
    else:
        # 从缓存获取网格和步长
        grid, stride = box_process.grid_cache[grid_key]
    
    # 应用DFL解码 - 直接使用结果避免中间变量
    position_decoded = dfl(position)
    
    # 计算边界框坐标 - 使用广播避免循环
    box_xy  = grid + 0.5 - position_decoded[:, 0:2, :, :]
    box_xy2 = grid + 0.5 + position_decoded[:, 2:4, :, :]
    
    # 合并坐标并应用步长 - 直接返回结果
    return np.concatenate((box_xy*stride, box_xy2*stride), axis=1)


def filter_boxes(boxes, box_confidences, box_class_probs):
    """
    根据置信度阈值过滤检测框
    
    优化版本：使用NumPy的向量化操作提高性能，减少内存使用
    
    Args:
        boxes: 边界框坐标
        box_confidences: 边界框置信度
        box_class_probs: 类别概率
        
    Returns:
        boxes: 过滤后的边界框
        classes: 过滤后的类别
        scores: 过滤后的得分
    """
    # 提前检查输入数据有效性
    if boxes.size == 0 or box_confidences.size == 0 or box_class_probs.size == 0:
        return np.array([]), np.array([]), np.array([])
    
    # 重塑置信度数组 - 使用视图而不是复制
    box_confidences = box_confidences.reshape(-1)
    
    # 使用NumPy的向量化操作获取每个框的最高类别得分和对应的类别
    class_max_score = np.max(box_class_probs, axis=-1)
    classes = np.argmax(box_class_probs, axis=-1)
    
    # 计算最终得分并根据阈值过滤 - 使用布尔索引一次性完成
    final_scores = class_max_score * box_confidences
    mask = final_scores >= get_config('obj_thresh')
    
    # 如果没有框通过过滤，返回空数组
    if not np.any(mask):
        return np.array([]), np.array([]), np.array([])
    
    # 应用过滤 - 直接返回过滤后的结果
    return boxes[mask], classes[mask], final_scores[mask]


def fast_nms(boxes, scores, iou_threshold=None):
    """
    快速非极大值抑制算法
    
    使用矩阵运算一次性计算所有IoU，大幅提高NMS速度
    
    Args:
        boxes: 边界框坐标，格式为 [x1, y1, x2, y2]
        scores: 对应的置信度得分
        iou_threshold: IoU阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        keep: 保留的边界框索引数组
    """
    if iou_threshold is None:
        iou_threshold = get_config('nms_thresh')
        
    # 提前检查输入数据有效性
    if len(boxes) == 0 or len(scores) == 0:
        return np.array([], dtype=np.int32)
    
    # 如果只有一个框，直接返回其索引
    if len(boxes) == 1:
        return np.array([0], dtype=np.int32)
    
    # 确保boxes是float类型
    if boxes.dtype != np.float32 and boxes.dtype != np.float64:
        boxes = boxes.astype(np.float32)
    
    # 按得分降序排序
    order = scores.argsort()[::-1]
    boxes = boxes[order]
    
    # 计算所有框的面积
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    
    # 预分配keep数组
    keep = []
    
    # 计算所有框之间的IoU矩阵
    # 使用广播计算所有框之间的交集坐标
    xx1 = np.maximum(x1[:, None], x1)  # [N,N]
    yy1 = np.maximum(y1[:, None], y1)  # [N,N]
    xx2 = np.minimum(x2[:, None], x2)  # [N,N]
    yy2 = np.minimum(y2[:, None], y2)  # [N,N]
    
    # 计算交集面积
    w = np.maximum(0.0, xx2 - xx1)  # [N,N]
    h = np.maximum(0.0, yy2 - yy1)  # [N,N]
    inter = w * h  # [N,N]
    
    # 计算IoU
    iou = inter / (areas[:, None] + areas - inter + 1e-10)  # [N,N]
    
    # 创建上三角掩码(不包括对角线)
    triu_mask = np.triu(np.ones_like(iou, dtype=bool), k=1)
    
    # 初始化保留掩码
    keep_mask = np.ones(len(boxes), dtype=bool)
    
    # 遍历每个框
    for i in range(len(boxes)):
        # 如果当前框已被抑制，跳过
        if not keep_mask[i]:
            continue
            
        # 找出与当前框IoU大于阈值的所有框
        overlap_mask = (iou[i] > iou_threshold) & triu_mask[i]
        
        # 抑制这些框
        keep_mask[overlap_mask] = False
    
    # 获取保留的框的原始索引
    keep = order[keep_mask]
    
    return keep


def nms_boxes(boxes, scores):
    """
    非极大值抑制 (NMS) 算法实现
    
    优化版本：提高计算效率，减少内存使用，处理边界情况
    根据配置选择标准NMS或快速NMS
    
    Args:
        boxes: 边界框坐标，格式为 [x1, y1, x2, y2]
        scores: 对应的置信度得分
        
    Returns:
        keep: 保留的边界框索引数组
    """
    # 使用快速NMS
    if get_config('use_fast_nms'):
        return fast_nms(boxes, scores)
    
    # 提前检查输入数据有效性
    if len(boxes) == 0 or len(scores) == 0:
        return np.array([], dtype=np.int32)
    
    # 如果只有一个框，直接返回其索引
    if len(boxes) == 1:
        return np.array([0], dtype=np.int32)
    
    # 确保boxes是float类型，避免整数溢出
    if boxes.dtype != np.float32 and boxes.dtype != np.float64:
        boxes = boxes.astype(np.float32)
    
    # 按得分降序排序
    order = scores.argsort()[::-1]
    boxes = boxes[order]
    
    # 计算所有框的面积
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    
    # 预分配keep数组
    keep = []
    
    # 标准NMS实现
    while order.size > 0:
        i = order[0]
        keep.append(i)
        
        # 计算当前框与剩余框的IoU
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-10)
        
        # 获取IoU小于阈值的框的索引
        inds = np.where(ovr <= get_config('nms_thresh'))[0]
        
        # 更新order
        order = order[inds + 1]
    
    return np.array(keep)


def post_process_parallel(input_data, conf_thresh=None, nms_thresh=None):
    """
    并行处理模型输出，生成最终的检测结果
    
    使用线程池并行处理不同分支的输出，提高处理速度
    
    Args:
        input_data: 模型的原始输出
        conf_thresh: 置信度阈值，如果为None则使用CONFIG['obj_thresh']
        nms_thresh: NMS阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        boxes: 边界框坐标 [x1, y1, x2, y2]
        classes: 类别索引
        scores: 置信度得分
    """
    # 提前检查输入数据有效性
    if not input_data or len(input_data) == 0:
        return None, None, None
    
    # 如果提供了自定义阈值，临时更新CONFIG
    from .config import update_config, get_config
    original_config = get_config()
    if conf_thresh is not None or nms_thresh is not None:
        new_config = {}
        if conf_thresh is not None:
            new_config['obj_thresh'] = conf_thresh
        if nms_thresh is not None:
            new_config['nms_thresh'] = nms_thresh
        update_config(new_config)
    
    try:
        # YOLOv8输出处理参数
        default_branch = 3
        pair_per_branch = len(input_data) // default_branch
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务处理每个分支
            futures = []
            for i in range(default_branch):
                box_data = input_data[pair_per_branch * i]
                cls_data = input_data[pair_per_branch * i + 1]
                futures.append(executor.submit(process_branch, box_data, cls_data))
            
            # 收集结果
            boxes_list = []
            classes_conf_list = []
            scores_list = []
            
            for future in concurrent.futures.as_completed(futures):
                box_flat, cls_flat, score_flat = future.result()
                boxes_list.append(box_flat)
                classes_conf_list.append(cls_flat)
                scores_list.append(score_flat)
        
        # 合并所有分支的结果
        boxes = np.concatenate(boxes_list)
        classes_conf = np.concatenate(classes_conf_list)
        scores = np.concatenate(scores_list)
        
        # 清理不再需要的变量以释放内存
        del boxes_list, classes_conf_list, scores_list
        
        # 根据阈值过滤检测框
        boxes, classes, scores = filter_boxes(boxes, scores, classes_conf)
        del classes_conf  # 立即释放不再需要的大数组
        
        # 如果没有检测到物体，直接返回
        if len(classes) == 0 or len(boxes) == 0:
            # 恢复原始配置
            if conf_thresh is not None or nms_thresh is not None:
                update_config(original_config)
            return None, None, None
        
        # 使用NumPy的unique获取唯一类别，比set()更高效
        unique_classes = np.unique(classes)
        
        # 预分配结果数组的估计大小
        est_size = min(len(boxes), len(unique_classes) * 10)  # 假设每个类别平均保留10个框
        result_boxes = np.zeros((est_size, 4), dtype=boxes.dtype)
        result_classes = np.zeros(est_size, dtype=classes.dtype)
        result_scores = np.zeros(est_size, dtype=scores.dtype)
        
        # 对每个类别应用NMS
        idx = 0
        for c in unique_classes:
            # 使用布尔索引获取当前类别的所有检测框
            mask = (classes == c)
            if not np.any(mask):
                continue
                
            b = boxes[mask]
            s = scores[mask]
            
            # 应用NMS
            keep = nms_boxes(b, s)
            keep_count = len(keep)
            
            if keep_count > 0:
                # 直接写入预分配的结果数组
                if idx + keep_count > est_size:
                    # 如果预分配空间不足，扩展数组
                    new_size = idx + keep_count
                    result_boxes.resize((new_size, 4), refcheck=False)
                    result_classes.resize(new_size, refcheck=False)
                    result_scores.resize(new_size, refcheck=False)
                
                result_boxes[idx:idx+keep_count] = b[keep]
                result_classes[idx:idx+keep_count] = c
                result_scores[idx:idx+keep_count] = s[keep]
                idx += keep_count
        
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        # 如果没有检测结果
        if idx == 0:
            return None, None, None
        
        # 裁剪结果数组到实际大小
        return result_boxes[:idx], result_classes[:idx], result_scores[:idx]
        
    except Exception as e:
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        logging.error(f"并行后处理错误: {e}")
        traceback.print_exc()
        return None, None, None


def process_branch(box_data, cls_data):
    """
    处理单个分支的输出
    
    用于并行处理的辅助函数
    
    Args:
        box_data: 边界框数据
        cls_data: 类别数据
        
    Returns:
        box_flat: 展平的边界框坐标
        cls_flat: 展平的类别概率
        score_flat: 展平的置信度得分
    """
    # 处理边界框坐标
    box_processed = box_process(box_data)
    
    # 转换和展平数据
    ch_box = box_processed.shape[1]
    box_flat = box_processed.transpose(0, 2, 3, 1).reshape(-1, ch_box)
    
    ch_cls = cls_data.shape[1]
    cls_flat = cls_data.transpose(0, 2, 3, 1).reshape(-1, ch_cls)
    
    # 创建置信度得分并展平
    score_flat = np.ones((cls_flat.shape[0], 1), dtype=np.float32)
    
    return box_flat, cls_flat, score_flat


def post_process(input_data, conf_thresh=None, nms_thresh=None):
    """
    处理模型输出，生成最终的检测结果
    
    高度优化版本：专注于只返回boxes、classes和scores三个值，
    减少内存分配和复制，提高处理速度
    根据配置选择并行或串行处理
    
    Args:
        input_data: 模型的原始输出
        conf_thresh: 置信度阈值，如果为None则使用CONFIG['obj_thresh']
        nms_thresh: NMS阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        boxes: 边界框坐标 [x1, y1, x2, y2]
        classes: 类别索引
        scores: 置信度得分
    """
    # 如果提供了自定义阈值，临时更新CONFIG
    from .config import update_config, get_config
    original_config = get_config()
    
    # 使用并行处理
    if get_config('use_parallel'):
        return post_process_parallel(input_data, conf_thresh, nms_thresh)
    
    # 提前检查输入数据有效性
    if not input_data or len(input_data) == 0:
        return None, None, None
    if conf_thresh is not None or nms_thresh is not None:
        new_config = {}
        if conf_thresh is not None:
            new_config['obj_thresh'] = conf_thresh
        if nms_thresh is not None:
            new_config['nms_thresh'] = nms_thresh
        update_config(new_config)
        
    # YOLOv8输出处理参数
    default_branch = 3
    pair_per_branch = len(input_data) // default_branch
    
    # 使用NumPy的向量化操作处理数据
    try:
        # 预分配内存并直接处理每个分支的输出
        boxes_list = []
        classes_conf_list = []
        scores_list = []
        
        for i in range(default_branch):
            # 处理边界框坐标
            box_data = input_data[pair_per_branch * i]
            box_processed = box_process(box_data)
            
            # 处理类别概率和置信度
            cls_data = input_data[pair_per_branch * i + 1]
            
            # 转换和展平数据 - 内联以减少函数调用
            ch_box = box_processed.shape[1]
            box_flat = box_processed.transpose(0, 2, 3, 1).reshape(-1, ch_box)
            boxes_list.append(box_flat)
            
            ch_cls = cls_data.shape[1]
            cls_flat = cls_data.transpose(0, 2, 3, 1).reshape(-1, ch_cls)
            classes_conf_list.append(cls_flat)
            
            # 创建置信度得分并展平 (使用ones_like的切片视图避免额外内存分配)
            score_flat = np.ones((cls_flat.shape[0], 1), dtype=np.float32)
            scores_list.append(score_flat)
        
        # 合并所有分支的结果
        boxes = np.concatenate(boxes_list)
        classes_conf = np.concatenate(classes_conf_list)
        scores = np.concatenate(scores_list)
        
        # 清理不再需要的变量以释放内存
        del boxes_list, classes_conf_list, scores_list, box_processed, cls_data
        
        # 根据阈值过滤检测框
        boxes, classes, scores = filter_boxes(boxes, scores, classes_conf)
        del classes_conf  # 立即释放不再需要的大数组
        
        # 如果没有检测到物体，直接返回
        if len(classes) == 0 or len(boxes) == 0:
            # 恢复原始配置
            if conf_thresh is not None or nms_thresh is not None:
                update_config(original_config)
            return None, None, None
        
        # 使用NumPy的unique获取唯一类别，比set()更高效
        unique_classes = np.unique(classes)
        
        # 预分配结果数组的估计大小
        est_size = min(len(boxes), len(unique_classes) * 10)  # 假设每个类别平均保留10个框
        result_boxes = np.zeros((est_size, 4), dtype=boxes.dtype)
        result_classes = np.zeros(est_size, dtype=classes.dtype)
        result_scores = np.zeros(est_size, dtype=scores.dtype)
        
        # 对每个类别应用NMS
        idx = 0
        for c in unique_classes:
            # 使用布尔索引获取当前类别的所有检测框
            mask = (classes == c)
            if not np.any(mask):
                continue
                
            b = boxes[mask]
            s = scores[mask]
            
            # 应用NMS
            keep = nms_boxes(b, s)
            keep_count = len(keep)
            
            if keep_count > 0:
                # 直接写入预分配的结果数组
                if idx + keep_count > est_size:
                    # 如果预分配空间不足，扩展数组
                    new_size = idx + keep_count
                    result_boxes.resize((new_size, 4), refcheck=False)
                    result_classes.resize(new_size, refcheck=False)
                    result_scores.resize(new_size, refcheck=False)
                
                result_boxes[idx:idx+keep_count] = b[keep]
                result_classes[idx:idx+keep_count] = c
                result_scores[idx:idx+keep_count] = s[keep]
                idx += keep_count
        
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        # 如果没有检测结果
        if idx == 0:
            return None, None, None
        
        # 裁剪结果数组到实际大小
        return result_boxes[:idx], result_classes[:idx], result_scores[:idx]
        
    except Exception as e:
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        logging.error(f"后处理错误: {e}")
        traceback.print_exc()
        return None, None, None