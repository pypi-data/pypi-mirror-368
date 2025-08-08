from ats_base.common import func
from ats_base.log.logger import logger

from ats_case.case import command
from ats_case.case.context import Context


def monitoring_control(func):
    """
    逻辑控制语句监测和控制
    :param func:
    :return:
    """

    def wrap(self, index):
        # 执行前
        self._context.runtime.step = self._steps[index]

        is_exec = True
        if _is_control_start_step(self._context):
            if not _condition_is_true(self._context):
                # 条件False -> 跳到控制语句结束步骤
                is_exec = False

        # 执行步骤
        if is_exec:
            func(self, index)

        # 执行后
        not_incr_index = False  # 加1 - 步骤数组的索引
        if _is_control_end_step(self._context):
            not_incr_index = True  # 不加1 - 步骤数组的索引
            if _is_if_end_step(self._context):
                if _is_loop_end_step(self._context):
                    if _loop_is_over(self._context, self._steps):
                        # 循环没有结束, 函数体内会跳步; 结束, 函数体内不跳步, 下面 当前步骤索引加1取下一步骤号, 看是否溢出
                        not_incr_index = _is_not_overflow(self._context, self._steps)  # 没有溢出, 函数体内会跳步
                else:
                    not_incr_index = _is_not_overflow(self._context, self._steps)  # 没有溢出, 函数体内会跳步
            else:
                if _is_loop_end_step(self._context):
                    if _loop_is_over(self._context, self._steps):  # 循环没有结束, 函数体内会跳步
                        not_incr_index = _is_not_overflow(self._context, self._steps)  # 没有溢出, 函数体内会跳步

        if not_incr_index:
            index = self._steps.index(self._context.runtime.step)
        else:
            index = self._steps.index(self._context.runtime.step) + 1

        return index

    return wrap


def _is_control_start_step(context: Context):
    """
    是否是控制语句开始步骤
    :param context:
    :return:
    """
    return context.runtime.step in context.runtime.start_conditions


def _condition_is_true(context: Context):
    """
    条件判断
    :param context:
    :return:
    """
    # if条件
    ifBody = context.runtime.logicBody.get("IF_S_{}".format(context.runtime.step))
    if ifBody is not None and isinstance(ifBody, dict):
        try:
            ci = int(ifBody.get("condition"))
        except:
            ci = int(context.runtime.glo.get(ifBody.get("condition"), 1))

        if ci == 0:  # 条件判断False
            start = ifBody.get("start")
            end = ifBody.get("end")

            context.runtime.step = end
            for i in range(start, end + 1):
                context.runtime.sos.update({i: func.to_dict(result=None)})

            return False

    # loop条件 - 实例化currentLoop
    loopBody = context.runtime.logicBody.get("LOOP_S_{}".format(context.runtime.step))
    if loopBody is not None and isinstance(loopBody, dict):
        start = loopBody.get("start", 0)
        end = loopBody.get("end", 0)
        count = loopBody.get("count", 0)

        if count <= 0:
            context.runtime.step = end
            for i in range(start, end + 1):
                context.runtime.sos.update({i: func.to_dict(result=None)})
            return False

        if context.runtime.currentLoop is None:
            context.runtime.currentLoop = _new_loop(context, start=start, end=end, count=count)
            _log(context)
        else:
            # 新的循环
            if context.runtime.currentLoop.start != start:
                newLoop = _new_loop(context, start=start, end=end, count=count)

                # 判断新的循环是否在当前循环内
                if context.runtime.currentLoop.start < newLoop.start \
                        and newLoop.end <= context.runtime.currentLoop.end:
                    newLoop.parent = context.runtime.currentLoop
                else:  # 判断新循环是否与当前循环在同一个父循环内
                    if context.runtime.currentLoop.parent is not None:
                        if context.runtime.currentLoop.parent.start < newLoop.start \
                                and newLoop.end <= context.runtime.currentLoop.parent.end:
                            newLoop.parent = context.runtime.currentLoop.parent

                context.runtime.currentLoop = newLoop
                _log(context)

    return True


def _is_control_end_step(context: Context):
    """
    是否是控制语句结束步骤
    :param context:
    :return:
    """
    return context.runtime.step in context.runtime.end_conditions


def _is_if_end_step(context: Context):
    """
    是否是if的结束步骤
    :param context:
    :return:
    """
    ifBody = context.runtime.logicBody.get("IF_E_{}".format(context.runtime.step))
    if ifBody is not None and isinstance(ifBody, dict):
        return True

    return False


