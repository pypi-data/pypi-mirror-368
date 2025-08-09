import ast
from pydantic import BaseModel
from enum import Enum
from pathlib import Path
from typing import Any
from .format import format_code
from .expression import Expr


class ActiveBaseModel(BaseModel):
    def copy_with(self, func):
        model_copy = self.model_copy()
        func(model_copy)
        return model_copy


class OrderEnum(Enum):
    "排序方式类"

    asc = True
    "从小到大排序"

    desc = False
    "从大到小排序"


class Factor(ActiveBaseModel):
    """
    [因子配置模型](https://bbs.quantclass.cn/thread/51962)
    """

    name: str
    "因子名称, 必须与因子库目录中的因子文件名一致, 例如 'Ret' 或 '市值'"

    order: OrderEnum = OrderEnum.asc
    "设置为`OrderEnum.asc`(True)从小到大排序, 设置为`OrderEnum.desc`(False)从大到小排序"

    params: Any | None = None
    "因子参数, 对应的是因子中的param参数"

    weight: float | int | str | Any
    """
    多任务参数位, 默认为因子权重, 多个选股因子组成复合因子时, 用于计算每个因子参与计算排名的权重。

    选股因子排名计算: `因子1排名 * 因子权重 + 因子2排名 * 因子权重`

    有一些策略奇葩，还用str，比如高材生，避免还有这种奇葩，也兼容 Any 吧
    """

    def build(self) -> ast.Tuple:
        return ast.Tuple(
            elts=[
                ast.Constant(value=self.name),
                ast.Constant(value=self.order.value),
                ast.Constant(value=self.params),
                ast.Constant(value=self.weight),
            ],
            ctx=ast.Load(),
        )


class TimingFactor(Factor):
    """
    [定风波因子](https://bbs.quantclass.cn/thread/51962)
    """

    time: str
    "择时计算时间, 计算是否开仓信号的开始时间, 如0945就是在上午09:45计算早盘强度动态阈值, 测算是否开仓的择时信号"

    def build(self) -> ast.Tuple:
        return ast.Tuple(
            elts=[
                ast.Constant(value=self.name),
                ast.Constant(value=self.order.value),
                ast.Constant(value=self.params),
                ast.Constant(value=self.weight),
                ast.Constant(value=self.time),
            ],
            ctx=ast.Load(),
        )


class Filter(ActiveBaseModel):
    """
    [过滤规则](https://bbs.quantclass.cn/thread/51962)
    """

    name: str
    "过滤指标的名称, 例如 '成交额Mean'"

    params: Any
    "因子参数, 对应的是因子中的params参数"

    expression: Expr
    """
    过滤排序规则, 有三种规则, 以市值因子举例:

    - `pct`: 按照百分比排序, `pct:<0.2` 就是保留排序前20%, 剔除后80%的股票; 就是保留市值最小20%的股票, 剔除市值大的80%的股票;
    - `rank`: 按照排名排序, `rank:>1` 保留排名大于1的股票; 按照True从小到大排序, 就是剔除掉市值最小的股票;
    - `val`: 按照因子值排序, `val:<1_0000_0000` 就是保留市值小于1亿的股票, 剔除市值大于等于1亿的股票。
    """

    order: OrderEnum = OrderEnum.asc
    "设置为`OrderEnum.asc`(True)从小到大排序, 设置为`OrderEnum.desc`(False)从大到小排序"

    def build(self) -> ast.Tuple:
        return ast.Tuple(
            elts=[
                ast.Constant(value=self.name),
                ast.Constant(value=self.params),
                ast.Constant(value=self.expression.build()),
                ast.Constant(value=self.order.value),
            ],
            ctx=ast.Load(),
        )


class Timing(ActiveBaseModel):
    """
    [换仓时机](https://bbs.quantclass.cn/thread/51962)
    """

    name: str
    "与信号库的定风波择时文件名一一对应，相当于调用择时信号因子；"

    limit: int | float
    """
    择时的选股范围, 有三种形式: 0, 小数和整数。

    - 0, 代表全市场（选股策略过滤过的全市场）。定风波会测算全市场的下跌比列, 决定是否开仓
    - 小数, 如0.2代表全市场的20%。如果全市场是5000只股票, 0.2就是测算1000只股票的下跌比例
    - 整数, 如200代表200只股票, 就是测算选股策略前200只股票的下跌比例
    - 一般建议设置为整数, 如200或者500, 计算择时会比较快。但是不建议设置的太小, 如小于100会导致择时信号失真。
    """

    factor_list: list[TimingFactor]
    "因子列表"

    params: tuple[float | int, float | int] | int | float
    """
    择时规则参数, 目前12个定风波因子有三种规则参数类型:

    - 固定阈值: 如早盘强度, 固定阈值就是0, 意思指全市场平均涨幅超过0
    - 时间周期: 如早盘强度动态阈值这里的60是计算过去60天的早盘强度
    - 技术指标参数: 案例参考macd动态阈值
    - 注: 择时信号设置的策略原理, 参数解释请参考视频: [定风波1的适度理解(2)](https://www.quantclass.cn/online-player/67e6379154df1343dea8f1b5), [各类定风波策略客户端实盘介绍](https://www.quantclass.cn/online-player/67f37e0828d19b07ebdc7c3e)
    """

    def build(self) -> ast.Dict:
        return ast.Dict(
            keys=[
                ast.Constant(value="name"),
                ast.Constant(value="limit"),
                ast.Constant(value="factor_list"),
                ast.Constant(value="params"),
            ],
            values=[
                ast.Constant(value=self.name),
                ast.Constant(value=self.limit),
                ast.List(
                    elts=[factor.build() for factor in self.factor_list], ctx=ast.Load()
                ),
                ast.Constant(value=self.params),
            ],
        )


