from django.db import models


# Create your models here.


class Tag(models.Model):
    """（epon，ISP接入、pop、cmts pop、core、BRAS、SR、PE、公安监控eopn、出口、电子政务网核心、电子政务网接入、郊县BRAS、郊县POP、）"""
    name = models.CharField(max_length=32)
    version = models.ForeignKey("Version", on_delete=models.PROTECT, null=True,blank=True)
    authmode = models.ForeignKey("AuthMode",on_delete=models.PROTECT, null=True,blank=True)
    company = models.ForeignKey("Company", on_delete=models.PROTECT, null=True,blank=True)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        if self.version and self.authmode and self.company:
            return "%s/%s/%s/%s"%(self.name,self.company,self.version,self.authmode)
        return self.name


class Device(models.Model):
    name = models.CharField(max_length=32, null=True, verbose_name="设备名称", blank=True)
    IP = models.GenericIPAddressField(verbose_name="管理IP", unique=True)
    tag = models.ForeignKey("Tag", on_delete=models.PROTECT)  # 可以尝试关联tag的name字段试试
    enable = models.BooleanField(default=False, verbose_name="是否可用")

    """Device与Version、AuthMode、Company做了外键关系，
    Tag与Version、AuthMode、Company做了多对多关系，
    Device对象添加外键关系时，是通过选择tag对象关联的Version对象、AuthMode对象、Company对象来进行关系绑定的"""
    class Meta:
        verbose_name = "网络设备"
        verbose_name_plural = "网络设备"

    def __str__(self):
        if self.name:
            return self.name + self.IP
        else:
            return self.IP


class Version(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "软件版本"
        verbose_name_plural = "软件版本"

    def __str__(self):
        return self.name


class AuthMode(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "认证方式"
        verbose_name_plural = "认证方式"

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = "厂商"
        verbose_name_plural = "厂商"

    def __str__(self):
        return self.name


class Olt(models.Model):
    name = models.CharField(max_length=32,default="None")
    interface = models.CharField(max_length=32,)
    epon = models.ForeignKey("Device",on_delete=models.CASCADE)
    silent_onus = models.CharField(max_length=128,default="None")

    class Meta:
        unique_together = (("interface","epon"),)

    def __str__(self):
        return "%s:%s"%(self.name,self.interface)


class Onu(models.Model):
    interface = models.CharField(max_length=32, null=True)
    mac = models.CharField(max_length=32, null=True)
    olt = models.ForeignKey("Olt", on_delete=models.CASCADE)

    class Meta:
        unique_together = (("interface", "olt"),)

    def __str__(self):
        return "%s:%s"%(self.interface,self.mac)
    #
    # onu表
    # onu名称、onu
    # mac、外键绑定的olt
    # onu和olt做联合唯一
