"""Set of constants such as user-facing strings."""

from rime_sdk.swagger.swagger_client.models import (
    MonitorMonitorType,
    RiskscoreRiskCategoryType,
)

# User-facing strings for Monitor types.
MONITOR_TYPE_DEFAULT_STR: str = "Default"
MONITOR_TYPE_CUSTOM_STR: str = "Custom"
MONITOR_TYPE_TO_SWAGGER = {
    MONITOR_TYPE_DEFAULT_STR: MonitorMonitorType.DEFAULT,
    MONITOR_TYPE_CUSTOM_STR: MonitorMonitorType.CUSTOM,
}

# User-facing strings for Risk Categories.
RISK_CATEGORY_OPERATIONAL_STR: str = "Operational"
RISK_CATEGORY_BIAS_AND_FAIRNESS_STR: str = "Bias_and_Fairness"
RISK_CATEGORY_SECURITY_STR: str = "Security"
RISK_CATEGORY_CUSTOM_STR: str = "Custom"
RISK_CATEGORY_TO_SWAGGER = {
    RISK_CATEGORY_OPERATIONAL_STR: RiskscoreRiskCategoryType.OPERATIONAL_HEALTH,
    RISK_CATEGORY_BIAS_AND_FAIRNESS_STR: RiskscoreRiskCategoryType.ETHICAL_RISK,
    RISK_CATEGORY_SECURITY_STR: RiskscoreRiskCategoryType.SECURITY_RISK,
    RISK_CATEGORY_CUSTOM_STR: RiskscoreRiskCategoryType.CUSTOM,
}
