# from cms.plugin_base import CMSPluginBase
# from cms.plugin_pool import plugin_pool
# from django.utils.translation import ugettext_lazy as _
#
# from .models import University
#
# @plugin_pool.register_plugin
# class FormPlugin(CMSPluginBase):
#     model = University
#     name = _("Anketa")
#     render_template = "criteria.html"
#     cache = False
#
#     def render(self, context, instance, placeholder):
#         context = super(FormPlugin, self).render(context, instance, placeholder)
#         return context