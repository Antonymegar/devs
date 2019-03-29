from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed


from products.models import Product

User = settings.AUTH_USER_MODEL

class BookManager(models.Manager):
	def new_or_get(self, request):
		book_id = request.session.get("book_id", None)
		qs = self.get_queryset().filter(id=book_id)
		if qs.count() == 1:	
		    new_obj = False
		    book_obj = qs.first()
		    if request.user.is_authenticated() and book_obj.user is None:
		    	book_obj.user = request.user
		    	book_obj.save()
		else:
		    book_obj = Book.objects.new(user=request.user)
		    new_obj = True
		    request.session['book_id'] = book_obj.id    
		return book_obj, new_obj

	def new(self, user=None):
		user_obj = None
		if user is not None:
			if user.is_authenticated():
				user_obj = user

      

		return self.model.objects.create(user=user_obj)


class Book(models.Model):
	user        = models.ForeignKey(User, null=True, blank=True)
	products    = models.ManyToManyField(Product, blank=True)
	subtotal    = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	total       = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	updated     = models.DateTimeField(auto_now=True)
	timestamp   = models.DateTimeField(auto_now_add=True)

	objects = BookManager()

	def __str__(self):
		return str(self.id)


def m2m_changed_book_receiver(sender, instance, action, *args, **kwargs):
	if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
		products = instance.products.all()
		total = 0
		for x in products:
			total += x.price
		if instance.subtotal != total:
		   instance.subtotal = total
		   instance.save()

m2m_changed.connect(m2m_changed_book_receiver, sender=Book.products.through)


def pre_save_book_receiver(sender, instance, *args, **kwargs):
	if instance.subtotal > 0:
		instance.total = Decimal(instance.subtotal) *Decimal(1.08) # 8% tax
	else:
	    instance.total = 0.00	

pre_save.connect(pre_save_book_receiver, sender=Book)	



	  




