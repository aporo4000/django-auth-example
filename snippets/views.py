from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from snippets.forms import SnippetForm, CommentForm
from snippets.models import Snippet, Comment


def top(request):
    context = {
        "snippets": Snippet.objects.all(),
        "num_snippets": Snippet.objects.all().count(),
        "num_users": get_user_model().objects.all().count(),
    }
    return render(request, "top.html", context)


@login_required
def new_snippet(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            snippet.save()
            return redirect(top)
    else:
        form = SnippetForm()
    return render(request, "snippets/snippet_new.html", {'form': form})


@login_required
def edit_snippet(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)

    if request.method == "POST":
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "スニペットを更新しました。")
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/snippet_edit.html', {'form': form})


@login_required
@require_GET
def snippet_detail(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    comments = Comment.objects.filter(commented_to=snippet_id).all()
    comment_form = CommentForm()

    return render(request, "snippets/snippet_detail.html", {
        'snippet': snippet,
        'comments': comments,
        'form': comment_form,
    })


@login_required
@require_POST
def new_comment(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.commented_to = snippet
        comment.commented_by = request.user
        comment.save()
        messages.add_message(request, messages.SUCCESS, "コメントを投稿しました")
    else:
        messages.add_message(request, messages.ERROR, "コメントの投稿に失敗しました")
    return redirect('snippet_detail', snippet_id=snippet_id)