def _is_loop_end_step(context: Context):
    """
    是否是loop的结束步骤
    :param context:
    :return:
    """
    loopBody = context.runtime.logicBody.get("LOOP_E_{}".format(context.runtime.step))
    if loopBody is not None and isinstance(loopBody, dict):
        return True

    return False


def _loop_is_over(context: Context, steps, is_over=True):
    """
    loop是否结束
    :param context:
    :param steps:
    :param is_over:
    :return:
    """
    if context.runtime.currentLoop is not None:
        context.runtime.currentLoop.index += 1
        context.runtime.loop_index = context.runtime.currentLoop.index  # 兼容2.0.0以前的版本

        if context.runtime.currentLoop.index < context.runtime.currentLoop.count:  # 当前循环未结束, 跳到第一步
            context.runtime.step = context.runtime.currentLoop.start
            is_over = False

            _log(context, level=2)  # 再循环 - 输出日志
        else:
            _log(context, level=1)  # 循环结束 - 输出日志

            if context.runtime.currentLoop.parent is not None:
                context.runtime.currentLoop = context.runtime.currentLoop.parent

                context.runtime.loop_sn = context.runtime.currentLoop.sn
                context.runtime.loop_count = context.runtime.currentLoop.count
                context.runtime.loop_index = context.runtime.currentLoop.index

                if context.runtime.step >= context.runtime.currentLoop.end:
                    is_over = _loop_is_over(context, steps)
                else:
                    context.runtime.step = steps[steps.index(context.runtime.step) + 1]
                    is_over = False

        if is_over:
            context.runtime.currentLoop = None

            context.runtime.loop_sn = 0
            context.runtime.loop_count = 0
            context.runtime.loop_index = 0

    return is_over


def _is_not_overflow(context: Context, steps):
    """
    是否溢出
    :param context:
    :param steps:
    :return:
    """
    try:
        context.runtime.step = steps[steps.index(context.runtime.step) + 1]
    except:  # 溢出测试用例步骤
        return False

    return True


def _new_loop(context: Context, start=0, end=0, count=0):
    context.runtime.incr_loop_sn += 1
    context.runtime.loop_sn = context.runtime.incr_loop_sn
    # 兼容2.0.0以前的版本
    if context.runtime.currentLoop is None and context.runtime.loop_count > 0:
        count = context.runtime.loop_count
    return CurrentLoop(sn=context.runtime.incr_loop_sn, start=start, end=end, count=count)


def _log(context: Context, level=0):
    if level == 0:
        logger.info('~ @TCC-LOOP-> loops[#{}] start. -range {}:{}  -count {}'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count))

        command.client().message('[#{}]循环开始 - 步骤范围[{}-{}], 共{}次'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count)).show(context)

        logger.info('~ @TCC-LOOP-> loops[#{}-{}:{}], -count {}, -index {}'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count,
            context.runtime.currentLoop.index + 1))
        command.client().message('[#{}-{}:{}]循环 - 共{}次, 当前执行第{}次'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count,
            context.runtime.currentLoop.index + 1)).show(context)

    if level == 1:
        command.client().message("[#{}-{}:{}]循环结束...".format(context.runtime.currentLoop.sn,
                                                             context.runtime.currentLoop.start,
                                                             context.runtime.currentLoop.end)).show(context)
        logger.info('~ @TCC-LOOP-> loops[#{}-{}:{}] end.'.format(context.runtime.currentLoop.sn,
                                                                 context.runtime.currentLoop.start,
                                                                 context.runtime.currentLoop.end))

    if level == 2:
        logger.info('~ @TCC-LOOP-> loops[#{}-{}:{}], -count {}, -index {}'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count,
            context.runtime.currentLoop.index + 1))
        command.client().message('[#{}-{}:{}]循环 - 共{}次, 当前执行第{}次'.format(
            context.runtime.currentLoop.sn, context.runtime.currentLoop.start,
            context.runtime.currentLoop.end, context.runtime.currentLoop.count,
            context.runtime.currentLoop.index + 1)).show(context)


class CurrentLoop(object):
    def __init__(self, sn=0, start=0, end=0, count=0):
        self._sn = sn
        self._start = start
        self._end = end
        self._count = count
        self._index = 0
        self._parent = None

    @property
    def sn(self):
        return self._sn

    @sn.setter
    def sn(self, value):
        self._sn = value

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
