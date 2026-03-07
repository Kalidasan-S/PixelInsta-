from django import template

register = template.Library()

@register.filter
def has_user_liked(post, user):
    """
    Returns True if the given user has liked the given post.
    Usage: {% if post|has_user_liked:request.user %}
    Requires prefetch_related('likes') for performance.
    """
    if not user.is_authenticated:
        return False
    # If standard prefetch_related('likes') was used
    # we can check post.likes.all() without hitting the DB
    return any(like.user_id == user.id for like in post.likes.all())
