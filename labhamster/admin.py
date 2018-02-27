## Copyright 2016 - 2018 Raik Gruenberg

## This file is part of the LabHamster project (https://github.com/graik/labhamster). 
## LabHamster is released under the MIT open source license, which you can find
## along with this project (LICENSE) or at <https://opensource.org/licenses/MIT>.
from __future__ import unicode_literals

from labhamster.models import *
from django.contrib import admin
import django.forms
from django.http import HttpResponse
import django.utils.html as html

import customforms

def export_csv(request, queryset, fields):
    """
    Helper method for Admin make_csv action. Exports selected objects as 
    CSV file.
    fields - OrderedDict of name / field pairs, see Product.make_csv for example
    """
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=orders.csv'
    
    writer = csv.writer(response)
    writer.writerow(fields.keys())

    for o in queryset:
        columns = []
        for name,value in fields.items():
            try:
                columns.append( eval('o.%s'%value) )
            except:
                columns.append("")  ## capture 'None' fields

        columns = [ c.encode('utf-8') if type(c) is unicode else c \
                    for c in columns]
            
        writer.writerow( columns )

    return response
    

class RequestFormAdmin(admin.ModelAdmin):
    """
    ModelAdmin that adds a 'request' field to the form generated by the Admin.
    This e.g. allows to extract the user ID during the creation of the form.
    """

    def get_form(self, request, obj=None, **kwargs):
        """
        Assign request variable to form
        http://stackoverflow.com/questions/1057252/how-do-i-access-the-request-object-or-any-other-variable-in-a-forms-clean-met
        (last answer, much simpler than Django 1.6 version)
        """
        form = super(RequestFormAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form   


class GrantAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Grant, GrantAdmin)

class CategoryAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Category, CategoryAdmin)


class VendorAdmin(admin.ModelAdmin):

    fieldsets = ((None, {'fields': (('name',),
                                    ('link', 'login', 'password'),)}),
                 ('Contact', {'fields' : (('contact',),
                                          ('email','phone'),)})
                 )


    list_display = ('name', 'link', 'login', 'password')

    ordering = ('name',)
    search_fields = ('name', 'contact')

admin.site.register(Vendor, VendorAdmin)

class ProductAdmin(admin.ModelAdmin):
    fieldsets = ((None, {'fields': (('name', 'category'),
                                    ('vendor', 'catalog'), 
                                    ('manufacturer', 'manufacturer_catalog'),
                                    'link',
                                    ('status', 'shelflife'),
                                    'comment',
                                    'location')}),)
    
    list_display = ('show_name', 'show_vendor', 'category', 'show_catalog',
                     'status')
    list_filter = ('status', 'category', 'vendor')

    ordering = ('name',)
    search_fields = ('name', 'comment', 'catalog', 'location', 'vendor__name',
                     'manufacturer__name', 'manufacturer_catalog')

    save_as = True

    actions = ['make_ok',
               'make_low',
               'make_out',
               'make_deprecated',
               'make_csv']

    ## reduce size of Description text field.
    formfield_overrides = {
        models.TextField: {'widget': django.forms.Textarea(
            attrs={'rows': 4,
                   'cols': 80})},
    }    

    def make_ok(self, request, queryset):
        n = queryset.update(status='ok')
        self.message_user(request, '%i products were updated' % n)

    make_ok.short_description = 'Mark selected entries as in stock'

    def make_low(self, request, queryset):
        n = queryset.update(status='low')
        self.message_user(request, '%i products were updated' % n)

    make_low.short_description = 'Mark selected entries as running low'

    def make_out(self, request, queryset):
        n = queryset.update(status='out')
        self.message_user(request, '%i products were updated' % n)

    make_out.short_description = 'Mark selected entries as out of stock'

    def make_deprecated(self, request, queryset):
        n = queryset.update(status='deprecated')
        self.message_user(request, '%i products were updated' % n)

    make_deprecated.short_description = 'Mark selected entries as deprecated'
    
    def make_csv(self, request, queryset):
        from collections import OrderedDict
        
        fields = OrderedDict( [('Name', 'name'),
                               ('Vendor', 'vendor.name'),
                               ('Vendor Catalog','catalog'),
                               ('Manufacturer', 'manufacturer.name'),
                               ('Manufacturer Catalog', 'manufacturer_catalog'),
                               ('Category','category.name'),
                               ('Shelf_life','shelflife'),
                               ('Status','status'),
                               ('Location','location'),
                               ('Link','link'),
                               ('Comment','comment')])
        return export_csv( request, queryset, fields)
    
    make_csv.short_description = 'Export products as CSV'


    def show_name(self, o):
        """truncate product name to less than 40 char"""
        from django.utils.safestring import SafeUnicode
        return html.format_html(
            '<a href="{url}" title="{comment}">{name}</a>', 
                url=o.get_absolute_url(),
                name=T.truncate(o.name, 40),
                comment=SafeUnicode(o.comment))
    show_name.short_description = 'Name'
    show_name.admin_order_field = 'name'

    def show_vendor(self, o):
        """Display in table: Vendor (Manufacturer)"""
        r = o.vendor.name
        if o.manufacturer:
            r += '<br>(%s)' % o.manufacturer.name
        return html.format_html(r)
    show_vendor.admin_order_field = 'vendor'
    show_vendor.short_description = 'Vendor'
    
    def show_catalog(self, o):
        return T.truncate(o.catalog, 15)
    show_catalog.short_description = 'Catalog'
    show_catalog.admin_order_field = 'catalog'

