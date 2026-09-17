from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .services import merge_anon_votes_into_user
from .voter import read_anon_id


@receiver(user_logged_in)
def merge_votes_on_login(sender, request, user, **kwargs):
    """Her giriş yolunda (form, kayıt, Google) tetiklenir.

    request.user bu noktada zaten oturum açmış kullanıcıya işaret ettiği için
    anon_id'yi get_voter() yerine doğrudan çerezden okuruz.
    """
    anon_id = read_anon_id(request)
    if anon_id is not None:
        merge_anon_votes_into_user(anon_id, user)
