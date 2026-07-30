from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project


class Sales(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    product_name = models.CharField(
        _("Nome do produto"), max_length=100, null=False, blank=False
    )
    product_price = models.DecimalField(
        _("Preco do produto"), decimal_places=2, max_digits=12
    )
    product_quantity = models.PositiveIntegerField(
        _("Quantidade do produto"), default=1
    )
    description = models.CharField(
        _("Descricao"), max_length=300, null=True, blank=True
    )
    extra_data = models.JSONField(_("Extra"), default=dict, null=True, blank=True)

    sold_at = models.DateTimeField(
        _("Data da venda"), default=None, null=True, blank=True
    )
    created_at = models.DateTimeField(_("Data de registo"), auto_now_add=True)

    def asave(self, *args, **kwargs):
        if not self.sold_at:
            self.sold_at = self.created_at
        return super().asave(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.sold_at:
            self.sold_at = self.created_at
        return super().save(*args, **kwargs)

    def get_total(self):
        return self.product_price * self.product_quantity

    def __str__(self):
        return f"{self.project.name} - {self.product_name}: {self.get_total()}"

    class Meta:
        verbose_name = _("Venda")
        verbose_name_plural = _("Vendas")
