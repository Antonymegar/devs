import math
from django.db import models
from addresses.models import Address
from django.db.models.signals import pre_save, post_save
from billing.models import BillingProfile
from booking.models import Book


from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = (
    ('created ', 'Created'),
    ('paid ', 'Paid'), 
    ('booked ', 'Booked'),  
    ('refunded ', 'Refunded'),
)




class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, book_obj):
        created = False
        qs = self.get_queryset().filter(billing_profile=billing_profile, book=book_obj, active=True)
        if qs.count() == 1:


            obj = qs.first()
        else:
            

            obj = self.model.objects.create(billing_profile=billing_profile, book=book_obj)
            created = True
        return obj, created


class Order(models.Model):
    billing_profile  = models.ForeignKey(BillingProfile, null=True, blank=True) 
    order_id         = models.CharField(max_length=120, blank=True) # AB31DE4
    reserved_address = models.ForeignKey(Address, related_name="reserved_address", null=True, blank=True)
    billing_address  = models.ForeignKey(Address, related_name="billing_address",  null=True, blank=True)
    book             = models.ForeignKey(Book)
    status           = models.CharField(max_length=120,  default='created ', choices=ORDER_STATUS_CHOICES)
    advance_total    = models.DecimalField(default=12.99, max_digits=100, decimal_places=2)
    total            = models.DecimalField(default=0.00,  max_digits=100, decimal_places=2)
    active           = models.BooleanField(default=True)



    def __str__(self):
    	return self.order_id


    objects = OrderManager()

    def update_total(self):
        book_total = self.book.total
        advance_total= self.advance_total
        new_total = math.fsum([book_total, advance_total])
        formatted_total = format(new_total, '.2f')
        self.total = formatted_total
        self.save()
        return new_total


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(book=instance.book).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)
pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_book_total(sender,instance, created, *args, **kwargs):
	if not created:
		book_obj = instance
		book_total = book_obj.total
		book_id = book_obj.id
		qs = Order.objects.filter(book__id=book_id)
		if qs.count() == 1:
			order_obj = qs.first()
			order_obj.update_total()
post_save.connect(post_save_book_total, sender=Book)


def post_save_order(sender, instance, created, *args, **kwargs):
    print("running")
    if created:
        print("Updating....first")
        instance.update_total()
post_save.connect(post_save_order, sender=Order)
