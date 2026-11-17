from django.core.paginator import Paginator
from django.shortcuts import render
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import ListView, DetailView

class PostListView(ListView):
    # model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    # ordering = '-pk'
    paginate_by = 9
    # queryset = Post.objects.published_and_ordered()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'home'
        })
        return context

    def get_queryset(self):
        queryset = Post.objects.published_and_ordered()
        return queryset
        
        

# def index(request):

'''
---->  View index - function based view <----

'''
#     posts = Post.objects.published_and_ordered()
#     paginator = Paginator(posts, 9)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#         'blog/pages/index.html',
#         {
#             'page_obj': page_obj,
#             'page_title': 'home',
#         }
#     )

class CreatedByListView(PostListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._temp_context = {}

    def get_context_data(self, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404

        user_full_name = user.username
        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = f'Posts de {user_full_name}'
        context = super().get_context_data(**kwargs)
        context.update(
            {'page_title': page_title},
        )
        return context

    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by__pk= self._temp_context['user'].pk)
        return queryset
    
    def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404

        self._temp_context.update({
            'author_pk': author_pk,
            'user': user,
        })       
        return super().get(request, *args, **kwargs)

# def created_by(request, author_pk):
#     posts = Post.objects.published_and_ordered().filter(created_by__pk = author_pk)
#     user = User.objects.filter(pk=author_pk).first()

#     if user is None:
#         raise Http404
    
#     paginator = Paginator(posts, 9)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)    
#     user_full_name = user.username
#     if user.first_name:
#         user_full_name = f'{user.first_name} {user.last_name}'
#     title = f'Posts de {user_full_name}'
#     return render(
#         request,
#         'blog/pages/index.html',
#         {
#             'page_obj': page_obj,
#             'page_title': title,
#         }
#     )

class CategoryListView(PostListView):
    allow_empty = False
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_title = f'{self.object_list[0].category.name} - categoria'
        context.update({'page_title': page_title})
        return context

    def get_queryset(self): 
        '''Retorna a lista de objetos que a view vai utilizar   '''
        return super().get_queryset().filter(
            category__slug = self.kwargs.get('slug')
        )
    
    
# def category(request, slug):
#     posts = Post.objects.published_and_ordered().filter(category__slug = slug)
    
#     paginator = Paginator(posts, 9)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     if len(page_obj) == 0:
#         raise Http404

#     page_title = f'Categoria - {page_obj[0].category.name}'

#     return render(
#         request,
#         'blog/pages/index.html',
#         {
#             'page_obj': page_obj,
#             'page_title': page_title,
#         }
#     )
class TagListView(PostListView):
    allow_empty = False
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object_list)
        slug = self.kwargs.get('slug')
        page_title = self.object_list[0].tags.filter(slug=slug).first().name
        context.update({'page_title': page_title})
        return context

    def get_queryset(self): 
        '''Retorna a lista de objetos que a view vai utilizar   '''
        return super().get_queryset().filter(
            tags__slug = self.kwargs.get('slug')
        )
    
# def tag(request, slug):
#     posts = Post.objects.published_and_ordered().filter(tags__slug = slug)
#     paginator = Paginator(posts, 9)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#         'blog/pages/index.html',
#         {
#             'page_obj': page_obj,
#             'title': 'tag',
#         }
#     )
class SearchListView(PostListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._search_value = ''

    def setup(self, request, *args, **kwargs):
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        search_value = self._search_value
        return super().get_queryset().filter(
    Q(title__icontains = search_value) | 
    Q(excerpt__icontains = search_value) |
    Q(content__icontains = search_value) |
    Q(tags__name__icontains = search_value) |
    Q(category__name__icontains = search_value)
)[0:9]           

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_value = self._search_value
        ctx.update(
        {'page_title': f'{self._search_value}',
        'search_value': search_value,}
        )
        return ctx
    
# def search(request):
#     search_value = request.GET.get('search', '').strip()
#     posts = (Post.objects.published_and_ordered().filter(
#     Q(title__icontains = search_value) | 
#     Q(excerpt__icontains = search_value) |
#     Q(content__icontains = search_value) |
#     Q(tags__name__icontains = search_value) |
#     Q(category__name__icontains = search_value)
# ))[0:9]

#     return render(
#         request,
#         'blog/pages/index.html',
#         {
#             'page_obj': posts,
#             'search_value': search_value,
#         }
#     )
class PageDetailView(DetailView):
    model = Page
    template_name = 'blog/pages/page.html'
    slug_field = 'slug'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        ctx =  super().get_context_data(**kwargs)
        page_title = self.get_object().title
        ctx.update({'page_title': page_title})
        return ctx

    def get_queryset(self):
        return super().get_queryset().filter(is_published= True)

# def page(request, slug):
#     page = Page.objects.filter(is_published=True).filter(slug=slug).first()
#     return render(
#         request,
#         'blog/pages/page.html',
#         {
#             'page': page,
#             'title': 'page',
#         }
#     )
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/pages/post.html'
    slug_field = 'slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.get_object()
        page_title = post.title
        ctx.update({'page_title': page_title})
        return ctx
    
# def post(request, slug):
#     post = Post.objects.published_and_ordered().filter(slug=slug).first()

#     if post is None:
#         raise Http404

#     page_title = f'{post.title} - Post'

#     return render(
#         request,
#         'blog/pages/post.html',
#         {
#             'post': post,
#             'page_title': page_title,
#         },
#     )
