from MignonFramework import GenericProcessor
from datetime import datetime
from MignonFramework.GenericProcessor import Rename

def parseJson(dic: dict) -> dict:
    return {
        "PlanEndDate": Rename("plan_end_date"),  # 仅改名用来对应字段
        "Fundingfloat": Rename("funding_float"),
        "Budgetfloat": ("budget_floats", dic.get("Budgetfloat")), # 改名同时修改逻辑(或新增)
        "Fundingfloats": dic.get("Fundingfloat") # 仅改逻辑
    }


def filterFun(dicts: dict, lineNo) -> bool:
    # 过滤器方法 解析后执行, 当且仅当返回True时才会insert
    return True

# 默认值
defaultVal = {
    "PlanEndDate": datetime.now(),
    "CompleteDate": datetime.now(),
    "StartYear": "2025",
    "Fundingfloat": 0.0,
    "Budgetfloat": 0.0,
    "PlanStartDate": datetime.now(),
    "ApplyYear": "2025",
    "has_outcome": True
}

# 排除字段
exclude = [
    "ForCodeForSearchs", "outComes", "AwardeeOrgState", "projectAbstract"
]

GenericProcessor.GenericFileProcessor(modifier_function=parseJson, default_values=defaultVal, filter_function=filterFun,
                                      exclude_keys=exclude).run()
