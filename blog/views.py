from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator


# def post_list(request):
#   posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#  return render(request, 'blog/post_list.html', {'posts': posts})

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='347dd147-98c1-43d9-bcb1-2562f3bd937f',
        password='KaGeQxoWu1GH',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='cde34c09-9fcb-4fe3-89fc-8d401718754c',
        password='Sfc6tYQzuVNY')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        data = json.dumps(tone_analyzer.tone(text=post.text), indent=1)  # converting to string and storing in the data
        j = json.loads(data);
        post.info = j['document_tone']['tone_categories'][0]['tones']
        # post.info = json.dumps(post.info);
        post.angerScore = post.info[0]['score']
        post.disgustScore = post.info[1]['score']
        post.fearScore = post.info[2]['score']
        post.joyScore = post.info[3]['score']
        post.sadScore = post.info[4]['score']
        # print(post.info[0]['tone_name'])
        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        post.translatedText = json.dumps(translation, indent=2, ensure_ascii=False)
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})