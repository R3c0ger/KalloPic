#!/usr/bin/env python
# -*- coding: utf-8 -*-

def merge_intersecting_sets(unmerged_sets: list[set[str]]) -> list[set[str]]:
    """
    合并列表中有交集的集合。

    :param unmerged_sets: 未合并的集合列表，列表中的元素为集合，这些集合可能有交集
    :return: 合并后的集合列表，列表中的元素为集合
    """
    def condition(x):
        return not unmerge_set.isdisjoint(x)

    merged_sets = []
    for unmerge_set in unmerged_sets:
        if not unmerge_set:
            continue
        # 使用 filter 函数来筛选出与当前集合有交集的已合并集合
        intersect_sets = list(filter(condition, merged_sets))
        # 如果存在有交集的集合则合并，并将原来的集合从已合并集合中删除
        if intersect_sets:
            unmerge_set.update(*intersect_sets)
            merged_sets = [s for s in merged_sets if s not in intersect_sets]
        # 将新合并出的集合添加到已合并集合中
        merged_sets.append(unmerge_set)
    return merged_sets
