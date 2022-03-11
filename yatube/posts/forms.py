from django import forms
from .models import Follow, Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_post(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Напишите пост!')
        return data


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ('user', 'author',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )

    def clean_post(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Напишите пост!')
        return data