admin.site.register(Product, ProductAdmin)


class OrderAdmin(RequestFormAdmin):
    form = customforms.OrderForm
    
    raw_id_fields = ('product',)

    fieldsets = ((None, 
                  {'fields': (('status', 'is_urgent', 'product',), 
                              ('created_by', 'ordered_by', 'date_ordered', 
                               'date_received'))}),
                 ('Details', {'fields': (('unit_size', 'quantity'),
                                         ('price', 'po_number'),
                                         ('grant', 'grant_category'),
                                         'comment')}))
    
    radio_fields = {'grant': admin.VERTICAL,
                    'grant_category': admin.VERTICAL}
    
    list_display = ('show_title',  'Status', 'show_urgent', 
                    'show_quantity', 'show_price', 
                    'requested', 'show_requestedby', 'ordered', 
                    'received', 'show_comment',)

    list_filter = ('status', 
                   'product__category__name', 'grant', 'created_by', 'product__vendor__name',)
    ordering = ('-date_created', 'product', '-date_ordered') #, 'price')

    search_fields = ('comment', 'grant__name', 'grant__grant_id', 'product__name', 
                     'product__vendor__name')

    save_as = True

    date_hierarchy = 'date_created'

    actions = ['make_ordered', 'make_received', 'make_cancelled', 'make_csv']
    
    def show_title(self, o):
        """truncate product name + supplier to less than 40 char"""
        n = T.truncate(o.product.name, 40)
        v = o.product.vendor.name
        r = html.format_html('<a href="{}">{}', o.get_absolute_url(), n)
        r += '<br>' if len(n) + len(v) > 37 else ' '
        r += html.format_html('[{}]</a>',v)
        return html.mark_safe(r)
    show_title.short_description = 'Product'
        
    
    def show_comment(self, obj):
        """
        @return: str; truncated comment with full comment mouse-over
        """
        if not obj.comment: 
            return ''
        if len(obj.comment) < 30:
            return obj.comment
        r = obj.comment[:28]
        r = '<a title="%s">%s</a>' % (obj.comment, T.truncate(obj.comment, 30))
        return r
    show_comment.short_description = 'comment'
    show_comment.allow_tags = True
    

    def show_price(self, o):
        """Workaround for bug in djmoney -- MoneyField confuses Admin formatting"""
        if not o.price:
            return ''
        return o.price
    show_price.admin_order_field = 'price'
    show_price.short_description = 'Unit price'

    def show_urgent(self, o):
        """Show exclamation mark if order is urgent"""
        if not o.is_urgent:
            return ''
        return html.format_html(
            '<big>&#10071;</big>')
    show_urgent.admin_order_field = 'is_urgent'
    show_urgent.short_description = '!'

    def show_requestedby(self,o):
        return o.created_by
    show_requestedby.admin_order_field = 'created_by'
    show_requestedby.short_description = 'By'
    

    def show_quantity(self, o):
        return o.quantity
    show_quantity.short_description = 'Q'

    def make_ordered(self, request, queryset):
        """
        Mark several orders as 'ordered'
        see: https://docs.djangoproject.com/en/1.4/ref/contrib/admin/actions/
        """
        import datetime
        n = queryset.update(status='ordered', ordered_by=request.user, 
                            date_ordered=datetime.datetime.now())
        self.message_user(request, '%i orders were updated' % n)

    make_ordered.short_description = 'Mark selected entries as ordered'

    def make_received(self, request, queryset):
        import datetime
        n = queryset.update(date_received=datetime.datetime.now(), 
                            status='received')
        i = 0
        for order in queryset:
            order.product.status = 'ok'
            order.product.save()
            i += 1

        self.message_user(request, 
                          '%i orders were updated and %i products set to "in stock"'\
                          % (n, i))

    make_received.short_description= 'Mark as received (and update product status)'

    def make_cancelled(self, request, queryset):
        import datetime

        n = queryset.update(date_received=None, date_ordered=None, 
                            status='cancelled')
        self.message_user(request, '%i orders were set to cancelled' % n)

    make_cancelled.short_description = 'Mark selected entries as cancelled'
    

    def make_csv(self, request, queryset):
        """
        Export selected orders as CSV file
        """
        from collections import OrderedDict
       
        fields = OrderedDict( [('Product', 'product.name'),
                               ('Quantity', 'quantity'),
                               ('Price','price'),
                               ('Vendor','product.vendor.name'),
                               ('Catalog','product.catalog'),
                               ('PO Number', 'po_number'),
                               ('Requested','date_created'),
                               ('Requested by','created_by.username'),
                               ('Ordered','date_ordered'),
                               ('Ordered by','ordered_by.username'),
                               ('Received','date_received'),
                               ('Status','status'),
                               ('Urgent','is_urgent'),
                               ('Comment','comment')])
        
        return export_csv(request, queryset, fields)
    
    make_csv.short_description = 'Export orders as CSV'


admin.site.register(Order, OrderAdmin)
