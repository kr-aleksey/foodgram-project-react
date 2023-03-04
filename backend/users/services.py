from users.models import Subscription


def delete_subscription(user, author):
    return (Subscription
            .objects
            .get(user=user, author=author)
            .delete())
