from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from django.db.models import Q
from .models import UserAccount, Profile, Post, Story, Like, Comment, Follow, Message, Notification


@login_required
def home_view(request):
    
    following_ids = request.user.following.values_list("following_id", flat=True)
    posts = (
        Post.objects.filter(user_id__in=list(following_ids) + [request.user.id])
        .select_related("user")
        .prefetch_related("likes", "comments__user")
        .order_by("-created_at")
    )

    
    latest_stories = {}
    for story in Story.objects.select_related("user").order_by("-created_at"):
        if story.user_id not in latest_stories:
            latest_stories[story.user_id] = story

    return render(
        request,
        "login/home.html",
        {"posts": posts, "stories": list(latest_stories.values())},
    )


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            contact = request.POST.get("contact", "")
            full_name = request.POST.get("full_name", "")
            UserAccount.objects.create(
                contact=contact,
                full_name=full_name or user.get_full_name() or user.username,
                username=user.username,
                password=form.cleaned_data.get("password1"),
            )
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                auth_login(request, user)
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "login/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login/login.html", {"form": form})


from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

@login_required
def profile_view(request, username=None):
    if username and username != request.user.username:
        viewed_user = get_object_or_404(User, username=username)
        is_owner = False
    else:
        viewed_user = request.user
        is_owner = True

    profile, _ = Profile.objects.get_or_create(user=viewed_user)
    posts = (
        Post.objects.filter(user=viewed_user)
        .prefetch_related("likes", "comments__user")
        .order_by("-created_at")
    )
    
    # Calculate Follow counts
    followers_count = viewed_user.followers.count()
    following_count = viewed_user.following.count()
    
    is_following = False
    if not is_owner:
        is_following = request.user.following.filter(following=viewed_user).exists()

    if request.method == "POST":
        
        if "save_profile" in request.POST:
            profile.bio = request.POST.get("bio", "").strip()
            raw_website = request.POST.get("website", "").strip()
            profile.website = raw_website or None
            if request.FILES.get("avatar"):
                profile.avatar = request.FILES["avatar"]
            profile.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")

        # Add new post form
        if "add_post" in request.POST and request.FILES.get("post_image"):
            Post.objects.create(
                user=request.user,
                image=request.FILES["post_image"],
                caption=request.POST.get("post_caption", "").strip(),
            )
            messages.success(request, "Post added.")
            return redirect("profile")

        
        if "add_story" in request.POST and request.FILES.get("story_image") and is_owner:
            Story.objects.create(
                user=request.user,
                image=request.FILES["story_image"],
            )
            messages.success(request, "Story added.")
            return redirect("profile")

    return render(
        request, 
        "login/profile.html", 
        {
            "profile": profile, 
            "posts": posts,
            "is_owner": is_owner,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
        }
    )


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("login")


@login_required
def post_delete_view(request, post_id: int):
    if request.method != "POST":
        return redirect("profile")

    post = Post.objects.filter(id=post_id, user=request.user).first()
    if post is None:
        messages.error(request, "Post not found.")
        return redirect("profile")

    
    if post.image:
        post.image.delete(save=False)
    post.delete()

    messages.success(request, "Post deleted.")
    return redirect("profile")


@login_required
def like_post(request, post_id: int):
    if request.method != "POST":
        return redirect("home")

    post = Post.objects.filter(id=post_id).first()
    if not post:
        messages.error(request, "Post not found.")
        return redirect("home")

    
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    else:
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='like',
                post=post
            )

    
    next_url = request.POST.get("next", "")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("home")


@login_required
def add_comment(request, post_id: int):
    if request.method != "POST":
        return redirect("home")

    post = Post.objects.filter(id=post_id).first()
    if not post:
        messages.error(request, "Post not found.")
        return redirect("home")

    text = request.POST.get("text", "").strip()
    if text:
        Comment.objects.create(user=request.user, post=post, text=text)
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='comment',
                post=post
            )

    next_url = request.POST.get("next", "")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("home")


@login_required
def follow_user(request, username: str):
    if request.method != "POST":
        return redirect("profile_dynamic", username=username)
        
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect("profile")

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user, 
        following=target_user
    )
    
    if not created:
        follow_obj.delete() # Unfollow
    else:
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )
        
    next_url = request.POST.get("next", "")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("profile_dynamic", username=username)


@login_required
def search_users(request):
    query = request.GET.get("q", "").strip()
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    return render(request, "login/search.html", {"users": users, "query": query})


@login_required
def inbox(request):
    sent_msgs = Message.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    received_msgs = Message.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    user_ids = set(sent_msgs).union(set(received_msgs))
    conversations = User.objects.filter(id__in=user_ids)
    
    return render(request, "login/inbox.html", {"conversations": conversations})


@login_required
def chat(request, username: str):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect("inbox")
        
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=target_user,
                content=content
            )
            Notification.objects.create(
                recipient=target_user,
                sender=request.user,
                notification_type='message'
            )
            return redirect("chat", username=username)
            
   
    Message.objects.filter(sender=target_user, recipient=request.user, is_read=False).update(is_read=True)
    
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=target_user) | 
        Q(sender=target_user, recipient=request.user)
    ).order_by("created_at")
    
    return render(request, "login/chat.html", {"target_user": target_user, "chat_messages": messages})


@login_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('sender', 'post').order_by('-created_at')
    # Mark as read
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, "login/notifications.html", {"notifications": notifs})
