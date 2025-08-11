"""
OSLisLim 异常类定义
"""


class OSLisLimError(Exception):
    """OSLisLim 基础异常类"""
    pass


class ValidationError(OSLisLimError):
    """验证失败异常"""
    pass


class ProtectionError(OSLisLimError):
    """保护机制异常"""
    pass


class LicenseNotFoundError(ValidationError):
    """许可证文件未找到异常"""
    pass


class CodeIntegrityError(ValidationError):
    """代码完整性检查失败异常"""
    pass


class UnauthorizedUsageError(ProtectionError):
    """未授权使用异常"""
    pass


class CommercialUsageDetectedError(ProtectionError):
    """检测到商业使用异常"""
    pass
