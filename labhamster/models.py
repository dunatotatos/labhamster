# Copyright 2016 - 2018 Raik Gruenberg

# This file is part of the LabHamster project (https://github.com/graik/labhamster).
# LabHamster is released under the MIT open source license, which you can find
# along with this project (LICENSE) or at <https://opensource.org/licenses/MIT>.

from django.db import models
from django.contrib.auth.models import User
from .customfields import DayModelField, DayConversion
from djmoney.models.fields import MoneyField
from datetime import date
from . import tools as T

APP_URL = '/labhamster'


class Order(models.Model):
    STATUS_TYPES = (('draft', 'draft'),
                    ('pending', 'pending'),
                    ('quote', 'quote requested'),
                    ('ordered', 'ordered'),
                    ('received', 'received'),
                    ('cancelled', 'cancelled'))

    status = models.CharField('Status', max_length=20, choices=STATUS_TYPES,
                              default='pending')

    is_urgent = models.BooleanField('Urgent!', default=False,
                                    help_text='Mark this order as urgent')

    date_created = models.DateField('requested', auto_now_add=True,
                                    help_text='Date when order was created')

    date_ordered = models.DateField('ordered', blank=True, null=True,
                                    help_text='Date when order was placed')

    date_received = models.DateField('received', blank=True, null=True,
                                     help_text='Date when product was received')

    # recent Django Admin version do not sort users any longer
    # workaround with custom form:
    # https://code.djangoproject.com/ticket/8220
    created_by = models.ForeignKey(User, null=False, blank=False, db_index=True,
                                   verbose_name='requested by',
                                   related_name='requests',
                                   help_text='user who created this order')

    ordered_by = models.ForeignKey(User, null=True, blank=True, db_index=True,
                                   verbose_name='ordered by',
                                   related_name='orders',
                                   help_text='user who sent this order out')

    po_number = models.CharField('P.O.number',
                                 max_length=20, blank=True, null=True,
                                 help_text='')

    product = models.ForeignKey('Product', verbose_name='Product', related_name='orders',
                                blank=False, null=False,
                                help_text='Click the magnifying lens to select from the list of existing products.\n' +
                                'For a new product, first click the lens, then click "Add Product" and fill out and save the Product form.')

    unit_size = models.CharField(max_length=20, blank=True, null=True,
                                 help_text='e.g. "10 l", "1 kg", "500 tips"')

    quantity = models.IntegerField(default=1,
                                   help_text='number of units ordered')
    price = MoneyField('Unit price', max_digits=8, decimal_places=2,
                       default_currency='USD',
                       blank=True, null=True,
                       help_text='cost per unit (!)')

    grant_category = models.CharField('Grant category',
                                      choices=(('consumables', 'consumables'),
                                               ('equipment', 'equipment')),
                                      default='consumables', max_length=20)

    grant = models.ForeignKey('Grant', null=True, blank=True, db_index=True,
                              related_name='orders')

    comment = models.TextField(blank=True,
                               help_text="Order-related remarks. " +
                               "Please put catalog number and descriptions not here but into the " +
                               "product page.")

    def __str__(self):
        return '%04i -- %s' % (self.id, self.product)

    def get_absolute_url(self):
        """
        Define standard URL for object.get_absolute_url access in templates
        """
        return APP_URL + '/' + self.get_relative_url()

    def get_relative_url(self):
        """
        Define standard relative URL for object access in templates
        """
        return 'order/%i/' % self.id

    def save(self, *args, **kwargs):
        if self.status == "ordered" and self.date_ordered is None:
            self.date_ordered = date.today()
        elif self.status == "received" and self.date_received is None:
            self.date_received = date.today()
        super(Order, self).save(*args, **kwargs)

    def Status(self):
        """color status display"""
        color = {'ordered': '088A08',
                 'pending': 'B40404'}
        return '<span style="color: #%s;">%s</span>' %\
               (color.get(self.status, '000000'), self.status)

    Status.allow_tags = True
    Status.admin_order_field = 'status'

    def requested(self):
        """filter '(None)' display in admin table"""
        if self.date_created:
            return self.date_created
        return ''

    requested.allow_tags = True
    requested.admin_order_field = 'date_created'

    def ordered(self):
        """filter '(None)' display in admin table"""
        if self.date_ordered:
            return self.date_ordered
        return ''

    ordered.allow_tags = True
    ordered.admin_order_field = 'date_ordered'

    def received(self):
        """filter '(None)' display in admin table"""
        if self.date_received:
            return self.date_received
        return ''

    received.allow_tags = True
    received.admin_order_field = 'date_received'

    def Price(self):
        """filter '(None)' display in admin table"""
        if self.price:
            return self.price
        return ''

    Price.allow_tags = True
    Price.short_description = 'Unit price'
    Price.admin_order_field = 'price'

    class Meta:
        ordering = ('date_created', 'id')


