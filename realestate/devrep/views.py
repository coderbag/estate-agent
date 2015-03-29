# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from devrep.models import Partner, WorkType, ClientPartner, Gear
from django.views.generic.edit import CreateView, ModelFormMixin, DeleteView,\
    UpdateView
from estatebase.helpers.functions import safe_next_link
from devrep.forms import PartnerForm, ClientPartnerThroughUpdateForm,\
    AddressForm
from django.views.generic.detail import DetailView
from estatebase.views import DeleteMixin, ClientListView, BaseMixin
from estatebase.models import prepare_history, Client
from django.http import HttpResponseRedirect, Http404, HttpResponse
from estatebase.forms import ClientFilterForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape, escapejs
from django.core.urlresolvers import reverse

class PartnerListView(ListView):    
    filtered = False
    template_name = 'partner_list.html'
    paginate_by = 7      
    def get_queryset(self):        
        q = Partner.objects.all()        
        #filter_form = self.filter_form(self.request.GET)
        #filter_dict = filter_form.get_filter()        
        #if filter_dict:
        #    self.filtered = True                    
        #q = set_estate_filter(q, filter_dict, user=self.request.user)
        order_by = self.request.fields 
        if order_by:      
            return q.order_by(','.join(order_by))
        return q
    def get_context_data(self, **kwargs):
        context = super(PartnerListView, self).get_context_data(**kwargs)
#         filter_form = self.filter_form(self.request.GET)
#         
        params = self.request.GET.copy()      
        get_params = params.urlencode()
                   
        context.update({            
            'next_url': safe_next_link(self.request.get_full_path()),
            'total_count': Partner.objects.count(),
            'filter_count' : self.get_queryset().count(),
#             'filter_form': filter_form,
#             'filter_action': '%s?next=%s' % (reverse('estate-list'), self.request.GET.get('next','')),
            'filtered' :self.filtered,
            'get_params': get_params,
        })        
        return context

class PartnerMixin(ModelFormMixin):    
    form_class = PartnerForm
    template_name = 'partner_form.html'
    model = Partner 
    def form_valid(self, form):
        context = self.get_context_data()
        address_form = context['address_form']
        if address_form.is_valid():
            address = address_form.save()             
            self.object = form.save(commit=False)        
            self.object._user_id = self.request.user.pk
            self.object.address = address                
            return super(PartnerMixin, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):   
        next_url = self.request.REQUEST.get('next', '')         
        if '_continue' in self.request.POST:                  
            return '%s?%s' % (reverse('partner_update', args=[self.object.id]), safe_next_link(next_url)) 
        return next_url
            
    def get_context_data(self, **kwargs):
        context = super(PartnerMixin, self).get_context_data(**kwargs)
        address = self.object.address if self.object else None
        if self.request.POST:
            if not 'address_form' in context:                  
                context['address_form'] = AddressForm(self.request.POST, instance=address)
        else:
            context['address_form'] = AddressForm(instance=address)
        context.update({
            'dialig_title' : u'Добавление нового партнера',            
        })    
        return context
    
        
class PartnerCreateView(PartnerMixin, CreateView): 
    pass    

class PartnerUpdateView(PartnerMixin, UpdateView):
    def get_context_data(self, **kwargs):
        context = super(PartnerUpdateView, self).get_context_data(**kwargs)
        context.update({
            'dialig_title' : u'Редактирование портнера [%s] «%s»' % (self.object.pk, self.object) 
        })        
        return context

class PartnerDetailView(PartnerMixin, DetailView):    
    template_name = 'partner_detail.html'
    def get_context_data(self, **kwargs):
        context = super(PartnerDetailView, self).get_context_data(**kwargs)                
        context.update({            
            'next_url': safe_next_link(self.request.get_full_path()),
        })        
        return context  
    
class PartnerDeleteView(DeleteMixin, PartnerMixin, DeleteView):
    template_name = 'confirm.html'
    def get_context_data(self, **kwargs):
        context = super(PartnerDeleteView, self).get_context_data(**kwargs)
        context.update({
            'dialig_title' : u'Удаление партнера...',
            'dialig_body'  : u'Подтвердите удаление партнера: %s' % self.object,
        })
        return context

class ClientPartnerSelectView(ClientListView):
    template_name = 'client_partner_select.html'
    def get_bid(self):
        bid = Partner.objects.get(pk=self.kwargs['partner_pk'])
        return bid            
    def get_context_data(self, **kwargs):         
        context = super(ClientPartnerSelectView, self).get_context_data(**kwargs)                    
        context.update ({            
            'partner' : self.get_bid(),
            'client_filter_form' : ClientFilterForm(self.request.GET),
        })        
        return context
    def get_queryset(self):
        q = super(ClientPartnerSelectView, self).get_queryset()
        q = q.exclude(bids_m2m__id=self.kwargs['partner_pk'])
        return q

class ClientPartnerUpdateView(DetailView):   
    model = Client
    template_name = 'confirm.html'
    PARTNER_CLIENT_STATUS = 1
    def get_context_data(self, **kwargs):
        context = super(ClientPartnerUpdateView, self).get_context_data(**kwargs)
        context.update({
            'dialig_title' : u'Привязка...',
            'dialig_body'  : u'Привязать работника %s к партнеру [%s]?' % (self.object, self.kwargs['partner_pk']),
        })
        return context
    def update_object(self, client_pk, partner_pk):
        ClientPartner.objects.create(client_id=client_pk, partner_id=partner_pk, partner_client_status_id=self.PARTNER_CLIENT_STATUS)                
    def post(self, request, *args, **kwargs):       
        self.update_object(self.kwargs['pk'], self.kwargs['partner_pk'])      
        prepare_history(Partner.objects.get(pk=self.kwargs['partner_pk']).history, self.request.user.pk)      
        return HttpResponseRedirect(self.request.REQUEST.get('next', ''))    

class ClientPartnerRemoveView(ClientPartnerUpdateView):    
    def get_context_data(self, **kwargs):
        context = super(ClientPartnerRemoveView, self).get_context_data(**kwargs)
        context.update({
            'dialig_title' : u'Отвязка...',
            'dialig_body'  : u'Отвязать работника %s от партнера [%s]?' % (self.object, self.kwargs['partner_pk']),
        })
        return context 
    def update_object(self, client_pk, partner_pk):                         
        ClientPartner.objects.get(partner_id=partner_pk, client_id=client_pk).delete() 

class ClientPartnerThroughUpdateView(BaseMixin, UpdateView):
    model = ClientPartner
    form_class = ClientPartnerThroughUpdateForm
    template_name = 'client_partner_through_update.html'
    def get_object(self, queryset=None):        
        client = self.kwargs.get('client', None)
        partner = self.kwargs.get('partner', None)
        if queryset is None:
            queryset = self.get_queryset()
        queryset =  queryset.filter(client=client, partner=partner)
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") % 
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class PopupCreateMixin(CreateView):
    title = None
    def get_context_data(self, **kwargs):
        context = super(PopupCreateMixin, self).get_context_data(**kwargs)
        context.update({
            'dialig_title' : self.title
        })        
        return context    
    def form_valid(self, form):
        self.object = form.save(commit=True)
        if  '_popup' in self.request.POST:            
            return HttpResponse(
            '<!DOCTYPE html><html><head><title></title></head><body>'
            '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script></body></html>' % \
            (escape(self.object.pk), escapejs(self.object)))                
        return super(PopupCreateMixin, self).form_valid(form)   

class GearCreateView(PopupCreateMixin):
    title = u'Добавление новой техники'
    model = Gear    