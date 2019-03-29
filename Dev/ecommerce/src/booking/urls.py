from django.conf.urls import url


from .views import ( 
        book_home,
        book_update,
        checkout_home 
        
        )
                                  
     

urlpatterns = [ 
    url(r'^$', book_home, name='home'),
    url(r'^checkout/$', checkout_home, name='checkout'),
    url(r'^update/$', book_update, name='update'),
    ]   



