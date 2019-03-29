from django.shortcuts import render, redirect
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail

from addresses.forms import AddressForm
from addresses.models import Address
from billing.models import BillingProfile

from orders.models import Order

from products.models import Product
from .models import Book
  



    

def book_home(request):
	book_obj, new_obj = Book.objects.new_or_get(request)
	
	  
	return render(request,"booking/home.html", {"book": book_obj})

def	book_update(request):

	product_id = request.POST.get('product_id')
	if product_id is not None:
		try:
			product_obj = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
		    print("Show message to user ,Room is gone?")
		    return redirect("book:home")	
	
	book_obj, new_obj = Book.objects.new_or_get(request)
	if product_obj in book_obj.products.all():
		book_obj.products.remove(product_obj)
		
	else:	

	    book_obj.products.add(product_obj)
	request.session['book_items'] = book_obj.products.count()    

	     #book_obj.products.add(product_id)
	
	# return redirect(product_obj.get_absolute_url())
	return redirect("book:home")

def checkout_home(request):
	book_obj, book_created = Book.objects.new_or_get(request)
	order_obj = None
	if book_created or book_obj.products.count() == 0:
		return redirect("book:home")   
	
	login_form = LoginForm()
	guest_form = GuestForm()
	address_form = AddressForm()
	billing_address_id = request.session.get("billing_address_id", None)
	reserved_address_id = request.session.get("reserved_address_id",None)

	
	billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request) 
	
	if billing_profile is not None:
		order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, book_obj)
		if reserved_address_id:
			order_obj.reserved_address = Address.objects.get(id=reserved_address_id)
			del request.session["reserved_address_id"]
		if billing_address_id:
			order_obj.billing_address = Address.objects.get(id=billing_address_id)
			del request.session["billing_address_id"]
		if billing_address_id or reserved_address_id:
			order_obj.save()

			


	context = {
	    "object": order_obj,
	    "billing_profile": billing_profile,
	    "login_form": login_form,
	    "guest_form": guest_form,
	    "address_form": address_form
	    

	}

	return render(request, "booking/checkout.html", context)

