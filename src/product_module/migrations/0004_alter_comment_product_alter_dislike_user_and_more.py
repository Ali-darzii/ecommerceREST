# Generated by Django 5.1.1 on 2024-10-20 14:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_module', '0003_alter_comment_parent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_comment', to='product_module.product'),
        ),
        migrations.AlterField(
            model_name='dislike',
            name='user',
            field=models.ManyToManyField(null=True, related_name='user_dislikes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ManyToManyField(null=True, related_name='user_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productgallery',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_gallery', to='product_module.product'),
        ),
    ]