class Product(models.Model):

    name = models.CharField(max_length=60, unique=True,
                            help_text='short descriptive name of this product')

    vendor = models.ForeignKey('Vendor', verbose_name='Vendor',
                               blank=False,
                               help_text='select normal supplier of this product')

    catalog = models.CharField(max_length=30, unique=False, blank=False,
                               help_text='vendor catalogue number')

    manufacturer = models.ForeignKey('Vendor', verbose_name='Manufacturer',
                                     blank=True, null=True,
                                     related_name='manufacturer_product',
                                     help_text='original manufacturer if different')

    manufacturer_catalog = models.CharField(max_length=30, unique=False,
                                            blank=True,
                                            help_text='manufacturer catalogue number')

    category = models.ForeignKey('Category', verbose_name='Product Category',
                                 blank=False)

    shelflife = DayModelField(verbose_name='Shelf Life', unit='months',
                              blank=True, null=True)

    STATUS_TYPES = (('ok', 'in stock'),
                    ('low', 'running low'),
                    ('out', 'not in stock'),
                    ('expired', 'expired'),
                    ('deprecated', 'deprecated'))

    status = models.CharField('Status', max_length=20, choices=STATUS_TYPES,
                              default='out')

    link = models.URLField('Product Link', blank=True,
                           help_text='Product web site')

    comment = models.TextField('comments & description', blank=True,
                               help_text='')

    location = models.CharField(max_length=60, blank=True,
                                help_text='location in the lab')

    def __str__(self):
        return '%s [%s]' % (self.name, self.vendor)

    def get_absolute_url(self):
        """
        Define standard URL for object.get_absolute_url access in templates
        """
        return APP_URL + '/' + self.get_relative_url()

    def get_relative_url(self):
        """
        Define standard relative URL for object access in templates
        """
        return 'product/%i/' % self.id

    def related_orders(self):
        """
        @return: QuerySet of orders for this product
        """
        if self.orders:
            r = Order.objects.filter(product=self)
            return r
        return []

    def received(self):
        """filter '(None)' display in admin table"""
        if self.date_received:
            return self.date_received
        return ''

    received.allow_tags = True
    received.admin_order_field = 'date_ordered'

    def shelf_life(self):
        """filter '(None)' display in admin table"""
        if not self.shelflife:
            return ''
        return DayConversion.days2str(self.shelflife)

    class Meta:
        ordering = ('name', 'vendor')


class Vendor(models.Model):

    name = models.CharField(max_length=30, unique=True,
                            verbose_name='Vendor name',
                            help_text='short descriptive name of this supplier')

    link = models.URLField(blank=True,
                           help_text='URL Link to Vendor home page')

    phone = models.CharField(max_length=20, blank=True,
                             verbose_name='Phone')

    email = models.CharField(max_length=30, blank=True,
                             verbose_name='E-mail')

    contact = models.CharField(max_length=30, blank=True,
                               verbose_name='Primary contact name')

    login = models.CharField(max_length=50, blank=True,
                             verbose_name='Account Login')

    password = models.CharField(max_length=30, blank=True,
                                verbose_name='Password')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Define standard URL for object.get_absolute_url access in templates
        """
        return APP_URL + '/' + self.get_relative_url()

    def get_relative_url(self):
        """
        Define standard relative URL for object access in templates
        """
        return 'vendor/%i/' % self.id


class Category(models.Model):

    name = models.CharField(max_length=20, unique=True,
                            verbose_name='Product Category',
                            help_text='name of product category')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)


class Grant(models.Model):

    name = models.CharField(max_length=40, unique=True,
                            help_text='descriptive name of grant')

    grant_id = models.CharField(max_length=30, unique=True, blank=True)

    active = models.BooleanField('Active', default=True)

    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name + ' ' + self.grant_id

    class Meta:
        ordering = ('name', 'grant_id')
        verbose_name = 'Grant'
