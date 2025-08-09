from typing import Literal
from pydantic import BaseModel

type Operator = Literal["<", ">", "==", "!=", ">=", "<="]

class Expr(BaseModel):
    "expression 表达式"
    
    expr_type: str
    operator: Operator
    value: float | int

    def build(self):
        return f"{self.expr_type}:{self.operator}{self.value}"
    

    @classmethod
    def pct(cls, operator: Operator, value: float):
        """
        百分比表达式, 例如: 以市值因子举例, Expr.pct("<", 0.2) 就是保留排序前20%, 剔除后80%的股票; 就是保留市值最小20%的股票, 剔除市值大的80%的股票;
        - 注意: 百分比表达式只能使用小数, 不能使用整数。
        - Operator 只能使用 <, >, ==, !=, >=, <=
        """
        return cls(expr_type="pct", operator=operator, value=value)


    @classmethod
    def rank(cls, operator: Operator, value: int):
        """
        排名表达式, 例如: 以市值因子举例, Expr.rank(">", 1) 保留排名大于1的股票; 按照True从小到大排序, 就是剔除掉市值最小的股票;
        - 注意: 排名表达式只能使用整数, 不能使用小数。
        - Operator 只能使用 <, >, ==, !=, >=, <=
        """
        return cls(expr_type="rank", operator=operator, value=value)
    

    @classmethod
    def val(cls, operator: Operator, value: float | int):
        """
        值表达式, 例如: 以市值因子举例, Expr.val("<", 1_0000_0000) 就是保留市值小于1亿的股票, 剔除市值大于等于1亿的股票。
        - 注意: 值表达式只能使用整数, 不能使用小数。
        - Operator 只能使用 <, >, ==, !=, >=, <=
        """
        return cls(expr_type="val", operator=operator, value=value)