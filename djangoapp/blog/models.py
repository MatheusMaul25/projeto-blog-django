from django.db import models
from utils._random import new_slugify
from utils.images import resize_images
from django.contrib.auth.models import User
from django_summernote.models import AbstractAttachment
from django.urls import reverse

class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    name = models.CharField(max_length=50)
    slug = models.SlugField(
        unique= True,
        null= True,
        blank= True,
        default= None,
        max_length= 50,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.name, 4)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    name = models.CharField(
        max_length=50,
        unique= True)
    description = models.CharField(
        max_length=150,
        blank= True,
        null= True)
    slug = models.SlugField(
        unique= True,
        null= True,
        blank= True,
        default= None,
        max_length= 50,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.name, 5)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Page(models.Model):
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    title = models.CharField(max_length=50)
    content = models.TextField(
        help_text= 'Use um modelo HTML'
    )
    slug = models.SlugField(
        null= True,
        blank= True,
        default= '',
        max_length= 50,
    )

    is_published = models.BooleanField(
        default= False,
        help_text= 'Marque essa opção para que seu conteudo\n' \
        ' seja postado publicamente'
    )
    def get_absolute_url(self):
        if not self.is_published:
            return reverse('blog:index')
        return reverse('blog:page', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.title, 5)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PostManager(models.Manager):
    def published_and_ordered(self):
        return self.filter(is_published= True).order_by('-pk')

class Post(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    objects = PostManager()

    title = models.CharField(max_length=50)
    content = models.TextField(
        help_text= 'Use um modelo HTML'
    )
    slug = models.SlugField(
        null= True,
        blank= True,
        default= '',
        max_length= 50,
    )
    excerpt = models.CharField(max_length=250)
    cover = models.ImageField(upload_to='posts/%Y/%m/', blank= True, default= '')
    cover_in_post_content = models.BooleanField(
        help_text= 'Exibe a capa dentro do conteúdo do post',
        default= True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete= models.SET_NULL,
        blank= True,
        null= True,
        related_name= 'post_created_by',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete= models.SET_NULL,
        blank= True,
        null= True,
        related_name= 'post_updated_by',
    )
    category = models.ForeignKey(
        Category,
        on_delete= models.SET_NULL,
        null= True,
        blank= True,
        default= None,
        )
    tags = models.ManyToManyField(Tag, blank= True, default= '')
    is_published = models.BooleanField(
    default= False,
    help_text= 'Marque essa opção para que seu conteudo\n' \
    ' seja postado publicamente'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if not self.is_published:
            return reverse('blog:index')
        return reverse('blog:post', args=(self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.title, 5)

        current_cover_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        changed_cover = False

        if self.cover:
            changed_cover = current_cover_name != self.cover.name

        if changed_cover:
            resize_images(self.cover, 900, 70)
        
        return super_save

class PostAttachment(AbstractAttachment):

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name

        current_file_name = str(self.file.name)
        super_save = super().save(*args, **kwargs)
        changed_file = False

        if self.file:
            changed_file = current_file_name != self.file.name

        if changed_file:
            resize_images(self.file, 900, 70)