class StrategyConfig(ActiveBaseModel):
    "[策略配置模型](https://bbs.quantclass.cn/thread/51962)"

    name: str
    "策略名称"

    hold_period: str
    """
    持仓周期, 例如 'D' (日), 'W' (周), 'M' (月)

    - 日级别: 2D, 3D, 4D, 5D, 10D;
    - 周级别: W, 2W, 3W, 4W, 5W, 6W, W53;
    - 月级别: M;

    注意: `W53_0`, 也就是周五买入, 周三卖出, 周四空仓休息
    """

    offset_list: list[int]
    """
    offset列表, 书写方式参照股票周期预运算表的数据文件。

    - [夏普的计算工具](https://bbs.quantclass.cn/thread/29895)

    ps. 论坛里有人说: `不过夏普船长教导我说, 回测好的offset数可能是偶然数, 不建议只写回测好的offset数值。`
    """

    select_num: int | float
    "选股数量, 可以是整数, 如10就是选股10只。也可以是小数, 如0.1就是选全市场10%的股票, 约500+只。"

    cap_weight: float | int
    """
    资金占比, 多策略组合时使用。
    
    如有两个策略, 每个策略的cap_weight都设置为1, 那么每个子策略的资金占比为 1/(1+1) = 0.5, 也就是每个子策略资金占比50%。
    
    当然也可以是1:2, 或者2:1, 那么资金占比就是33%比66%或者66%比33%。
    """

    rebalance_time: str
    """
    换仓时机, 根据持仓周期和offset交易时, 在股票开始时间具体什么时刻卖出和买入。
    这里可以设置的参数有三类, 一共六种。

    1. 隔日换仓
        - `close-open`: 选股日收盘前卖出, 交易日开盘后买入（隔日换仓）
    2. 日内换仓
        - `open`: 交易日开盘后先卖出, 交易日开盘后再买入（日内早盘）
        - `close`: 选股日收盘前卖出, 选股日收盘前再买入（日内尾盘）
    3. 定风波定时换仓
        - `0935-0935`: 开盘后09:35换仓, 先卖出再买入
        - `0945-0945`: 开盘后09:45换仓, 先卖出再买入
        - `0955-0955`: 开盘后09:55换仓, 先卖出再买入

    注: 
    - 支持全天任意5分钟换仓, 但必须比定风波择时时间晚10分钟。
    - 这是个重要的参数必须设置, 没有默认参数, 不设置报错。
    """

    factor_list: list[Factor]
    "用于选股的因子列表"

    filter_list: list[Filter]
    "用于过滤股票池的条件列表"

    timing: Timing | None = None
    "可选, 定风波择时区域以'timing':{}的形式设置, 只要在子策略里包含timing范式就会被当作定风波择时策略。"

    def build(self) -> ast.Dict:
        """生成更美观的Python格式配置文件"""

        keys = [
            ast.Constant(value="name"),
            ast.Constant(value="hold_period"),
            ast.Constant(value="offset_list"),
            ast.Constant(value="select_num"),
            ast.Constant(value="cap_weight"),
            ast.Constant(value="rebalance_time"),
            ast.Constant(value="factor_list"),
            ast.Constant(value="filter_list"),
        ]

        if self.timing:
            keys.append(ast.Constant(value="timing"))

        values = [
            ast.Constant(value=self.name),
            ast.Constant(value=self.hold_period),
            ast.List(
                elts=[ast.Constant(value=offset) for offset in self.offset_list],
                ctx=ast.Load(),
            ),
            ast.Constant(value=self.select_num),
            ast.Constant(value=self.cap_weight),
            ast.Constant(value=self.rebalance_time),
            ast.List(
                elts=[factor.build() for factor in self.factor_list], ctx=ast.Load()
            ),
            ast.List(
                elts=[filter.build() for filter in self.filter_list], ctx=ast.Load()
            ),
        ]

        if self.timing:
            values.append(self.timing.build())

        return ast.Dict(keys=keys, values=values)


class StrategyList(ActiveBaseModel):
    """
    [策略列表](https://bbs.quantclass.cn/thread/51962)
    """

    name: str
    "策略名称"

    strategy_list: list[StrategyConfig] = []
    "策略列表"

    def append(self, *strategies: StrategyConfig):
        self.strategy_list.extend(strategies)
        return self

    def build(self, path: Path):
        """生成更美观的Python格式配置文件"""

        backtest_assign = ast.Assign(
            targets=[ast.Name(id="backtest_name", ctx=ast.Store())],
            value=ast.Constant(value=self.name),
        )

        strategy_list_assign = ast.Assign(
            targets=[ast.Name(id="strategy_list", ctx=ast.Store())],
            value=ast.List(
                elts=[strategy.build() for strategy in self.strategy_list],
                ctx=ast.Load(),
            ),
        )

        module = ast.Module(
            body=[backtest_assign, strategy_list_assign], type_ignores=[]
        )

        ast.fix_missing_locations(module)

        code_str = ast.unparse(module)
        code_str = format_code(code_str)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code_str)

        return path
